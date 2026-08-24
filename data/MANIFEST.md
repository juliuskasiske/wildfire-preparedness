# Free data sources — what was pulled, how to use it, what's wrong with it

Everything here is free and requires no API key. Run `sources/verify.py` to re-check.

## Downloaded and indexed (point lookup, offline, ~100–250 ms)

| Dataset | Raw | Indexed | Records | Vintage |
|---|---|---|---|---|
| CAL FIRE FHSZ — State Responsibility Areas | 220 MB | 97 MB | 21,169 | 2024 |
| CAL FIRE FHSZ — Local Responsibility Areas | 102 MB | 46 MB | 9,752 | map dated 2025-03-24 |
| CAL FIRE FHSZ — **for Real Estate Inspections (AB 38)** | 221 MB | 7.7 MB | 21,157 | 2024 |
| CAL FIRE Responsibility Areas (SRA/LRA/FRA) | 114 MB | — | 20,319 | 2022 |
| NFPA Firewise USA sites in good standing | 1.6 MB | small | 3,575 US / 1,717 CA | 2026 |
| Microsoft Building Footprints, California | 3.6 GB | see caveat 1 | ~11 M | **2021** |

Source of truth for CAL FIRE layers:
`https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/ArcGIS/rest/services`
Firewise: `https://services1.arcgis.com/0V03GIVRCAoxbtdR/.../Firewise_sites_In_Good_Standing_2024`

CAL FIRE publishes a **separate layer explicitly for real estate inspections**. Use that
one for AB 38 questions rather than deriving it from the SRA/LRA layers.

## API clients, no download (too large to mirror, or inherently per-request)

| Source | Client | Notes |
|---|---|---|
| US Census Geocoder | `sources/geocode.py` | Free, unlimited, no key. Address → lat/lon, county, incorporated place. |
| USGS 3DEP elevation | `sources/terrain.py` | 1 m. `slope_aspect()` = 9 point queries, no GDAL needed. |
| USGS 3DEP lidar tiles | `sources/terrain.py` | Tile discovery via TNM API. See caveat 3. |

## Not yet pulled, and why

| Source | Status | Reason |
|---|---|---|
| NAIP imagery | not pulled | USDA endpoint fails TLS against this machine's LibreSSL. Use AWS Open Data or Earth Engine instead. |
| LANDFIRE | not pulled | Async geoprocessing service, not a simple download. Build a job-submit client. |
| Canopy height | not pulled | Derive from 3DEP lidar (caveat 3) rather than licensing a raster. |
| TIGER / OSM roads | not pulled | Small and easy (12 MB for CA primary+secondary). Deferred, not blocked. |
| Fire Risk Reduction Communities | **no dataset exists** | Board of Forestry publishes a list, not a layer. Manual. Worth only $5.59/yr — low priority. |
| Wind climatology | not pulled | gridMET via Earth Engine. Needs an EE account (free). |

---

# Caveats — read before trusting any of this

### 1. The building footprints are from 2021, and California burned since
`California.geojson` is dated **2021-03-26**. The Palisades and Eaton fires destroyed
thousands of structures in January 2025. **This dataset will show buildings that no
longer exist**, in precisely the neighbourhoods most likely to use your product.

Distance-to-nearest-structure was supposed to be a high-confidence finding. On 2021
data in a burn scar it is confidently wrong.

Fix, verified available: **Overture Maps** buildings theme. Monthly releases merging
Microsoft + OSM + Esri, GeoParquet on S3, no key. Confirmed releases include
**2026-08-19** (two days old) at
`s3://overturemaps-us-west-2/release/2026-08-19.0/theme=buildings/`
versus Microsoft's 2021-03-26. Switch to Overture and keep Microsoft only as a gap
fallback. Do not ship the 2021 layer anywhere in LA County.

