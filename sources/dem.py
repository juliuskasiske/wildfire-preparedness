"""1 m DEM for a property and its surroundings, plus hillshade.

Why this replaces the old 9-point sampler: the 3DEP ImageServer will export a whole
raster in ONE request. Covering a 300 m box at 1 m used to imply 90,000 point calls;
exportImage returns the same grid in a single ~350 KB GeoTIFF. The parallel point
sampler is kept only as a fallback for when exportImage is unavailable.

The DEM is requested in UTM so pixels are true metres. Asking in EPSG:4326 gives
pixels that are ~0.8x as tall as wide at California latitudes, which silently biases
slope and aspect.
"""
import math, os, subprocess, requests, urllib3
from concurrent.futures import ThreadPoolExecutor
urllib3.disable_warnings()

IMG = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer"
GDAL = next((p for p in ["/Applications/Postgres.app/Contents/Versions/latest/bin",
                         "/opt/homebrew/bin", "/usr/local/bin"]
             if os.path.exists(os.path.join(p, "gdaldem"))), "")
def _g(t): return os.path.join(GDAL, t) if GDAL else t

def utm_epsg(lat, lon):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) / 6) + 1

def fetch_dem(lat, lon, radius_m=150, px_m=1.0, out=None, timeout=120):
    """One request. radius_m=150 -> a 300x300 m box: the parcel plus a good margin of
    neighbouring ground, which is what slope-above-the-house actually depends on."""
    epsg = utm_epsg(lat, lon)
    dlat = radius_m / 111320.0
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    size = int(2 * radius_m / px_m)
    r = requests.get(f"{IMG}/exportImage", timeout=timeout, verify=False, params={
        "bbox": f"{lon-dlon},{lat-dlat},{lon+dlon},{lat+dlat}",
        "bboxSR": 4326, "imageSR": epsg, "size": f"{size},{size}",
        "format": "tiff", "pixelType": "F32", "interpolation": "RSP_BilinearInterpolation",
        "noDataInterpretation": "esriNoDataMatchAny", "f": "image"})
    r.raise_for_status()
    if not r.content.startswith(b"II") and not r.content.startswith(b"MM"):
        raise RuntimeError(f"not a GeoTIFF: {r.content[:120]!r}")
    out = out or f"data/dem/dem_{lat:.5f}_{lon:.5f}.tif"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(r.content)
    return out, {"epsg": epsg, "px_m": px_m, "size_px": size,
                 "covers_m": 2 * radius_m, "bytes": len(r.content)}

def _derive(src, kind, out, extra=()):
    subprocess.run([_g("gdaldem"), kind, src, out, "-of", "GTiff", *extra],
                   check=True, capture_output=True)
    return out

def terrain(lat, lon, radius_m=150, px_m=1.0, outdir="data/dem"):
    """DEM -> slope, aspect, hillshade. Returns stats plus paths."""
    tif, meta = fetch_dem(lat, lon, radius_m, px_m, out=f"{outdir}/dem_{lat:.5f}_{lon:.5f}.tif")
    base = tif[:-4]
    slope = _derive(tif, "slope",  base + "_slope.tif",  ["-p"])          # percent
    aspect = _derive(tif, "aspect", base + "_aspect.tif")
    hs = _derive(tif, "hillshade", base + "_hillshade.tif", ["-z", "1.5", "-az", "315", "-alt", "45"])
    png = base + "_hillshade.png"
    subprocess.run([_g("gdal_translate"), "-of", "PNG", "-scale", hs, png],
                   check=True, capture_output=True)
    return {**meta, "dem": tif, "slope": slope, "aspect": aspect,
            "hillshade_tif": hs, "hillshade_png": png,
            "stats": {"elevation": _stats(tif), "slope_pct": _stats(slope), "aspect_deg": _stats(aspect)}}

def _stats(tif):
    out = subprocess.run([_g("gdalinfo"), "-stats", "-json", tif],
                         capture_output=True, text=True).stdout
    import json
    b = json.loads(out)["bands"][0]
    return {k: round(b[v], 1) for k, v in
            [("min", "minimum"), ("max", "maximum"), ("mean", "mean"), ("stddev", "stdDev")]
            if v in b}

