"""What a 3DEP lidar tile actually gives you for one address.

A tile is a raw 3D point cloud: millions of laser returns, each with x, y, z and a
classification code (ground, vegetation, building, ...). On its own it says nothing
about a property. You extract per-address facts like this:

  1. clip to a box around the address
  2. build a ground surface from class-2 points
  3. subtract ground from every other point -> HEIGHT ABOVE GROUND
  4. read off canopy height, building height, and what overhangs what
"""
import numpy as np, laspy

CLS = {1: "unclassified", 2: "ground", 3: "low veg", 4: "med veg", 5: "high veg",
       6: "building", 7: "noise", 9: "water", 10: "rail", 11: "road"}

def read(path):
    return laspy.read(path)

def crs_units_to_m(las):
    """CRITICAL: many CA tiles are in State Plane US survey FEET, not metres.
    Every distance and height must be scaled or your 'canopy height' is 3.3x wrong."""
    crs = las.header.parse_crs()
    if crs is None: return 1.0, "unknown"
    name = crs.to_string().lower() + " " + (crs.name or "").lower()
    if "ftus" in name or "us survey foot" in name or "survey foot" in name:
        return 0.3048006096012192, "US survey foot"
    if "foot" in name or "ft" in name.split():
        return 0.3048, "international foot"
    return 1.0, "metre"

def clip(las, easting, northing, half_m=40):
    x, y = np.asarray(las.x), np.asarray(las.y)
    m = (np.abs(x - easting) <= half_m) & (np.abs(y - northing) <= half_m)
    return x[m], y[m], np.asarray(las.z)[m], np.asarray(las.classification)[m]

def normalise(x, y, z, cls, cell=2.0):
    """Height above ground. Ground surface = min class-2 elevation per `cell` metre bin."""
    g = cls == 2
    if g.sum() < 10: return None
    gx = np.floor(x[g] / cell).astype(int); gy = np.floor(y[g] / cell).astype(int)
    key = gx.astype(np.int64) * 100000 + gy
    order = np.argsort(key); key_s, z_s = key[order], z[g][order]
    uniq, first = np.unique(key_s, return_index=True)
    ground_z = np.minimum.reduceat(z_s, first)
    lut = dict(zip(uniq.tolist(), ground_z.tolist()))
    ax = np.floor(x / cell).astype(np.int64) * 100000 + np.floor(y / cell).astype(int)
    base = np.array([lut.get(int(k), np.nan) for k in ax])
    return z - base

def property_facts(path, easting, northing, half_m=40):
    las = read(path)
    k, unit = crs_units_to_m(las)          # tile units -> metres
    half_native = half_m / k               # clip window expressed in tile units
    x, y, z, cls = clip(las, easting, northing, half_native)
    if len(x) == 0: return {"error": "no points in clip window"}
    h = normalise(x, y, z, cls, cell=2.0 / k)
    veg = np.isin(cls, [3, 4, 5]); bld = cls == 6
    def rings(mask, r_m):
        d = np.hypot(x - easting, y - northing) * k      # metres
        sel = mask & (d <= r_m) & np.isfinite(h)
        return None if sel.sum() == 0 else round(float(np.nanmax(h[sel]) * k), 1)
    return {
        "crs_unit": unit, "unit_scale_to_m": k,
        "tile_points_total": int(las.header.point_count),
        "points_in_window": int(len(x)),
        "window_m": half_m * 2,
        "classes_present": {CLS.get(int(c), str(c)): int((cls == c).sum())
                            for c in np.unique(cls)},
        "ground_points": int((cls == 2).sum()),
        "usable": bool((cls == 2).sum() > 100 and (np.isin(cls, [3,4,5,6])).sum() > 0),
        "max_canopy_height_m": {
            "within_1.5m (Zone 0)": rings(veg, 1.5),
            "within_9m  (Zone 1)":  rings(veg, 9.0),
            "within_30m (Zone 2)":  rings(veg, 30.0)},
        "max_building_height_m": rings(bld, 30.0),
        "building_points": int(bld.sum()),
    }