### 2. FHSZ is two layers and they do not overlap
SRA and LRA are separate datasets with different vintages (2024 vs March 2025) and must
both be queried. A point in an incorporated city returns nothing from the SRA layer —
that is correct, not a miss. `lookup.fhsz()` handles this; do not query one layer alone.

Verified behaviour: Pacific Palisades → Very High (LRA). Sierra Nevada → Very High (SRA).
Grass Valley city → nothing in SRA (it is LRA). Downtown Sacramento → nothing (correct).

### 3. Per-property lidar is ~1 GB, so it cannot be a per-request call
`terrain.lidar_tiles()` at a ~450 m radius returns 12–14 tiles totalling ~1 GB around a
Los Angeles address. That is fine as a **batch preprocessing step for a target area**,
and completely unviable inside a web request. Precompute a canopy height model for the
counties you serve, then query the raster.

Good news: 2025-vintage tiles exist for LA County, i.e. post-fire.

### 4. Firewise gives you points, not boundaries
NFPA publishes site centroids with a resident count, not polygons. You can say "there is
a Firewise site 200 m away", you cannot say "your address is inside one." Since this
drives a $46.49/yr insurance credit — more than any single property measure — confirm
with the homeowner rather than asserting it.

### 5. The Census geocoder misses addresses Google would find
Free and unlimited, but venue-style and new-construction addresses fail. In testing,
2 of 3 test addresses matched; the failure was a stadium, not a house. Budget a paid
fallback on no-match. Also note it returns `place: None` for unincorporated areas
(e.g. Altadena) — that is correct and load-bearing, because it routes Zone 0 Phase 2
timing to the county rather than a city.

### 6. Coordinate precision matters more than it looks
Point-in-polygon uses a degenerate bounding box. At `eps=1e-7` GDAL returned no
features; at `1e-6` (~10 cm) it works. Geocoder output is rooftop-or-interpolated —
an interpolated point can land across a zone boundary. For addresses near a boundary,
report the zone as uncertain rather than asserting it.

### 7. Everything here is a snapshot with no refresh mechanism
The LRA FHSZ map is dated March 2025 and CAL FIRE is still rolling out updates. Zone 0
regulations were adopted 2026-08-19 and their effective date is still pending. Re-pull
on a schedule and record `fetched_at` (the downloader already stamps it into `_meta`).

### 8. The Eaton Fire address returns no fire hazard zone at all
Verified: `2200 Fair Oaks Ave, Altadena` — inside the January 2025 Eaton Fire burn area —
returns **no FHSZ**, in neither the SRA nor the LRA layer, and nothing in the AB 38
real-estate layer either. Flat (2.2% slope), 84 buildings within 120 m.

This is not a bug in the pipeline. Altadena's flat suburban core was not mapped as a
high hazard zone, and it burned anyway, driven by wind-blown embers and
structure-to-structure spread rather than a wildland flame front.

Two consequences:
- **A product gated on FHSZ will tell Altadena homeowners they are not at risk.**
  Zone 0 and AB 38 genuinely do not apply to them. Compliance and safety diverge here
  in the most consequential possible way.
- It is direct evidence for the `E` (evidence) column existing separately from `R`.
  The structure-separation finding — 84 buildings within 120 m — is the signal that
  matters at this address, and no regulation reaches it.

### Verified end-to-end results (`sources/verify.py`)

| Address | FHSZ | Resp. area | Slope | Firewise ≤4 km | Bldgs ≤120 m |
|---|---|---|---|---|---|
| Pacific Palisades | Very High (LRA) | LRA | 19.5% | 5 | 16 |
| Altadena | none | LRA | 2.2% | 0 | 84 |
| Sacramento (control) | none | LRA | 0.5% | 0 | 10 |
| Grass Valley (Alta Sierra) | Very High (SRA) | SRA | 3.8% | 11 | 7 |

Runtime 13–25 s per address, dominated by the 9 sequential 3DEP elevation calls.
Parallelise those to get under 5 s.
