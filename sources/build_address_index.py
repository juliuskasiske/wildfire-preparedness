"""OpenAddresses county file -> a small SQLite lookup keyed on (street, number).

Official county address points are placed on the parcel/rooftop. Measured against
3461 Snowden Ave, Long Beach: Census interpolation is 46.5 m off, Nominatim 55.1 m,
snap-to-nearest-building 49.7 m. The official point is 0 m and lands inside a
footprint. At ~15 m lot frontage those errors are 3-4 houses.
"""
import gzip, json, os, re, sqlite3, sys, time

def norm_street(s):
    """Normalise so 'W 112th St' and 'West 112th Street' collide."""
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    words = {"street":"st","avenue":"ave","boulevard":"blvd","road":"rd","drive":"dr",
             "lane":"ln","court":"ct","place":"pl","terrace":"ter","circle":"cir",
             "parkway":"pkwy","highway":"hwy","north":"n","south":"s","east":"e","west":"w",
             "trail":"trl","way":"way"}
    return " ".join(words.get(w, w) for w in s.split())

def build(gz_path, db_path, source_name):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=OFF")   # sqlite3.execute takes ONE statement
    con.execute("PRAGMA synchronous=OFF")
    con.execute("""CREATE TABLE IF NOT EXISTS addr(
        number TEXT, street TEXT, street_n TEXT, unit TEXT,
        city TEXT, postcode TEXT, lat REAL, lon REAL, source TEXT)""")
    n, t0, batch = 0, time.time(), []
    with gzip.open(gz_path, "rt") as f:
        for line in f:
            try: d = json.loads(line)
            except Exception: continue
            p = d.get("properties", {}); c = (d.get("geometry") or {}).get("coordinates")
            if not c or not p.get("number"): continue
            batch.append((str(p.get("number","")).strip(), p.get("street",""),
                          norm_street(p.get("street")), p.get("unit",""),
                          p.get("city",""), p.get("postcode",""),
                          float(c[1]), float(c[0]), source_name))
            if len(batch) >= 50000:
                con.executemany("INSERT INTO addr VALUES (?,?,?,?,?,?,?,?,?)", batch)
                n += len(batch); batch = []
                print(f"  {n:,} ({time.time()-t0:.0f}s)", flush=True)
    if batch:
        con.executemany("INSERT INTO addr VALUES (?,?,?,?,?,?,?,?,?)", batch); n += len(batch)
    print("  indexing…", flush=True)
    con.execute("CREATE INDEX IF NOT EXISTS ix_num_street ON addr(number, street_n)")
    con.execute("CREATE INDEX IF NOT EXISTS ix_street ON addr(street_n)")
    con.commit(); con.close()
    print(f"ADDRINDEX DONE {n:,} rows -> {db_path} "
          f"({os.path.getsize(db_path)/1e6:.0f} MB) in {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    build("data/addresses/la_county_addresses.geojson.gz",
          "data/index/address_points.sqlite", "us/ca/los_angeles")
