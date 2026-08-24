"""Download and index EVERY California address source from OpenAddresses.

112 sources, ~0.60 GB gzipped. Resumable: a `done` table records which sources are
already loaded, so re-running skips them.
"""
import gzip, json, os, sqlite3, sys, time, urllib3, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_address_index import norm_street
urllib3.disable_warnings()

DB  = "data/index/address_points.sqlite"
RAW = "data/addresses"
API = "https://batch.openaddresses.io/api/data"
S3  = "https://v2.openaddresses.io/batch-prod/job/{job}/source.geojson.gz"

def ensure(con):
    con.execute("PRAGMA journal_mode=OFF"); con.execute("PRAGMA synchronous=OFF")
    con.execute("""CREATE TABLE IF NOT EXISTS addr(
        number TEXT, street TEXT, street_n TEXT, unit TEXT,
        city TEXT, postcode TEXT, lat REAL, lon REAL, source TEXT)""")
    con.execute("CREATE TABLE IF NOT EXISTS done(source TEXT PRIMARY KEY, rows INT, ts TEXT)")
    con.commit()

def load(con, path, source):
    n, batch = 0, []
    with gzip.open(path, "rt") as f:
        for line in f:
            try: d = json.loads(line)
            except Exception: continue
            p = d.get("properties", {}); c = (d.get("geometry") or {}).get("coordinates")
            if not c or not p.get("number"): continue
            batch.append((str(p.get("number","")).strip(), p.get("street",""),
                          norm_street(p.get("street")), p.get("unit",""),
                          p.get("city",""), p.get("postcode",""),
                          float(c[1]), float(c[0]), source))
            if len(batch) >= 50000:
                con.executemany("INSERT INTO addr VALUES (?,?,?,?,?,?,?,?,?)", batch)
                n += len(batch); batch = []
    if batch:
        con.executemany("INSERT INTO addr VALUES (?,?,?,?,?,?,?,?,?)", batch); n += len(batch)
    return n

def main():
    os.makedirs(RAW, exist_ok=True)
    con = sqlite3.connect(DB); ensure(con)
    already = {r[0] for r in con.execute("SELECT source FROM done")}
    # the two loaded before this script existed
    already |= {"us/ca/los_angeles", "us/ca/city_of_los_angeles"}
    for s in ("us/ca/los_angeles", "us/ca/city_of_los_angeles"):
        con.execute("INSERT OR IGNORE INTO done VALUES (?,?,?)", (s, -1, "pre-existing"))
    con.commit()

    srcs = [d for d in requests.get(API, timeout=120, verify=False).json()
            if d.get("source","").startswith("us/ca/") and d.get("layer") == "addresses"]
    todo = [d for d in srcs if d["source"] not in already]
    print(f"STATEWIDE: {len(srcs)} CA sources, {len(already)} done, {len(todo)} to fetch", flush=True)
    t0, total = time.time(), 0
    for i, d in enumerate(todo, 1):
        src, job = d["source"], d.get("job")
        if not job:
            print(f"  [{i}/{len(todo)}] {src}: no job id, skipped", flush=True); continue
        fn = os.path.join(RAW, src.replace("/", "_") + ".geojson.gz")
        try:
            if not os.path.exists(fn) or os.path.getsize(fn) < 1000:
                r = requests.get(S3.format(job=job), stream=True, timeout=900, verify=False)
                r.raise_for_status()
                with open(fn, "wb") as f:
                    for ch in r.iter_content(1 << 20): f.write(ch)
            n = load(con, fn, src)
            con.execute("INSERT OR REPLACE INTO done VALUES (?,?,?)",
                        (src, n, time.strftime("%Y-%m-%dT%H:%M:%S")))
            con.commit(); total += n
            os.remove(fn)                      # keep only the index, not the raw files
            print(f"  [{i}/{len(todo)}] {src}: {n:,} rows ({time.time()-t0:.0f}s)", flush=True)
        except Exception as e:
            print(f"  [{i}/{len(todo)}] {src}: FAILED {type(e).__name__} {str(e)[:80]}", flush=True)
    print("  reindexing…", flush=True)
    con.execute("DROP INDEX IF EXISTS ix_num_street")
    con.execute("DROP INDEX IF EXISTS ix_street")
    con.execute("CREATE INDEX ix_num_street ON addr(number, street_n)")
    con.execute("CREATE INDEX ix_street ON addr(street_n)")
    con.commit()
    tot = con.execute("SELECT count(*) FROM addr").fetchone()[0]
    ns  = con.execute("SELECT count(*) FROM done").fetchone()[0]
    con.close()
    print(f"STATEWIDE DONE {tot:,} address points from {ns} sources -> "
          f"{os.path.getsize(DB)/1e9:.2f} GB in {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
