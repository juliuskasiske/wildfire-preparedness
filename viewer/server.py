"""Local 3D property viewer. Address -> terrain + buildings + trees.

  .venv/bin/python viewer/server.py     ->  http://127.0.0.1:8000

Layers:
  terrain    3DEP 1 m DEM, fetched live per address (~0.6 MB, ~1.5 s)
  buildings  Overture polygons from the local GeoPackage, extruded to `height`
  trees      3DEP lidar height-above-ground, but ONLY for addresses covered by a
             tile already downloaded into data/lidar/ (tiles are ~90-200 MB each)
"""
import json, math, os, subprocess, sys, glob
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sources"))
import warnings; warnings.filterwarnings("ignore")
from flask import Flask, jsonify, request, send_from_directory

from geocode2 import resolve, suggest
from lookup import fhsz, firewise_site
from dem import fetch_dem, utm_epsg, _g
import firewind
from terrainwind import terrain_wind, summarize as terrain_wind_summary

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INDEX = os.path.join(ROOT, "data", "index")
OGRINFO = _g("ogrinfo")
app = Flask(__name__, static_folder=None)

_DEM_CACHE = {}

# ---------------------------------------------------------------- terrain
def hillshade_png(tif):
    """Render a hillshade and return its filename.

    Why this exists: at true scale a flat suburb is featureless (Long Beach has 2.0 m
    of relief over 300 m, i.e. 0.7% of the plane width, stddev 0.38 m). Hillshade
    shades by local GRADIENT rather than height, so a 20 cm curb still reads as a hard
    edge. Draping it on the mesh keeps geometry honest while making detail visible.
    """
    hs = tif[:-4] + "_hs.tif"
    png = tif[:-4] + "_hs.png"
    if not os.path.exists(png):
        subprocess.run([_g("gdaldem"), "hillshade", tif, hs, "-of", "GTiff",
                        "-z", "2", "-az", "315", "-alt", "45", "-compute_edges"],
                       check=True, capture_output=True)
        subprocess.run([_g("gdal_translate"), "-of", "PNG", "-ot", "Byte", "-scale", hs, png],
                       check=True, capture_output=True)
    return os.path.basename(png)

def terrain_grid(lat, lon, radius_m=150, target=140):
    """DEM -> a square grid of heights, downsampled to `target` per side."""
    tif, meta = fetch_dem(lat, lon, radius_m, 1.0,
                          out=os.path.join(ROOT, "data", "dem", f"v_{lat:.5f}_{lon:.5f}.tif"))
    asc = tif[:-4] + ".asc"
    subprocess.run([_g("gdal_translate"), "-of", "AAIGrid", "-outsize", str(target), str(target),
                    tif, asc], check=True, capture_output=True)
    vals, ncols, nodata = [], None, -9999.0
    with open(asc) as f:
        for line in f:
            p = line.split()
            if not p: continue
            if p[0].lower() == "ncols": ncols = int(p[1]); continue
            if p[0].lower() == "nodata_value": nodata = float(p[1]); continue
            if p[0][0].isalpha(): continue
            vals.extend(float(v) for v in p)
    n = int(math.isqrt(len(vals)))
    grid = [vals[i*n:(i+1)*n] for i in range(n)]
    good = [v for v in vals if v != nodata]
    try: shade = hillshade_png(tif)
    except Exception: shade = None
    _DEM_CACHE["grid"] = (grid, n, 2 * radius_m / max(n - 1, 1))
    return {"n": n, "size_m": 2 * radius_m, "heights": grid,
            "min": min(good) if good else 0, "max": max(good) if good else 0,
            "epsg": meta["epsg"], "hillshade": shade}

# ---------------------------------------------------------------- buildings
def buildings(lat, lon, radius_m=150):
    gp = os.path.join(INDEX, "overture_buildings_ca.gpkg")
    if not os.path.exists(gp): return []
    d = radius_m / 111320.0
    dl = d / max(math.cos(math.radians(lat)), 1e-6)
    out = subprocess.run([OGRINFO, "-ro", "-json", "-features", "-spat",
        str(lon-dl), str(lat-d), str(lon+dl), str(lat+d), gp, "overture_buildings_ca"],
        capture_output=True, text=True, timeout=180)
    if out.returncode != 0: return []
    feats = (json.loads(out.stdout).get("layers", [{}])[0] or {}).get("features", []) or []
    kx = 111320.0 * math.cos(math.radians(lat)); ky = 111320.0
    res = []
    for f in feats:
        g = f.get("geometry") or {}
        rings = g.get("coordinates") or []
        if g.get("type") == "MultiPolygon": rings = rings[0] if rings else []
        if not rings: continue
        ring = [[(p[0]-lon)*kx, (p[1]-lat)*ky] for p in rings[0]]
        p = f.get("properties", {})
        h = p.get("height")
        res.append({"ring": ring,
                    "height": float(h) if isinstance(h, (int, float)) else None,
                    "cls": p.get("class"), "src": p.get("src_dataset"),
                    "updated": (p.get("src_updated") or "")[:10]})
    return res

