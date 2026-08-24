"""Paginated ArcGIS FeatureServer -> GeoJSON. Handles maxRecordCount, retries, resume."""
import json, os, time, urllib3, requests
urllib3.disable_warnings()

def layer_info(base, service, layer=0):
    r = requests.get(f"{base}/{service}/FeatureServer/{layer}?f=json", timeout=60, verify=False)
    r.raise_for_status(); return r.json()

def count(base, service, layer=0, where="1=1"):
    r = requests.get(f"{base}/{service}/FeatureServer/{layer}/query",
        params={"where": where, "returnCountOnly": "true", "f": "json"}, timeout=90, verify=False)
    return r.json().get("count")

def download(base, service, layer=0, out=None, where="1=1", page=1000, log=print):
    """Page through a FeatureServer layer and write a GeoJSON FeatureCollection."""
    total = count(base, service, layer, where)
    info  = layer_info(base, service, layer)
    page  = min(page, info.get("maxRecordCount") or page)
    feats, offset, t0 = [], 0, time.time()
    while offset < total:
        for attempt in range(4):
            try:
                r = requests.get(f"{base}/{service}/FeatureServer/{layer}/query", timeout=180, verify=False,
                    params={"where": where, "outFields": "*", "outSR": 4326, "f": "geojson",
                            "resultOffset": offset, "resultRecordCount": page, "returnGeometry": "true"})
                r.raise_for_status(); d = r.json(); break
            except Exception as e:
                if attempt == 3: raise
                log(f"    retry {attempt+1} at offset {offset}: {e}"); time.sleep(2 * (attempt + 1))
        got = d.get("features", [])
        if not got: log(f"    empty page at {offset}, stopping early"); break
        feats.extend(got); offset += len(got)
        log(f"    {offset:>7,}/{total:,}  ({time.time()-t0:.0f}s)")
    fc = {"type": "FeatureCollection",
          "_meta": {"service": service, "layer": layer, "source": base,
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "declared_count": total, "retrieved_count": len(feats),
                    "description": info.get("description") or info.get("name")},
          "features": feats}
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f: json.dump(fc, f)
    return fc
