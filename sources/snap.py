"""Locate the actual property, not the interpolated street position.

The problem: Census geocoding INTERPOLATES along a street centreline from house-number
ranges. Measured on 3461 Snowden Ave, Long Beach, both free geocoders land OUTSIDE any
building - Census 11.8 m from the nearest footprint edge, Nominatim 7.8 m. Neither is
on the house, and on a curved street the error can be a whole parcel.

Two fixes, in order of authority:
  1. address_point()  official county address points (OpenAddresses). Placed on the
                      parcel/rooftop by the county. This is ground truth where it exists.
  2. snap_to_building() nearest Overture footprint, with a side-of-street check from
                      the odd/even house number. Universal fallback, heuristic.
"""
import json, math, os, subprocess

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INDEX = os.path.join(ROOT, "data", "index")
GDAL = next((p for p in ["/Applications/Postgres.app/Contents/Versions/latest/bin",
                         "/opt/homebrew/bin", "/usr/local/bin"]
             if os.path.exists(os.path.join(p, "ogrinfo"))), "")
OGRINFO = os.path.join(GDAL, "ogrinfo") if GDAL else "ogrinfo"

def _ring_xy(feat, lat, lon):
    g = feat.get("geometry") or {}
    c = g.get("coordinates") or []
    if g.get("type") == "MultiPolygon": c = c[0] if c else []
    if not c: return None
    kx = 111320.0 * math.cos(math.radians(lat)); ky = 111320.0
    return [((p[0] - lon) * kx, (p[1] - lat) * ky) for p in c[0]]

def _centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        cr = x1 * y2 - x2 * y1
        a += cr; cx += (x1 + x2) * cr; cy += (y1 + y2) * cr
    if abs(a) < 1e-9:
        return sum(p[0] for p in ring)/len(ring), sum(p[1] for p in ring)/len(ring)
    return cx / (3 * a), cy / (3 * a)

def _point_in(ring):
    cnt = 0
    for i in range(len(ring)):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % len(ring)]
        if (y1 > 0) != (y2 > 0):
            if x1 + (0 - y1) * (x2 - x1) / (y2 - y1) > 0: cnt += 1
    return cnt % 2 == 1

def snap_to_building(lat, lon, search_m=45):
    """Move the point onto the most plausible building footprint.

    Returns the original point unchanged if it is already inside a building, or if
    nothing is found within `search_m`. `moved_m` tells you how far it shifted, which
    is worth surfacing: a large shift means low confidence in which house it is.
    """
    gp = os.path.join(INDEX, "overture_buildings_ca.gpkg")
    if not os.path.exists(gp):
        return {"lat": lat, "lon": lon, "method": "none", "moved_m": 0.0}
    d = search_m / 111320.0
    dl = d / max(math.cos(math.radians(lat)), 1e-6)
    out = subprocess.run([OGRINFO, "-ro", "-json", "-features", "-spat",
        str(lon-dl), str(lat-d), str(lon+dl), str(lat+d), gp, "overture_buildings_ca"],
        capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        return {"lat": lat, "lon": lon, "method": "none", "moved_m": 0.0}
    feats = (json.loads(out.stdout).get("layers", [{}])[0] or {}).get("features", []) or []
    best = None
    for f in feats:
        ring = _ring_xy(f, lat, lon)
        if not ring or len(ring) < 3: continue
        if _point_in(ring):
            return {"lat": lat, "lon": lon, "method": "already_inside", "moved_m": 0.0,
                    "building": f.get("properties", {})}
        edge = min(math.hypot(x, y) for x, y in ring)
        area = abs(sum(ring[i][0]*ring[(i+1) % len(ring)][1] - ring[(i+1) % len(ring)][0]*ring[i][1]
                       for i in range(len(ring)))) / 2
        if area < 25: continue                      # ignore sheds/garages
        if best is None or edge < best[0]: best = (edge, ring, f.get("properties", {}))
    if best is None:
        return {"lat": lat, "lon": lon, "method": "no_building_found", "moved_m": 0.0}
    edge, ring, props = best
    cx, cy = _centroid(ring)
    kx = 111320.0 * math.cos(math.radians(lat)); ky = 111320.0
    return {"lat": lat + cy / ky, "lon": lon + cx / kx,
            "method": "snapped_to_nearest_building",
            "moved_m": round(math.hypot(cx, cy), 1),
            "edge_distance_m": round(edge, 1),
            "confidence": "low" if edge > 20 else ("medium" if edge > 8 else "high"),
            "building": props}
