#!/usr/bin/env python
"""End-to-end check of every free source. Run from repo root: .venv/bin/python sources/verify.py"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warnings; warnings.filterwarnings("ignore")
from geocode import geocode
from lookup import fhsz, firewise_site, nearest_structures
from terrain import slope_aspect, lidar_tiles

CASES = [
    ("15751 Sunset Blvd, Pacific Palisades, CA 90272", "burn scar, coastal VHFHSZ"),
    ("2200 Fair Oaks Ave, Altadena, CA 91001",         "burn scar, unincorporated"),
    ("1200 K St, Sacramento, CA 95814",                "urban control, expect no hazard"),
    ("10161 Alta Sierra Dr, Grass Valley, CA 95949",   "Sierra foothills, expect SRA"),
]

def main():
    ok = True
    for addr, why in CASES:
        print(f"\n{'='*74}\n{addr}\n  ({why})")
        t = time.time()
        g = geocode(addr)
        if not g["matched"]:
            print(f"  GEOCODE: no match  {g.get('error','')}"); ok = False; continue
        print(f"  geocode      {g['lat']:.5f},{g['lon']:.5f}  {g['place'] or '(unincorporated)'} / {g['county']} County")
        z = fhsz(g["lat"], g["lon"])
        print(f"  hazard       fhsz={z['fhsz'] or '-'} ({z['fhsz_source'] or '-'})  "
              f"resp_area={z['responsibility_area'] or '-'}  ab38_layer={z['ab38_fhsz'] or '-'}")
        t2 = slope_aspect(g["lat"], g["lon"])
        print(f"  terrain      slope={t2['slope_pct']}%  aspect={t2['aspect_deg']}deg  elev={t2['elevation_m']}m")
        fw = firewise_site(g["lat"], g["lon"], 4000)
        print(f"  firewise     {len(fw)} site(s) within 4km" +
              (f"  nearest '{fw[0]['name']}' at {fw[0]['km']}km" if fw else ""))
        ns = nearest_structures(g["lat"], g["lon"], 120)
        print(f"  footprints   {ns if ns else 'INDEX NOT BUILT'}")
        lt = lidar_tiles(g["lat"], g["lon"], pad_deg=0.001)
        print(f"  lidar        {len(lt)} tile(s), {sum(x['mb'] for x in lt):.0f}MB, newest {max((x['year'] for x in lt), default='-')}")
        print(f"  [{time.time()-t:.1f}s total]")
    print(f"\n{'='*74}\n{'PASS' if ok else 'PARTIAL — see notes above'}")

if __name__ == "__main__":
    main()
