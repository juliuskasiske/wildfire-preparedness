"""Point-in-polygon lookup against downloaded GeoPackages. Uses GDAL's spatial index
via ogrinfo, so no Python GDAL bindings are needed."""
import json, os, shutil, subprocess

GDAL_BIN = next((p for p in ["/Applications/Postgres.app/Contents/Versions/latest/bin",
                             "/opt/homebrew/bin", "/usr/local/bin"]
                 if os.path.exists(os.path.join(p, "ogrinfo"))), None)
OGRINFO = os.path.join(GDAL_BIN, "ogrinfo") if GDAL_BIN else shutil.which("ogrinfo")
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "index")

def point_query(gpkg, layer, lat, lon, eps=1e-6):
    """Return attributes of every polygon containing the point (usually 0 or 1)."""
    path = gpkg if os.path.exists(gpkg) else os.path.join(INDEX, gpkg)
    if not os.path.exists(path): raise FileNotFoundError(path)
    out = subprocess.run(
        [OGRINFO, "-ro", "-json", "-features", "-spat",
         str(lon-eps), str(lat-eps), str(lon+eps), str(lat+eps), path, layer],
        capture_output=True, text=True, timeout=120)
    if out.returncode != 0: raise RuntimeError(out.stderr[:400])
    d = json.loads(out.stdout)
    feats = (d.get("layers", [{}])[0] or {}).get("features", []) or []
    return [f.get("properties", {}) for f in feats]

def fhsz(lat, lon):
    """Combined SRA + LRA fire hazard severity zone, plus responsibility area."""
    res = {"fhsz": None, "fhsz_source": None, "responsibility_area": None, "ab38_fhsz": None}
    for key, layer, tag in [("calfire_fhsz_sra.gpkg", "fhsz_sra", "SRA"),
                            ("calfire_fhsz_lra.gpkg", "fhsz_lra", "LRA")]:
        if not os.path.exists(os.path.join(INDEX, key)): continue
        for p in point_query(key, layer, lat, lon):
            desc = (p.get("FHSZ_Description") or "").strip()
            if desc and desc.lower() != "nonwildland":
                res["fhsz"], res["fhsz_source"] = desc, tag
    for key, layer in [("calfire_responsibility_area.gpkg", "responsibility_area")]:
        if os.path.exists(os.path.join(INDEX, key)):
            for p in point_query(key, layer, lat, lon):
                res["responsibility_area"] = p.get("SRA")
    for key, layer in [("calfire_fhsz_realestate.gpkg", "fhsz_realestate")]:
        if os.path.exists(os.path.join(INDEX, key)):
            for p in point_query(key, layer, lat, lon):
                res["ab38_fhsz"] = (p.get("FHSZ_Description") or "").strip()
    return res

def firewise_site(lat, lon, radius_m=2000):
    """Nearest Firewise USA site in good standing. NFPA publishes site POINTS, not
    boundaries, so this can only say 'a site exists nearby' — it cannot prove the
    address is inside it. Treat as a lead, confirm with the homeowner."""
    import math
    d = radius_m / 111320.0
    dl = d / max(math.cos(math.radians(lat)), 1e-6)
    hits = []
    out = subprocess.run(
        [OGRINFO, "-ro", "-json", "-features", "-spat",
         str(lon-dl), str(lat-d), str(lon+dl), str(lat+d),
         os.path.join(INDEX, "firewise_sites.gpkg"), "firewise"],
        capture_output=True, text=True, timeout=120)
    if out.returncode != 0: return []
    feats = (json.loads(out.stdout).get("layers", [{}])[0] or {}).get("features", []) or []
    for f in feats:
        p = f.get("properties", {})
        try:
            plat, plon = float(p.get("Latitude")), float(p.get("Longitude"))
            km = 6371 * math.acos(min(1, math.sin(math.radians(lat))*math.sin(math.radians(plat))
                 + math.cos(math.radians(lat))*math.cos(math.radians(plat))*math.cos(math.radians(plon-lon))))
        except (TypeError, ValueError): km = None
        hits.append({"name": p.get("Name"), "county": p.get("County"), "state": p.get("State"),
                     "approval_year": p.get("ApprovalYear"), "residents": p.get("ResidentCount"),
                     "km": round(km, 2) if km is not None else None})
    return sorted(hits, key=lambda h: (h["km"] is None, h["km"]))

def nearest_structures(lat, lon, radius_m=120):
    """Neighbouring buildings from Overture (falls back to Microsoft if absent).

    Overture is the live source: monthly releases, and it carries height, num_floors,
    roof_shape, roof_material and facade_material, none of which Microsoft had.
    Microsoft's California extract is dated 2021-03-26 and therefore shows structures
    destroyed in the January 2025 fires as still standing.
    """
    import math
    for gpkg, layer, src in (("overture_buildings_ca.gpkg", None, "overture"),
                             ("ms_footprints_ca.gpkg", "footprints", "microsoft-2021")):
        path = os.path.join(INDEX, gpkg)
        if os.path.exists(path):
            break
    else:
        return None
    if layer is None:                       # discover the layer name duckdb wrote
        li = subprocess.run([OGRINFO, "-ro", path], capture_output=True, text=True, timeout=60)
        m = [l.split(":", 1)[1].split("(")[0].strip()
             for l in li.stdout.splitlines() if l[:1].isdigit() and ":" in l]
        layer = m[0] if m else "buildings"

    d = radius_m / 111320.0
    dl = d / max(math.cos(math.radians(lat)), 1e-6)
    out = subprocess.run(
        [OGRINFO, "-ro", "-json", "-features", "-spat",
         str(lon-dl), str(lat-d), str(lon+dl), str(lat+d), path, layer],
        capture_output=True, text=True, timeout=180)
    if out.returncode != 0:
        return {"source": src, "error": out.stderr[:200]}
    feats = (json.loads(out.stdout).get("layers", [{}])[0] or {}).get("features", []) or []
    props = [f.get("properties", {}) for f in feats]
    def pct(field):
        got = sum(1 for p in props if p.get(field) not in (None, ""))
        return round(100 * got / len(props), 1) if props else 0.0
    res = {"source": src, "layer": layer,
           "buildings_within_%dm" % radius_m: len(feats)}
    if src == "overture":
        res["attribute_coverage_pct"] = {f: pct(f) for f in
            ("height", "num_floors", "roof_shape", "roof_material", "facade_material")}
        hts = [p["height"] for p in props if isinstance(p.get("height"), (int, float))]
        if hts:
            res["height_m"] = {"n": len(hts), "max": round(max(hts), 1),
                               "median": round(sorted(hts)[len(hts)//2], 1)}
    return res
