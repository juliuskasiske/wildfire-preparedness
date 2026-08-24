"""Address -> lat/lon + jurisdiction. US Census Geocoder: free, unlimited, no key.

Caveats: US-only; match rate on rural/new-construction addresses is meaningfully worse
than Google's. Fall back to a paid geocoder only on no-match, not by default.
"""
import requests, urllib3
urllib3.disable_warnings()
ONELINE = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"

def geocode(address, benchmark="Public_AR_Current", vintage="Current_Current",
            timeout=30, retries=4):
    """The Census service returns intermittent 502s under load. Retry with backoff;
    a single 502 must not abort a batch."""
    import time
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(ONELINE, timeout=timeout, verify=False, params={
                "address": address, "benchmark": benchmark, "vintage": vintage,
                "layers": "Counties,Incorporated Places,States", "format": "json"})
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"{r.status_code}")
            r.raise_for_status()
            break
        except Exception as e:
            last = e
            if attempt == retries - 1:
                return {"matched": False, "address": address, "error": f"{type(e).__name__}: {e}"}
            time.sleep(1.5 * (attempt + 1))
    m = r.json()["result"]["addressMatches"]
    if not m:
        return {"matched": False, "address": address}
    top = m[0]; g = top.get("geographies", {})
    def first(k, f="NAME"):
        v = g.get(k) or []
        return v[0].get(f) if v else None
    return {"matched": True, "input": address,
            "matched_address": top["matchedAddress"],
            "lon": top["coordinates"]["x"], "lat": top["coordinates"]["y"],
            "state": first("States"), "county": (first("Counties") or "").replace(" County","") or None,
            "place": first("Incorporated Places"),
            "county_fips": (g.get("Counties") or [{}])[0].get("GEOID"),
            "tract": (g.get("Census Tracts") or [{}])[0].get("GEOID")}
