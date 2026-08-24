import sys, requests, os, urllib3, time; urllib3.disable_warnings()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,'sources'); from terrain import lidar_tiles
t=[x for x in lidar_tiles(34.04953,-118.53126,pad_deg=0.0005) if x['year']=='2025']
pick=sorted(t,key=lambda z:z['mb'])[0]
out=f"data/lidar/{os.path.basename(pick['url'])}"
print(f"START {pick['mb']}MB {pick['title'][:60]}",flush=True)
t0=time.time(); n=0
r=requests.get(pick['url'],stream=True,timeout=900,verify=False); r.raise_for_status()
with open(out,'wb') as f:
    for c in r.iter_content(1<<20):
        f.write(c); n+=len(c)
        if n%(25<<20)<(1<<20): print(f"  {n/1e6:.0f}MB",flush=True)
print(f"LIDAR2025 DONE {os.path.getsize(out)/1e6:.1f}MB in {time.time()-t0:.0f}s -> {out}",flush=True)
