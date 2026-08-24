"""Terrain effect on wind, computed directly from the DEM.

WHAT THIS IS: a diagnostic approximation, not a physical solver. WindNinja solves a
mass-conserving flow field; this does not. It computes two well-established terrain
indices and maps them onto a speed multiplier and a deflection angle. Label any output
as approximate.

WHAT IT CAPTURES (the parts that actually matter for ember exposure):
  - shelter: if the ground rises upwind of you, you are in a wind shadow
  - exposure: if the ground falls away upwind, wind arrives unobstructed and accelerates
  - crest speed-up: wind accelerates over ridges
  - deflection: flow turns to follow terrain rather than driving straight into a slope

WHAT IT DOES NOT CAPTURE: separation and recirculation in lee eddies, thermally driven
slope flows, channelling in narrow canyons where the true solution is 3D.

Sx follows Winstral & Marks (2002): the maximum angle to the horizon looking upwind
within a search radius. Positive Sx means sheltered, negative means exposed.
"""
import math
import numpy as np

def _shift(a, dr, dc, fill=np.nan):
    """Shift an array by integer pixels, padding with fill."""
    out = np.full_like(a, fill, dtype=np.float32)
    r0, r1 = max(0, dr), min(a.shape[0], a.shape[0] + dr)
    c0, c1 = max(0, dc), min(a.shape[1], a.shape[1] + dc)
    sr0, sr1 = max(0, -dr), min(a.shape[0], a.shape[0] - dr)
    sc0, sc1 = max(0, -dc), min(a.shape[1], a.shape[1] - dc)
    out[r0:r1, c0:c1] = a[sr0:sr1, sc0:sc1]
    return out

def sx_upwind(dem, px_m, wind_from_deg, dmax_m=300.0, nsteps=12):
    """Maximum upwind horizon angle, in radians. + = sheltered, - = exposed."""
    th = math.radians(wind_from_deg)
    # wind comes FROM this bearing, so 'upwind' is toward it.
    # north = decreasing row; east = increasing column.
    ur, uc = -math.cos(th), math.sin(th)
    best = np.full(dem.shape, -np.inf, dtype=np.float32)
    for k in range(1, nsteps + 1):
        d = dmax_m * k / nsteps
        dr, dc = int(round(ur * d / px_m)), int(round(uc * d / px_m))
        if dr == 0 and dc == 0: continue
        z = _shift(dem, dr, dc)
        ang = np.arctan((z - dem) / d)
        best = np.fmax(best, np.nan_to_num(ang, nan=-np.inf))
    best[~np.isfinite(best)] = 0.0
    return best

def terrain_wind(dem, px_m, wind_from_deg, dmax_m=300.0,
                 k_expose=1.1, k_shelter=1.4, max_deflect_deg=35.0):
    """Return (speed_multiplier, wind_from_deg_local) arrays.

    speed_multiplier is relative to the regional gridMET value: 1.0 = unchanged.
    Clipped to a defensible range; this is an index, not a wind tunnel.
    """
    dem = np.asarray(dem, dtype=np.float32)
    sx = sx_upwind(dem, px_m, wind_from_deg, dmax_m)

    # --- speed ---------------------------------------------------------------
    # sheltered (sx>0) slows, exposed (sx<0) speeds up. tan() so a 10 deg rise
    # upwind matters much less than a 40 deg one.
    mult = np.where(sx > 0,
                    1.0 - k_shelter * np.tanh(np.tan(np.clip(sx, 0, 1.2))),
                    1.0 + k_expose  * np.tanh(np.tan(np.clip(-sx, 0, 1.2))))
    mult = np.clip(mult, 0.45, 1.75).astype(np.float32)

    # --- deflection ----------------------------------------------------------
    # flow turns away from rising ground: use the cross-wind component of the
    # terrain gradient. gy is +north, gx is +east.
    gr, gc = np.gradient(dem, px_m)          # d/drow, d/dcol
    gx, gy = gc, -gr                         # east, north
    th = math.radians(wind_from_deg)
    # unit vector the wind BLOWS TOWARD (opposite of 'from')
    tx, ty = -math.sin(th), -math.cos(th)
    cross = gx * (-ty) + gy * (tx)           # gradient component 90deg left of flow
    scale = np.tanh(cross * 6.0)             # ~saturates by a 1:6 cross slope
    deflect = np.radians(max_deflect_deg) * scale
    local_from = (wind_from_deg + np.degrees(deflect)) % 360.0

    return mult.astype(np.float32), local_from.astype(np.float32), sx.astype(np.float32)

def summarize(dem, px_m, wind_from_deg, centre=None):
    """Property-level numbers for the report."""
    mult, local, sx = terrain_wind(dem, px_m, wind_from_deg)
    n, m = dem.shape
    i, j = centre or (n // 2, m // 2)
    # is the ground rising toward the house from the dangerous direction?
    th = math.radians(wind_from_deg)
    dr, dc = int(round(-math.cos(th) * 150 / px_m)), int(round(math.sin(th) * 150 / px_m))
    ii, jj = np.clip(i + dr, 0, n - 1), np.clip(j + dc, 0, m - 1)
    rise = float(dem[i, j] - dem[ii, jj])     # + means house is ABOVE the upwind ground
    return {
        "speed_multiplier": round(float(mult[i, j]), 2),
        "local_wind_from_deg": round(float(local[i, j]), 1),
        "deflection_deg": round(float(((local[i, j] - wind_from_deg + 180) % 360) - 180), 1),
        "shelter_index_deg": round(float(math.degrees(sx[i, j])), 1),
        "exposure": ("sheltered" if sx[i, j] > 0.09 else
                     "exposed" if sx[i, j] < -0.09 else "neutral"),
        "uphill_of_wind": bool(rise > 3.0),
        "rise_from_upwind_m": round(rise, 1),
    }
