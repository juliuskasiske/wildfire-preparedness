import requests, os, urllib3, time
urllib3.disable_warnings()
URL="https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/California.geojson.zip"
out="../data/raw/ms_footprints_california.geojson.zip"
os.chdir(os.path.dirname(os.path.abspath(__file__)))
t=time.time(); n=0
with requests.get(URL, stream=True, timeout=120, verify=False) as r:
    r.raise_for_status()
    with open(out,"wb") as f:
        for c in r.iter_content(1<<20):
            f.write(c); n+=len(c)
            if n % (100<<20) < (1<<20): print(f"  {n/1e6:.0f} MB ({time.time()-t:.0f}s)", flush=True)
print(f"DONE {n/1e6:.0f} MB in {time.time()-t:.0f}s -> {out}", flush=True)
