"""The six homeowner statistics, derived from the gridMET accumulation.

Nothing here averages a bearing arithmetically. Direction comes out of a 16-sector
histogram via vector summation, because 350 deg and 10 deg must average to 0, not 180.
"""
import math, os
import numpy as np

NPZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "data", "wind", "ca_firewind.npz")
SECTORS = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
           "S","SSW","SW","WSW","W","WNW","NW","NNW"]
MONTHS  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
LAT0, LON0, STEP = 49.4000, -124.7667, 1.0 / 24.0

_C = {}
def _load():
    if "d" not in _C:
        if not os.path.exists(NPZ): return None
        _C["d"] = np.load(NPZ)
    return _C["d"]

def available(): return os.path.exists(NPZ)

def cell_index(lat, lon, d):
    """Map lat/lon to an index inside the stored California window."""
    gi = int(round((LAT0 - lat) / STEP))          # global row (lat descends)
    gj = int(round((lon - LON0) / STEP))          # global col
    i, j = gi - int(d["ia"]), gj - int(d["ja"])
    h = d["hist"]
    if not (0 <= i < h.shape[0] and 0 <= j < h.shape[1]): return None
    return i, j

MIN_DAYS = 40      # >=2 qualifying days a year over a 20-year record

def stats(lat, lon, pct=90.0, max_rh=20.0, min_days=None):
    """max_rh: humidity ceiling for a 'dangerous' day. 15% separates Santa Ana and
    Diablo events from merely windy humid marine days; 20% does not."""
    d = _load()
    if d is None: return {"available": False, "reason": "gridMET climatology not built yet"}
    idx = cell_index(lat, lon, d)
    if idx is None: return {"available": False, "reason": "outside the California grid"}
    i, j = idx
    rh_edges = d["rh_edges"] if "rh_edges" in d.files else None
    if rh_edges is not None:
        nrh = int(np.clip(np.searchsorted(rh_edges, max_rh, side="left") + 1, 1, len(rh_edges)))
        hist = d["hist"][i, j][:, :, :nrh].sum(axis=2)      # [sector][band]
    else:
        hist = d["hist"][i, j]
    edges = d["band_edges"]
    nyears = len(d["years"])

    # per-cell wind-speed percentile, from the all-days histogram
    sh = d["spd_hist"][i, j].astype(np.float64)
    if sh.sum() == 0: return {"available": False, "reason": "no data in this cell"}
    cum = np.cumsum(sh) / sh.sum()
    thr_ms = float(np.searchsorted(cum, pct / 100.0) * 0.5)
    # bands are 0.5 m/s wide; take the first band at or above the threshold so we do
    # NOT sweep in the band the threshold sits inside (that bug counted 37% of dry days
    # as "dangerous" at Pacific Palisades instead of the intended 10%).
    band_min = int(np.clip(np.searchsorted(edges, thr_ms, side="left"), 0, len(edges) - 1))

    dang = hist[:, band_min:].sum(axis=1).astype(np.float64)   # per sector
    total = float(dang.sum())
    # A direction decided by a handful of days is noise, not a pattern. Oakland Hills
    # had 16 qualifying days in 20 YEARS and its "dominant" sector was 5 days vs 3 -
    # and it disagreed with the 1991 firestorm, which was north-easterly. Coastal
    # Northern California rarely drops below 20% humidity in gridMET's daily minimum,
    # so almost nothing passes the filter there. Say so rather than invent an arrow.
    need = MIN_DAYS if min_days is None else min_days
    if total < need:
        return {"available": False, "n_days": int(total), "min_days": need,
                "reason": (f"only {int(total)} qualifying days in "
                           f"{nyears} years - too few to identify a wind pattern here")}

    # vector mean of direction, weighted by count -- NOT an arithmetic mean
    ang = np.radians(np.arange(16) * 22.5)
    vx, vy = float((dang * np.sin(ang)).sum()), float((dang * np.cos(ang)).sum())
    mean_from = (math.degrees(math.atan2(vx, vy)) + 360.0) % 360.0
    concentration = math.hypot(vx, vy) / total     # 0 = scattered, 1 = all one way

    # HEADLINE DIRECTION = the modal sector, not the vector mean.
    # They can disagree badly: a scattered distribution gave "from N" with a vector
    # mean of 148 deg (SSE) - a flat contradiction on screen. The vector mean is only
    # meaningful when the distribution is concentrated, so it stays a diagnostic.
    k = int(np.argmax(dang))
    share = dang[k] / total
    # top three adjacent-ish sectors, for a fairer "share" of the dominant quarter
    quarter = sum(dang[(k + o) % 16] for o in (-1, 0, 1)) / total

    mon = d["month"][i, j].astype(np.float64)
    mon_share = mon / max(mon.sum(), 1)
    top_m = list(np.argsort(-mon_share)[:3])

    concentrated = concentration > 0.35
    return {
        "available": True,
        "dominant_sector": SECTORS[k],
        "dominant_from_deg": float(k * 22.5),
        # what the arrow and the terrain model should use
        "headline_from_deg": float(k * 22.5),
        "directional": bool(concentrated),
        "vector_mean_from_deg": round(mean_from, 1),
        "vector_mean_is_meaningful": bool(concentrated),
        "share_of_dangerous_days": round(float(share), 3),
        "share_within_one_sector_either_side": round(float(quarter), 3),
        "concentration": round(float(concentration), 3),
        "pattern": ("strongly directional" if concentration > 0.6 else
                    "moderately directional" if concentration > 0.35 else "scattered"),
        "dangerous_days_per_year": round(total / nyears, 1),
        # gridMET wind is a DAILY MEAN at 10 m, not a gust. A 90th-percentile daily
        # mean of ~7 mph reads as trivial to a homeowner even though it marks a genuinely
        # windy day. Lead with the percentile; keep mph as a labelled technical detail.
        "threshold_percentile": pct,
        "threshold_daily_mean_ms": round(thr_ms, 1),
        "threshold_daily_mean_mph": round(thr_ms * 2.23694, 1),
        "threshold_note": ("daily AVERAGE wind, not gusts - gusts on these days are "
                           "several times higher"),
        "peak_months": [MONTHS[m] for m in top_m],
        "years": [int(d["years"][0]), int(d["years"][-1])],
        "sector_counts": {SECTORS[s]: int(dang[s]) for s in range(16)},
        "note": ("4 km grid: these figures describe the AREA, not this individual "
                 "property. Month figures are for dry days generally."),
        "headline": (f"On the windiest, driest days here, wind comes from the "
                     f"{SECTORS[k]} about {round(float(share)*100)}% of the time."
                     if concentrated else
                     "Dangerous winds here come from no single direction - they are "
                     "scattered, so do not prioritise one side of the house."),
    }

