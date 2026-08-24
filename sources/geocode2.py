"""Address resolution with a fallback chain and autocomplete.

Three free providers, no API keys:
  Census    authoritative US, returns county + incorporated place (needed for
            jurisdiction), but misses venues, new construction and partial addresses.
  Nominatim OSM. Best house-number matching. Usage policy: <=1 req/sec, real
            User-Agent required. Used as the fallback, not the default.
  Photon    Komoot's OSM autocomplete. Fast, tolerant of partial input, but often
            drops the house number and returns a street/city centroid — so it is
            used for SUGGESTIONS ONLY, never as the final coordinate.
"""
import threading, time, requests, urllib3
urllib3.disable_warnings()

UA = {"User-Agent": "artesia-wildfire-assessment/0.1 (contact: julius@kasiske.de)"}
_nominatim_lock = threading.Lock()
_last_nominatim = [0.0]

def _nominatim_throttle():
    with _nominatim_lock:
        wait = 1.05 - (time.time() - _last_nominatim[0])
        if wait > 0: time.sleep(wait)
        _last_nominatim[0] = time.time()

def suggest(q, limit=6, timeout=12):
    """Autocomplete candidates, California only.

    Nominatim, not Photon: Photon drops house numbers entirely, so '3461 snowden'
    returned nothing usable. Nominatim returns exact house-number matches in 0.2-0.9 s.
    Throttled to <=1 req/sec per their usage policy, so debounce the UI by ~350 ms.
    """
    if len(q.strip()) < 3: return []
    _nominatim_throttle()
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search", timeout=timeout,
            verify=False, headers=UA,
            params={"q": q, "format": "json", "limit": limit, "countrycodes": "us",
                    "addressdetails": 1,
                    "viewbox": "-124.50,42.05,-114.10,32.50", "bounded": 1})
        j = r.json()
    except Exception:
        return []
    out, seen = [], set()
    for x in j:
        a = x.get("address", {})
        parts = [" ".join(v for v in (a.get("house_number"), a.get("road")) if v),
                 a.get("city") or a.get("town") or a.get("village") or a.get("hamlet"),
                 a.get("state"), a.get("postcode")]
        label = ", ".join(v for v in parts if v) or x.get("display_name", "")[:90]
        if label in seen: continue
        seen.add(label)
        out.append({"label": label,
                    "exact": bool(a.get("house_number")),
                    "lat": float(x["lat"]), "lon": float(x["lon"]),
                    "kind": x.get("type")})
    out.sort(key=lambda o: not o["exact"])       # exact house numbers first
    return out

def _nominatim(address, timeout=20):
    _nominatim_throttle()
    r = requests.get("https://nominatim.openstreetmap.org/search", timeout=timeout,
        verify=False, headers=UA,
        params={"q": address, "format": "json", "limit": 1,
                "countrycodes": "us", "addressdetails": 1})
    j = r.json()
    if not j: return None
    top = j[0]; a = top.get("address", {})
    county = (a.get("county") or "").replace(" County", "") or None
    place = a.get("city") or a.get("town") or a.get("village") or None
    return {"matched": True, "provider": "nominatim",
            "matched_address": top.get("display_name", address),
            "lat": float(top["lat"]), "lon": float(top["lon"]),
            "state": a.get("state"), "county": county, "place": place,
            "postcode": a.get("postcode"),
            "precision": "rooftop" if a.get("house_number") else "approximate"}

def _snap(g):
    """Last resort only. Snapping to the nearest footprint does NOT rescue a badly
    interpolated point: measured 49.7 m off on Snowden, barely better than the 46.5 m
    it started from. It is here to avoid rendering a point in the middle of a road."""
    try:
        from snap import snap_to_building
        s = snap_to_building(g["lat"], g["lon"])
        if s.get("method") == "snapped_to_nearest_building":
            return {"lat": s["lat"], "lon": s["lon"], "snapped": True,
                    "snap_moved_m": s["moved_m"], "precision": "snapped_approximate"}
    except Exception:
        pass
    return {}

def resolve(address, timeout=25, snap=True):
    """Official county address point first, then Census, then Nominatim.

    Order matters and is measured. On 3461 Snowden Ave, Long Beach:
        county address point   0.0 m  (lands inside the building footprint)
        Census interpolation  46.5 m
        Nominatim             55.1 m
    At ~15 m lot frontage the geocoders are 3-4 houses off, which is why the
    viewer was highlighting the wrong property.
    """
    from geocode import geocode as census
    try:
        from addrpoint import lookup as addr_lookup
        ap = addr_lookup(address)
        if ap: return ap
    except Exception:
        pass
    errs = []
    try:
        g = census(address, timeout=timeout)
        if g.get("matched"):
            g["provider"] = "census"; g["precision"] = "interpolated"
            if snap: g.update(_snap(g))
            return g
        errs.append("census: " + str(g.get("error", "no match")))
    except Exception as e:
        errs.append(f"census: {type(e).__name__}")
    try:
        n = _nominatim(address, timeout=timeout)
        if n:
            if snap and n.get("precision") != "rooftop": n.update(_snap(n))
            return n
        errs.append("nominatim: no match")
    except Exception as e:
        errs.append(f"nominatim: {type(e).__name__}: {e}")
    return {"matched": False, "address": address, "error": "; ".join(errs),
            "hint": "Try adding the city and state, e.g. '123 Main St, Altadena, CA'."}
