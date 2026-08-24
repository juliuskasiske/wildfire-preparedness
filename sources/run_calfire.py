import calfire, os, sys, json, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
results = {}
for k in calfire.LAYERS:
    t = time.time()
    try:
        out, meta = calfire.fetch(k, outdir="../data/raw")
        sz = os.path.getsize(out) / 1e6
        ok = meta["declared_count"] == meta["retrieved_count"]
        results[k] = dict(path=out, mb=round(sz, 1), **meta, complete=ok, secs=round(time.time()-t))
        print(f"  -> {out} {sz:.1f}MB {meta['retrieved_count']:,}/{meta['declared_count']:,} "
              f"{'OK' if ok else '!! MISMATCH'} in {time.time()-t:.0f}s", flush=True)
    except Exception as e:
        results[k] = dict(error=str(e)); print(f"  !! {k} FAILED: {e}", flush=True)
json.dump(results, open("../data/raw/_calfire_manifest.json", "w"), indent=1)
print("DONE")