# ---------------------------------------------------------------- trees
_LAS_CACHE = {}
def trees(lat, lon, radius_m=150, cell=2.5, min_h=2.0):
    """Height-above-ground from any locally cached lidar tile covering this point.
    Returns one 'tree' per `cell` metre bin: position + height."""
    import numpy as np, pyproj, laspy
    tiles = glob.glob(os.path.join(ROOT, "data", "lidar", "*.laz"))
    if not tiles: return {"available": False, "reason": "no lidar tiles cached locally"}
    for path in sorted(tiles, key=os.path.getsize, reverse=True):
        # Read the HEADER only to test coverage. Reading an 88 MB point cloud just to
        # discover it does not cover the address costs seconds per tile.
        with laspy.open(path) as fh:
            h0 = fh.header
            crs0 = h0.parse_crs()
            if crs0 is None: continue
            tr = pyproj.Transformer.from_crs("EPSG:4326", crs0, always_xy=True)
            E, N = tr.transform(lon, lat)
            if not (h0.mins[0] < E < h0.maxs[0] and h0.mins[1] < N < h0.maxs[1]):
                continue
        las = _LAS_CACHE.get(path) or laspy.read(path)
        _LAS_CACHE[path] = las
        h = las.header
        crs = crs0
        k = 1.0
        name = (crs.to_string() + " " + (crs.name or "")).lower()
        if "ftus" in name or "survey foot" in name: k = 0.3048006096012192
        R = radius_m / k
        x, y, z, c = (np.asarray(las.x), np.asarray(las.y),
                      np.asarray(las.z), np.asarray(las.classification))
        m = (np.abs(x-E) <= R) & (np.abs(y-N) <= R)
        x, y, z, c = x[m], y[m], z[m], c[m]
        if len(x) < 100: continue
        C = cell / k
        gi = (c == 2)
        if gi.sum() < 50: return {"available": False, "reason": "tile has too few ground points"}
        gx = np.floor((x[gi]-E)/C).astype(int); gy = np.floor((y[gi]-N)/C).astype(int)
        key = gx*100000 + gy
        o = np.argsort(key); ks, zs = key[o], z[gi][o]
        u, first = np.unique(ks, return_index=True)
        lut = dict(zip(u.tolist(), np.minimum.reduceat(zs, first).tolist()))
        ax = np.floor((x-E)/C).astype(np.int64)*100000 + np.floor((y-N)/C).astype(int)
        base = np.array([lut.get(int(kk), np.nan) for kk in ax])
        hag = (z - base) * k
        sel = np.isfinite(hag) & (hag > min_h) & (hag < 45) & (c != 2)
        if sel.sum() == 0: return {"available": True, "trees": [], "tile": os.path.basename(path)}
        bx = np.floor((x[sel]-E)/C).astype(np.int64); by = np.floor((y[sel]-N)/C).astype(np.int64)
        bkey = bx*100000 + by
        o2 = np.argsort(bkey); bk, bh = bkey[o2], hag[sel][o2]
        bxs, bys = bx[o2], by[o2]
        uu, ff = np.unique(bk, return_index=True)
        hmax = np.maximum.reduceat(bh, ff)
        ex = bxs[ff]; ey = bys[ff]
        out = [{"x": float((ix + .5) * cell), "y": float((iy + .5) * cell), "h": round(float(hh), 1)}
               for ix, iy, hh in zip(ex, ey, hmax) if hh >= min_h]
        return {"available": True, "trees": out, "tile": os.path.basename(path),
                "points_used": int(sel.sum()), "cell_m": cell}
    return {"available": False, "reason": "no cached tile covers this address"}

def _subject_ring(blds):
    """The footprint containing the address point (the scene origin)."""
    for b in blds or []:
        r = b.get("ring") or []
        if len(r) < 3: continue
        c = 0
        for i in range(len(r)):
            x1, y1 = r[i]; x2, y2 = r[(i + 1) % len(r)]
            if (y1 > 0) != (y2 > 0):
                if x1 + (0 - y1) * (x2 - x1) / (y2 - y1) > 0: c += 1
        if c % 2: return r
    return None

