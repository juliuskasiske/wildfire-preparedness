#!/usr/bin/env python3
"""
Build the address autocomplete index served by web/st/.

Source is data/index/address_points.sqlite, the 18.9M official county address
points already pulled by sources/. We do not ship all 18.9M: the user types
their own house number, so what autocomplete has to supply is the street. There
are only 543,810 distinct (street, city, zip) combinations in California, which
is 19 MB of text instead of 670 MB.

Shipping it as static files rather than a database is deliberate. Cloudflare
Pages serves and caches them at the edge for nothing, there is no runtime query,
no third party ever sees what anyone types, and the privacy notice stays true
as written.

Shards are split adaptively on the normalised street name until each is small
enough to fetch on a phone. A manifest lists the keys so the client knows which
file to ask for.

    python3 tools/build_street_index.py
"""
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict

DB       = "data/index/address_points.sqlite"
OUT      = "web/st"
MAX_ROWS = 2500          # per shard, roughly 70 KB raw and 18 KB over the wire
MIN_KEY  = 2             # shortest shard key; the client needs 2 chars to search

# Roughly one row in five is a placeholder rather than a street. Riverside
# County alone contributes 132,539 rows of "UNASSIGNED <parcel number>". Left
# in, a fifth of every dropdown would be parcel numbers.
JUNK = [
    (re.compile(r"^UNASSIGNED\b", re.I),                    "UNASSIGNED <parcel>"),
    (re.compile(r"\d{6,}"),                                 "6+ digit run"),
    (re.compile(r"^(UNNAMED|UNKNOWN|NONE|NULL|N/?A)\b", re.I), "unnamed/unknown"),
    (re.compile(r"^PRIVATE\b", re.I),                       "private road"),
    (re.compile(r"^[^A-Za-z]*$"),                           "no letters"),
]

def normalise(s):
    """Lowercase, strip punctuation, collapse spaces. The client normalises the
    same way, so the two always agree on which shard a query belongs to."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()

# Only genuine directionals stay upper case. An earlier version kept any
# two-letter capitalised word, which turned "EL MEDIO ST" into "EL Medio ST".
DIRECTIONS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}

def title(s):
    """County data is a mix of ALL CAPS and Mixed Case. Show one style."""
    def fix(m):
        w = m.group(0)
        return w.upper() if w.upper() in DIRECTIONS else w[0].upper() + w[1:].lower()
    return re.sub(r"[A-Za-z]+", fix, s)

def main():
    if not os.path.exists(DB):
        sys.exit(f"missing {DB}. Run the sources/ scripts first.")

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT DISTINCT street, city, postcode FROM addr "
        "WHERE street != '' AND city != '' AND postcode != ''"
    )

    dropped = defaultdict(int)
    seen = set()
    keep = []
    for street, city, zipc in rows:
        hit = next((label for rx, label in JUNK if rx.search(street)), None)
        if hit:
            dropped[hit] += 1
            continue
        key = normalise(street)
        if len(key) < 2:
            dropped["too short"] += 1
            continue
        ident = (key, normalise(city), zipc)
        if ident in seen:
            continue
        seen.add(ident)
        keep.append((key, title(street), title(city), zipc))

    print(f"kept {len(keep):,} streets")
    for label, n in sorted(dropped.items(), key=lambda x: -x[1]):
        print(f"  dropped {n:>7,}  {label}")

    # ---- adaptive sharding -------------------------------------------------
    # Start every street in its 2-character bucket, then keep extending the key
    # of any bucket that is still too big. Skewed letter frequencies mean a
    # fixed key length gives one 560 KB shard and hundreds of tiny ones.
    buckets = defaultdict(list)
    for rec in keep:
        buckets[rec[0][:MIN_KEY]].append(rec)

    final = {}
    queue = list(buckets.items())
    while queue:
        key, recs = queue.pop()
        if len(recs) <= MAX_ROWS or len(key) >= 10:
            final[key] = recs
            continue
        split = defaultdict(list)
        for rec in recs:
            # Streets shorter than the key land in the shard as-is.
            split[rec[0][:len(key) + 1]].append(rec)
        if len(split) == 1:            # cannot divide further, keep it whole
            final[key] = recs
            continue
        queue.extend(split.items())

    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))

    total = 0
    biggest = ("", 0)
    for key, recs in final.items():
        recs.sort(key=lambda r: (r[0], r[2], r[3]))
        # Tab separated, not JSON: the same data costs about a third less and
        # split('\t') is as cheap as JSON.parse.
        body = "\n".join(f"{disp}\t{city}\t{zipc}" for _, disp, city, zipc in recs)
        path = os.path.join(OUT, f"{key}.txt")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        size = os.path.getsize(path)
        total += size
        if size > biggest[1]:
            biggest = (key, size)

    manifest = sorted(final.keys())
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, separators=(",", ":"))

    print(f"\n{len(final)} shards, {total/1e6:.1f} MB total")
    print(f"largest shard: {biggest[0]}.txt at {biggest[1]/1024:.0f} KB")
    print(f"manifest: {len(manifest)} keys, "
          f"{os.path.getsize(os.path.join(OUT,'manifest.json'))/1024:.1f} KB")

if __name__ == "__main__":
    main()