# ---- fallback only: parallel point sampling ----
def _point(latlon):
    lat, lon = latlon
    r = requests.get(f"{IMG}/identify", timeout=45, verify=False, params={
        "geometry": f'{{"x":{lon},"y":{lat},"spatialReference":{{"wkid":4326}}}}',
        "geometryType": "esriGeometryPoint", "returnGeometry": "false", "f": "json"})
    v = r.json().get("value")
    return None if v in (None, "NoData") else float(v)

def sample_grid(lat, lon, radius_m=60, n=9, workers=16):
    """Parallel point sampler. n x n grid. Use only if exportImage is unavailable —
    at n=17 this is 289 HTTP requests to reproduce what one exportImage call returns."""
    dlat = radius_m / 111320.0; dlon = dlat / math.cos(math.radians(lat))
    pts = [(lat + (i/(n-1)*2-1)*dlat, lon + (j/(n-1)*2-1)*dlon)
           for i in range(n) for j in range(n)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_point, pts))

def robust_slope(slope_tif):
    """3DEP 1 m retains building pads and retaining walls, so max slope is an artifact.
    Palisades: median 5.1%, p90 60.4%, max 521.9% — the max is a wall edge, not terrain.
    Report percentiles, never the max."""
    import json, numpy as np
    out = subprocess.run([_g("gdalinfo"), "-json", "-hist", slope_tif],
                         capture_output=True, text=True).stdout
    b = json.loads(out)["bands"][0]; h = b.get("histogram", {})
    cnt = np.array(h.get("buckets", []), dtype=float)
    if cnt.sum() == 0: return {}
    edges = np.linspace(h["min"], h["max"], len(cnt) + 1)[:-1]
    cum = np.cumsum(cnt) / cnt.sum()
    q = lambda p: round(float(edges[np.searchsorted(cum, p)]), 1)
    return {"p50": q(.5), "p90": q(.9), "p95": q(.95),
            "max_artifact": round(b["maximum"], 1)}

MAX_PX = 4000   # 3DEP exportImage caps out around 4100 px per side

def fetch_dem_mosaic(lat, lon, radius_m=1000, px_m=1.0, outdir="data/dem", workers=8):
    """For areas bigger than one exportImage can return, split into a grid of chips,
    fetch them CONCURRENTLY, and mosaic with gdalbuildvrt. A 2 km box at 1 m is
    2000x2000 px (fine); a 8 km box is 8000 px and needs 4 chips."""
    import itertools
    side_px = int(2 * radius_m / px_m)
    n = max(1, math.ceil(side_px / MAX_PX))
    step_m = 2 * radius_m / n
    os.makedirs(outdir, exist_ok=True)
    jobs = []
    for i, j in itertools.product(range(n), repeat=2):
        clat = lat - radius_m/111320.0 + (i + 0.5) * step_m / 111320.0
        clon = lon - radius_m/(111320.0*math.cos(math.radians(lat))) \
               + (j + 0.5) * step_m / (111320.0*math.cos(math.radians(lat)))
        jobs.append((clat, clon, step_m/2, f"{outdir}/chip_{i}_{j}.tif"))
    def one(a):
        clat, clon, r, path = a
        return fetch_dem(clat, clon, r, px_m, out=path)[0]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        chips = list(ex.map(one, jobs))
    vrt = f"{outdir}/mosaic_{lat:.5f}_{lon:.5f}.vrt"
    subprocess.run([_g("gdalbuildvrt"), vrt, *chips], check=True, capture_output=True)
    return vrt, {"chips": len(chips), "grid": f"{n}x{n}", "px_per_side": side_px}

def terrain_batch(points, radius_m=150, px_m=1.0, workers=8):
    """Many properties at once. Each is one HTTP request, so N properties = N requests
    issued concurrently rather than serially."""
    def one(p):
        name, lat, lon = p
        try:
            r = terrain(lat, lon, radius_m, px_m)
            return {"name": name, "ok": True, "slope": robust_slope(r["slope"]),
                    "elev": r["stats"]["elevation"], "png": r["hillshade_png"]}
        except Exception as e:
            return {"name": name, "ok": False, "error": f"{type(e).__name__}: {e}"}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, points))
