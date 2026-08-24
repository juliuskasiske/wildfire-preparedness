"""USGS 3DEP terrain, on demand. Free, no key. Too large to download statewide (TB scale),
so this fetches a small DEM chip per property and derives slope/aspect locally."""
import io, math, requests, urllib3
import numpy as np
urllib3.disable_warnings()
IMG = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer"
TNM = "https://tnmaccess.nationalmap.gov/api/v1/products"

def elevation(lat, lon, timeout=45):
    r = requests.get(f"{IMG}/identify", timeout=timeout, verify=False, params={
        "geometry": f'{{"x":{lon},"y":{lat},"spatialReference":{{"wkid":4326}}}}',
        "geometryType": "esriGeometryPoint", "returnGeometry": "false", "f": "json"})
    v = r.json().get("value")
    return None if v in (None, "NoData") else float(v)

def dem_chip(lat, lon, radius_m=120, px=1.0, timeout=90):
    """Return (elevation array, metres-per-pixel). Chip is 2*radius_m across."""
    d = radius_m / 111320.0
    size = int(2 * radius_m / px)
    r = requests.get(f"{IMG}/exportImage", timeout=timeout, verify=False, params={
        "bbox": f"{lon-d/math.cos(math.radians(lat))},{lat-d},{lon+d/math.cos(math.radians(lat))},{lat+d}",
        "bboxSR": 4326, "imageSR": 4326, "size": f"{size},{size}",
        "format": "tiff", "pixelType": "F32", "f": "image"})
    r.raise_for_status()
    return r.content, px  # GeoTIFF bytes; decode with GDAL/rasterio downstream

def slope_aspect(lat, lon, radius_m=60):
    """Slope percent and aspect degrees from a 3x3 neighbourhood of point elevations.
    Uses 8 identify calls rather than a raster read, so it needs no GDAL. ~9 requests."""
    step = radius_m
    dlat = step / 111320.0
    dlon = step / (111320.0 * math.cos(math.radians(lat)))
    z = {}
    for i, di in enumerate((-1, 0, 1)):
        for j, dj in enumerate((-1, 0, 1)):
            z[(i, j)] = elevation(lat + di * dlat, lon + dj * dlon)
    if any(v is None for v in z.values()):
        return {"slope_pct": None, "aspect_deg": None, "elevation_m": z.get((1, 1))}
    dzdx = ((z[(0,2)] + 2*z[(1,2)] + z[(2,2)]) - (z[(0,0)] + 2*z[(1,0)] + z[(2,0)])) / (8 * step)
    dzdy = ((z[(2,0)] + 2*z[(2,1)] + z[(2,2)]) - (z[(0,0)] + 2*z[(0,1)] + z[(0,2)])) / (8 * step)
    slope = math.degrees(math.atan(math.hypot(dzdx, dzdy)))
    aspect = (450 - math.degrees(math.atan2(dzdy, -dzdx))) % 360
    return {"slope_pct": round(math.tan(math.radians(slope)) * 100, 1),
            "slope_deg": round(slope, 1), "aspect_deg": round(aspect, 1),
            "elevation_m": round(z[(1,1)], 1)}

def lidar_tiles(lat, lon, pad_deg=0.004, timeout=60):
    """Discover 3DEP lidar point-cloud tiles covering a property. Feeds canopy height,
    building height and possibly eave depth. Tiles are ~10-20 MB each."""
    r = requests.get(TNM, timeout=timeout, verify=False, params={
        "datasets": "Lidar Point Cloud (LPC)",
        "bbox": f"{lon-pad_deg},{lat-pad_deg},{lon+pad_deg},{lat+pad_deg}", "max": 50})
    j = r.json()
    return [{"title": i.get("title"), "url": i.get("downloadURL"),
             "mb": round((i.get("sizeInBytes") or 0)/1e6, 1),
             "year": i.get("publicationDate", "")[:4]} for i in j.get("items", [])]