# ---------------------------------------------------------------- wind
def wind_layer(lat, lon, radius_m, arrows=11, subject_ring=None):
    """Fire-weather wind for this cell, plus a terrain-adjusted vector field.

    The gridMET part is regional (4 km cells). The terrain part is local and is an
    APPROXIMATION computed from the DEM, not a WindNinja solve - no mass conservation,
    no lee-side recirculation, no true canyon channelling.
    """
    st = firewind.stats(lat, lon) if firewind.available() else \
         {"available": False, "reason": "gridMET climatology not built yet"}
    out = {"stats": st, "field": [], "terrain_model": "dem_approximation"}
    if not st.get("available"):
        return out
    wd = st["headline_from_deg"]   # modal sector; vector mean is unreliable when scattered
    g = _DEM_CACHE.get("grid")
    if not g: return out
    grid, n, px = g
    dem = np.array(grid, dtype=np.float32)
    dem[dem <= -9000] = np.nanmedian(dem[dem > -9000]) if (dem > -9000).any() else 0.0
    try:
        mult, local_from, sx = terrain_wind(dem, px, wd)
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"; return out
    step = max(1, n // arrows)
    S = 2 * radius_m
    for i in range(step // 2, n, step):
        for j in range(step // 2, n, step):
            out["field"].append({
                "x": round((j / (n - 1)) * S - S / 2, 1),        # east metres
                "y": round(S / 2 - (i / (n - 1)) * S, 1),        # north metres
                "from": round(float(local_from[i, j]), 1),
                "m": round(float(mult[i, j]), 2)})
    out["summary"] = terrain_wind_summary(dem, px, wd)
    out["regional_from_deg"] = wd

    # Per-WALL exposure on the real footprint. A single compass sector reads weak
    # ("26%") and invites "so what about the other 74%?". A wall's complement is
    # simply the opposite wall, and the two sum to 100%.
    if subject_ring and len(subject_ring) >= 3:
        try:
            walls = firewind.walls_from_footprint(subject_ring, st["sector_counts"])
            out["walls"] = walls
            out["windward"] = firewind.corner_or_wall(walls)
        except Exception as e:
            out["walls_error"] = f"{type(e).__name__}: {e}"
    return out

# ---------------------------------------------------------------- api
@app.route("/api/property")
def api_property():
    addr = request.args.get("address", "").strip()
    radius = int(request.args.get("radius", 150))
    if not addr: return jsonify({"error": "address required"}), 400
    g = resolve(addr)
    if not g.get("matched"):
        try:
            from addrpoint import nearest_numbers
            near = nearest_numbers(addr)
        except Exception:
            near = []
        if near:
            return jsonify({"error": "that house number does not exist on that street",
                            "did_you_mean": [n["label"] for n in near]}), 404
        return jsonify({"error": f"could not resolve address. {g.get('error','no match')}",
                        "hint": g.get("hint")}), 404
    lat, lon = g["lat"], g["lon"]
    payload = {"address": g["matched_address"], "lat": lat, "lon": lon,
               "place": g.get("place"), "county": g.get("county"),
               "geocoder": g.get("provider"), "precision": g.get("precision")}
    # If we fell back to a geocoder, check whether the county actually has that house
    # number. Interpolators invent a position for numbers that do not exist, and the
    # user has no way to tell. Surface it rather than rendering a confident wrong house.
    if g.get("provider") != "county_address_point":
        try:
            from addrpoint import nearest_numbers, available
            if available():
                near = nearest_numbers(addr)
                if near:
                    payload["warning"] = ("this house number is not in county records, "
                                          "so the position is interpolated and may be the wrong property")
                    payload["did_you_mean"] = [n["label"] for n in near]
        except Exception:
            pass
    try: payload["hazard"] = fhsz(lat, lon)
    except Exception as e: payload["hazard"] = {"error": str(e)}
    try:
        fw = firewise_site(lat, lon, 4000)
        payload["firewise"] = {"count": len(fw), "nearest": fw[0] if fw else None}
    except Exception as e: payload["firewise"] = {"error": str(e)}
    payload["terrain"] = terrain_grid(lat, lon, radius)
    payload["buildings"] = buildings(lat, lon, radius)
    payload["wind"] = wind_layer(lat, lon, radius,
                                 subject_ring=_subject_ring(payload["buildings"]))
    try: payload["vegetation"] = trees(lat, lon, radius)
    except Exception as e: payload["vegetation"] = {"available": False, "reason": str(e)}
    return jsonify(payload)

@app.route("/dem/<path:fn>")
def dem_file(fn):
    return send_from_directory(os.path.join(ROOT, "data", "dem"), fn)

@app.route("/api/suggest")
def api_suggest():
    return jsonify(suggest(request.args.get("q", ""), limit=6))

@app.route("/")
def index(): return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

if __name__ == "__main__":
    print("  http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)