# ---------------------------------------------------------------------------
# Framing metrics.
#
# "Wind comes from the NE on 26% of high-risk days" invites the obvious reply:
# "so what about the other 74%?" The share of a single 22.5 deg sector will almost
# always look weak, because real wind events wander across neighbouring sectors.
# Slicing finer makes the headline number smaller without changing the physics.
#
# Two framings below avoid that, and neither needs a hand-drawn grouping.
# ---------------------------------------------------------------------------

def narrowest_arc(counts, target=0.75):
    """Smallest contiguous compass arc containing `target` of the days.

    Self-answering: "three quarters of high-risk days come from a 90 degree arc
    centred on the north-east" leaves no missing remainder to ask about.
    """
    c = np.asarray([counts[s] for s in SECTORS], dtype=float)
    tot = c.sum()
    if tot <= 0: return None
    best = None
    for width in range(1, 17):                       # 22.5 deg .. full circle
        for start in range(16):
            idx = [(start + k) % 16 for k in range(width)]
            share = c[idx].sum() / tot
            if share >= target:
                if best is None or width < best["width_sectors"]:
                    mid = (start + (width - 1) / 2.0) % 16
                    best = {"width_deg": width * 22.5,
                            "width_sectors": width,
                            "centre_deg": round(mid * 22.5, 1),
                            "centre_sector": SECTORS[int(round(mid)) % 16],
                            "share": round(float(share), 3),
                            "from_sector": SECTORS[start],
                            "to_sector": SECTORS[(start + width - 1) % 16]}
        if best: break
    return best

def wall_exposure(counts, facings=8):
    """Share of high-risk days each side of the house is the windward one.

    A wall faces a 180 deg arc, so this asks 'is the wind hitting this wall at all'.
    The complement is simply the opposite wall, which is an intuitive answer rather
    than an unexplained remainder. This is also what the recommendation needs:
    which elevation to harden first.
    """
    c = np.asarray([counts[s] for s in SECTORS], dtype=float)
    tot = c.sum()
    if tot <= 0: return {}
    step = 16 // facings
    out = {}
    for f in range(facings):
        centre = f * step
        # wind FROM within +-90 deg of the wall's outward normal hits that wall
        idx = [(centre + k) % 16 for k in range(-4, 5)]
        w = np.ones(len(idx)); w[0] = w[-1] = 0.5     # half-weight the edges
        out[SECTORS[centre]] = round(float((c[idx] * w).sum() / tot), 3)
    return out

