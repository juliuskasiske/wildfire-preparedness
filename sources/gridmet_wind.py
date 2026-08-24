"""gridMET fire-weather wind climatology for California.

Single pass, nothing raw kept. For every 4 km cell we accumulate a small histogram:
    [16 compass sectors] x [8 wind-speed bands]   counted only on DRY days
plus a per-month tally. From that we can derive, after the fact:
  - a per-cell wind-speed percentile threshold (so the definition of "windy" adapts
    to local climate instead of a fixed number that means different things in
    Death Valley and San Francisco)
  - dominant direction on dangerous days, and what share of them it accounts for
  - days per year, and the months they fall in

Direction is accumulated as SECTOR COUNTS, never as a running mean: 350 deg and
10 deg average arithmetically to 180 deg, which is exactly backwards. Vector maths
is applied at the end, from the histogram.
"""
import numpy as np, netCDF4, os, sys, time, json

BASE = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/MET"
# Do NOT hardcode the inner variable names. rmin's variable is plain
# "relative_humidity", not "daily_minimum_relative_humidity" - guessing it cost a
# full 20-year run. Detect whatever data variable the file actually contains.
COORDS = {"lat", "lon", "day", "crs"}

def data_var(ds):
    names = [k for k in ds.variables if k not in COORDS]
    if not names: raise KeyError(f"no data variable in {ds.filepath() if hasattr(ds,'filepath') else '?'}")
    return names[0]
IA, IB, JA, JB = 176, 406, 6, 256          # California window in the gridMET grid
NLAT, NLON = IB - IA + 1, JB - JA + 1
NSEC = 16
# 0.5 m/s bands to 12 m/s. The original 8 coarse bands (0,2,3,4,5,6,7,8) made the
# percentile threshold round down badly: at Pacific Palisades a 3.50 m/s cutoff fell
# into the ">=3.0" band and swept in 37% of dry days instead of the intended 10%,
# diluting the directional signal into noise. The error varied by location depending
# on where the local threshold happened to fall relative to a band edge.
NBAND = 25
# Humidity is stored as a DIMENSION, not a fixed filter. Reason: a wind percentile
# alone picks the windiest days, and the windiest days are not the fire days
# everywhere. Coastal NorCal's strongest daily-mean winds are humid marine flow, so
# Oakland Hills came out WSW (sea breeze) when the 1991 firestorm was north-easterly.
# Diablo/Santa Ana events are far drier, so the RH cut is what separates them - and it
# needs to be tunable after the fact rather than baked in at download time.
RH_EDGES = np.array([0.0, 10.0, 15.0, 20.0, 30.0], dtype=np.float32)   # upper bounds
NRH = len(RH_EDGES)
BAND_EDGES = (np.arange(NBAND) * 0.5).astype(np.float32)            # m/s lower bounds

def open_var(v, year, tries=4):
    for a in range(tries):
        try:
            ds = netCDF4.Dataset(f"{BASE}/{v}/{v}_{year}.nc")
            return ds
        except Exception as e:
            if a == tries - 1: raise
            time.sleep(3 * (a + 1))

def run(years, out="data/wind/ca_firewind.npz", log=print):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    hist  = np.zeros((NLAT, NLON, NSEC, NBAND, NRH), dtype=np.int32)
    month = np.zeros((NLAT, NLON, 12), dtype=np.int32)
    spd_hist = np.zeros((NLAT, NLON, 40), dtype=np.int32)     # 0.5 m/s bins, ALL days
    ndays = 0
    t0 = time.time()
    for y in years:
        try:
            dsv = open_var("vs", y); dst = open_var("th", y); dsr = open_var("rmin", y)
            vs = np.asarray(dsv.variables[data_var(dsv)][:, IA:IB+1, JA:JB+1], dtype=np.float32)
            th = np.asarray(dst.variables[data_var(dst)][:, IA:IB+1, JA:JB+1], dtype=np.float32)
            rh = np.asarray(dsr.variables[data_var(dsr)][:, IA:IB+1, JA:JB+1], dtype=np.float32)
            days = np.asarray(dsv.variables["day"][:])
            for d in (dsv, dst, dsr): d.close()
        except Exception as e:
            log(f"  {y}: FAILED {type(e).__name__} {str(e)[:70]}"); continue
        ndays += vs.shape[0]
        # speed histogram over every day, for the per-cell percentile
        sb = np.clip((vs / 0.5).astype(np.int16), 0, 39)
        for b in range(40):
            spd_hist[:, :, b] += (sb == b).sum(axis=0)
        # dangerous-day histogram: dry days only
        dry = rh <= RH_EDGES[-1]
        rhb = np.clip(np.searchsorted(RH_EDGES, rh, side="left"), 0, NRH - 1)
        sec = np.mod(np.round(th / 22.5).astype(np.int16), NSEC)      # 16 compass sectors
        band = np.clip(np.searchsorted(BAND_EDGES, vs, side="right") - 1, 0, NBAND - 1)
        # month index from days-since-1900
        import datetime
        base = datetime.date(1900, 1, 1)
        mon = np.array([(base + datetime.timedelta(days=int(x))).month - 1 for x in days])
        for t in range(vs.shape[0]):
            m = dry[t]
            if not m.any(): continue
            np.add.at(hist, (np.where(m)[0], np.where(m)[1], sec[t][m], band[t][m], rhb[t][m]), 1)
            np.add.at(month, (np.where(m)[0], np.where(m)[1], mon[t]), 1)
        log(f"  {y}: {vs.shape[0]} days, {int(dry.sum()):,} dry cell-days ({time.time()-t0:.0f}s)", )
    if ndays == 0:
        raise RuntimeError("no years loaded - refusing to write an empty climatology")
    np.savez_compressed(out, hist=hist, month=month, spd_hist=spd_hist,
                        years=np.array(list(years)), ndays=ndays,
                        band_edges=BAND_EDGES, rh_edges=RH_EDGES,
                        ia=IA, ib=IB, ja=JA, jb=JB)
    log(f"GRIDMET DONE {len(years)} years, {ndays} days -> {out} "
        f"({os.path.getsize(out)/1e6:.1f} MB) in {time.time()-t0:.0f}s")

if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 2006
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    run(range(a, b + 1))
