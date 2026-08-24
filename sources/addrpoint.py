"""Official county address-point lookup. The most accurate locator available.

Measured on 3461 Snowden Ave, Long Beach, CA:
    Census (interpolated)      46.5 m off
    Nominatim                  55.1 m off
    snap to nearest building   49.7 m off
    official county point       0.0 m, lands inside a building footprint
At ~15 m lot frontage those errors are 3-4 houses, which is why the viewer was
highlighting the wrong property.
"""
import os, re, sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "data", "index", "address_points.sqlite")

_ABBR = {"street":"st","avenue":"ave","boulevard":"blvd","road":"rd","drive":"dr",
         "lane":"ln","court":"ct","place":"pl","terrace":"ter","circle":"cir",
         "parkway":"pkwy","highway":"hwy","north":"n","south":"s","east":"e",
         "west":"w","trail":"trl","way":"way"}

def norm_street(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(_ABBR.get(w, w) for w in s.split())

def available():
    return os.path.exists(DB)

def parse(address):
    """'3461 Snowden Ave, Long Beach, CA 90808' -> (number, street, city, zip)."""
    a = (address or "").strip()
    zipm = re.search(r"\b(\d{5})(?:-\d{4})?\b\s*$", a)
    zipc = zipm.group(1) if zipm else None
    if zipm: a = a[:zipm.start()].strip().rstrip(",")
    a = re.sub(r",?\s*\b(CA|California)\b\.?\s*$", "", a, flags=re.I).strip().rstrip(",")
    parts = [p.strip() for p in a.split(",") if p.strip()]
    city = parts[1] if len(parts) > 1 else None
    first = parts[0] if parts else a
    m = re.match(r"^(\d+[A-Za-z]?)\s+(.*)$", first)
    if not m: return None, first, city, zipc
    return m.group(1), m.group(2).strip(), city, zipc

_DIRS = ("n", "s", "e", "w")

def _variants(sn):
    """People omit directional prefixes: 'Fair Oaks Ave' vs 'North Fair Oaks Avenue'.
    Try the literal form first, then with each prefix added, then with one stripped."""
    out = [sn]
    parts = sn.split()
    if parts and parts[0] in _DIRS:
        out.append(" ".join(parts[1:]))
    else:
        out.extend(f"{d} {sn}" for d in _DIRS)
    return out

def lookup(address):
    """Exact (number, street) match, narrowed by city/zip when they are given."""
    if not available(): return None
    num, street, city, zipc = parse(address)
    if not num or not street: return None
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = []
    for v in _variants(norm_street(street)):
        rows = con.execute(
            "SELECT number,street,city,postcode,lat,lon,source FROM addr "
            "WHERE number=? AND street_n=?", (num, v)).fetchall()
        if rows: break
    con.close()
    if not rows: return None
    def score(r):
        s = 0
        if zipc and r[3] == zipc: s -= 2
        if city and r[2] and city.lower() == r[2].lower(): s -= 1
        return s
    rows.sort(key=score)
    r = rows[0]
    return {"matched": True, "provider": "county_address_point",
            "precision": "parcel_or_rooftop",
            "matched_address": f"{r[0]} {r[1]}, {r[2]} {r[3]}".strip(),
            "lat": r[4], "lon": r[5], "postcode": r[3], "place": r[2],
            "source": r[6], "candidates": len(rows)}

def nearest_numbers(address, k=6):
    """When the street exists but the house number does not, return real numbers on
    that street. Interpolating geocoders silently invent a position for a nonexistent
    number; this tells the user the address is wrong instead."""
    if not available(): return []
    num, street, city, zipc = parse(address)
    if not num or not street or not num.isdigit(): return []
    target = int(num)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = []
    for v in _variants(norm_street(street)):
        q = ("SELECT number,street,city,postcode,lat,lon FROM addr WHERE street_n=?"
             + (" AND lower(city)=lower(?)" if city else ""))
        args = (v, city) if city else (v,)
        rows = con.execute(q, args).fetchall()
        if rows: break
    con.close()
    cands = [(abs(int(r[0]) - target), r) for r in rows if r[0].isdigit()]
    if not cands: return []
    cands.sort(key=lambda t: t[0])
    seen, out = set(), []
    for _, r in cands:
        if r[0] in seen: continue
        seen.add(r[0])
        out.append({"label": f"{r[0]} {r[1]}, {r[2]} {r[3]}".strip(),
                    "number": r[0], "lat": r[4], "lon": r[5]})
        if len(out) >= k: break
    return out