# ---------------------------------------------------------------------------
# Per-WALL exposure from the real footprint.
#
# Compass-aligned facings are wrong twice over: houses are rotated arbitrarily, and
# a wind from a corner hits TWO walls, not one. Using the actual Overture footprint
# fixes both - each wall segment gets its own outward normal, and when two adjacent
# walls both score high we say "north-east corner" instead of picking a winner.
# ---------------------------------------------------------------------------

def _outward_normals(ring):
    """(bearing_deg, length_m, midpoint) per edge. Winding-independent: the normal is
    chosen to point away from the centroid, so it works for either ring direction."""
    n = len(ring)
    cx = sum(p[0] for p in ring) / n
    cy = sum(p[1] for p in ring) / n
    out = []
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        L = math.hypot(ex, ey)
        if L < 0.5: continue                      # ignore slivers
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = ey, -ex                          # one of the two perpendiculars
        if (mx - cx) * nx + (my - cy) * ny < 0:   # flip if it points inward
            nx, ny = -nx, -ny
        b = (math.degrees(math.atan2(nx, ny)) + 360.0) % 360.0   # bearing the wall faces
        out.append({"bearing": b, "length": L, "mid": (mx, my)})
    return out

def _exposure_for_bearing(counts, facing_deg):
    """Share of high-risk days with wind arriving within 90 deg of this wall's normal."""
    c = np.asarray([counts[s] for s in SECTORS], dtype=float)
    tot = c.sum()
    if tot <= 0: return 0.0
    sec_deg = np.arange(16) * 22.5
    # wind FROM sec_deg hits a wall FACING facing_deg when the angle between them < 90
    diff = np.abs(((sec_deg - facing_deg + 180.0) % 360.0) - 180.0)
    w = np.clip((90.0 - diff) / 22.5 + 0.5, 0.0, 1.0)     # taper at the edges
    return float((c * w).sum() / tot)

def walls_from_footprint(ring, counts, merge_deg=35.0):
    """Group footprint edges into walls by BEARING and score each.

    Grouping by contiguity was wrong: an articulated facade (bays, notches, an L-plan)
    has its east-facing edges split up around the ring, which produced five separate
    "east walls" of 3-6 m each. A homeowner means one east side. It also broke corner
    detection, because the two highest-scoring entries were duplicates of one side.
    """
    edges = _outward_normals(ring)
    if not edges: return []
    groups = []
    for e in sorted(edges, key=lambda x: -x["length"]):     # seed with the longest
        for g in groups:
            if abs(((e["bearing"] - g["bearing"] + 180) % 360) - 180) <= merge_deg:
                a1, a2 = math.radians(g["bearing"]), math.radians(e["bearing"])
                x = g["length"] * math.sin(a1) + e["length"] * math.sin(a2)
                y = g["length"] * math.cos(a1) + e["length"] * math.cos(a2)
                g["bearing"] = (math.degrees(math.atan2(x, y)) + 360) % 360
                g["length"] += e["length"]
                g["segments"] += 1
                break
        else:
            groups.append({"bearing": e["bearing"], "length": e["length"], "segments": 1})
    for w in groups:
        w["exposure"] = round(_exposure_for_bearing(counts, w["bearing"]), 3)
        w["faces"] = SECTORS[int(round(w["bearing"] / 22.5)) % 16]
        w["length_m"] = round(w["length"], 1)
        w["bearing"] = round(w["bearing"], 1)
        w["lift_vs_random"] = round(w["exposure"] / 0.5, 2)
        del w["length"]
    groups.sort(key=lambda w: -w["exposure"])
    return groups

def corner_or_wall(walls, close_pct=0.08):
    """If the top two walls are adjacent in bearing and score similarly, the wind is
    hitting a CORNER. Saying 'your north-east corner' beats naming one wall when the
    physics says both are windward."""
    if len(walls) < 2: return {"kind": "wall", "walls": walls[:1]}
    a, b = walls[0], walls[1]
    gap = abs(((a["bearing"] - b["bearing"] + 180) % 360) - 180)
    if a["exposure"] - b["exposure"] <= close_pct and 45 <= gap <= 135:
        x = math.sin(math.radians(a["bearing"])) + math.sin(math.radians(b["bearing"]))
        y = math.cos(math.radians(a["bearing"])) + math.cos(math.radians(b["bearing"]))
        cb = (math.degrees(math.atan2(x, y)) + 360) % 360
        return {"kind": "corner", "faces": SECTORS[int(round(cb / 22.5)) % 16],
                "bearing": round(cb, 1), "walls": [a, b],
                "exposure": round(max(a["exposure"], b["exposure"]), 3)}
    return {"kind": "wall", "walls": [a]}
