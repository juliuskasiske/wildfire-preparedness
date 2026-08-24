# Wildfire home-hardening: observable characteristics → recommendations

Working spec for the automated property assessment. Sources at the bottom.
Status: research draft, not yet validated against a real address sample.

---

## 1. Reframe: model ignition pathways, not "risk"

The research is consistent on one thing that changes the product design: **homes in
wildfires are overwhelmingly ignited by wind-blown embers landing on or near the
house, not by a wall of flame arriving from the wildland.** A house 500 m from any
vegetation still burns if an ember lands in a bark-mulch bed against a wood fence
that touches the siding.

There are exactly three exposures, and every measure maps to one or more:

| Exposure | What it is | Where it acts |
|---|---|---|
| **Embers (firebrands)** | Burning debris carried up to miles ahead of the fire | Vents, gutters, roof debris, decks, mulch, stored items |
| **Radiant heat** | Heat flux from nearby burning fuel, no contact | Windows, siding, eaves, adjacent structures |
| **Direct flame contact** | Fuel actually touching the house | Zone 0 vegetation, fences, decks, neighbour structures |

**Design implication:** the report should not be a single 0–100 risk number. It should
be three pathway scores plus a ranked action list. A single score invites the reader
to compare it to their insurance carrier's score (carriers already use Zesty.ai
Z-FIRE and Cape Analytics), and any mismatch destroys your credibility. Three pathway
scores plus concrete actions is defensible and more useful.

### Uncomfortable findings you should design around

1. **Defensible space matters less than people think, structure details matter more.**
   Syphard & Keeley, analysing 2013–2018 California fires, found vegetation clearance
   in the 0–30 m zone was a *poor* predictor of survival, while structural details
   – enclosed eaves, vent screen size, number of window panes – correlated strongly.
   Clearance beyond ~30 m added nothing, even on steep slopes.
2. **Structure-to-structure spread dominates in dense suburbs.** NIST's Camp Fire
   reconstruction and FEMA's Marshall Fire MAT report both found parcel-level
   pathways – wood fences acting as "wicks", mulch beds, neighbour structures at
   3–8 m – drove most losses. In a Palisades- or Altadena-density neighbourhood,
   distance-to-wildland is nearly irrelevant and distance-to-neighbour is everything.
3. **Combustibles compound.** NIST ran 187 experiments: a fence alone or mulch alone
   is a modest hazard, fence *plus* mulch at its base is dramatically worse, and two
   parallel fences less than 5 ft apart (back-to-back neighbour fences) is worse again.
   Your engine should score *combinations*, not independent features.

---

## 2. The measure catalogue, ordered by cost

Costs are Headwaters Economics / IBHS 2024, California union labour, installed
(materials + labour + demolition). Treat as order-of-magnitude for a report, not quotes.

### Tier 0 – free, this weekend ($0–150)

| Measure | Pathway | Cost | Evidence |
|---|---|---|---|
| Clear roof, valleys, gutters of needles and leaves | Ember | $0 | IBHS Base, CAL FIRE |
| Clear debris from deck surface and from *under* the deck | Ember | $0 | IBHS Base |
| Remove all combustibles from 0–5 ft: firewood, potted plants, doormats, furniture, trash cans, lawn tools | Flame | $0 | IBHS Base, Zone 0 draft |
| Move firewood stack to 30 ft from all structures | Flame | $0 | IBHS Base |
| Do not park vehicles / RV / boat within 5 ft of the house | Flame | $0 | IBHS Base |
| Remove vines from walls, pergolas and fences | Flame | $0 | IBHS Base |
| Cut grass to ≤4 in and keep it irrigated | Flame | $0 | IBHS Base |
| Remove dead vegetation and pruning piles | Flame | $0 | PRC 4291 Zone 1 |
| Move a movable propane tank to 30 ft (or ≥10 ft + shielded) | Flame | $0–150 | IBHS Base |

### Tier 1 – cheap, high leverage ($150–3,000)

| Measure | Pathway | Cost | Evidence |
|---|---|---|---|
| Replace bark/rubber mulch in 0–5 ft with pea gravel or pavers | Flame | ~$2,780 typical job; $464/CY gravel, +$100 weed barrier | IBHS Base, NIST fence/mulch |
| Cover existing vents with 1/8 in or finer corrosion-resistant metal mesh | Ember | $10–30 per vent DIY | IBHS Base, CBC Ch. 7A |
| Metal gutter guards | Ember | $4.48/LF (~$220 per 50 ft side) | IBHS Plus |
| Metal drip edge at roof edge | Ember | $2.93/LF | Headwaters |
| Metal flashing at deck-to-wall intersection | Flame | $2.74–4.14/LF | IBHS Base |
| Replace plastic dryer vent with metal, louvered | Ember | $69 ea | IBHS Plus |
| 6 in vertical noncombustible base at bottom of walls, and at deck posts | Flame | $6.67/SF | IBHS Base |
| Remove the 5–10 ft of wood fence where it meets the house, gate it in metal | Flame | ~$150 for a chain-link gate + demo | IBHS Base, NIST, FEMA Marshall |
| Fire-rated caulk on >1/8 in siding gaps and vent perimeters | Ember | $4.38/LF | Headwaters |
| Limb up trees to 6 ft, thin canopies to 10 ft spacing (5–30 ft zone) | Radiant | $300–1,500 arborist | IBHS Base, PRC 4291 |
| Replace combustible deck furniture with metal, remove rugs | Ember | $0–800 | IBHS Base |

### Tier 2 – meaningful project ($3,000–15,000)

| Measure | Pathway | Cost | Evidence |
|---|---|---|---|
| WUI-listed ember- and flame-resistant vents throughout | Ember | $53–106 ea eave/circular, $229 ea foundation, $421 ea gable | IBHS Base/Plus |
| Enclose open eaves with noncombustible soffit | Radiant | $4.51/SF, ~$4,000 typical | IBHS Plus |
| Metal gutter system replacing vinyl | Ember | $18.78/LF, ~$930 per side | IBHS Base |
| 1/8 in mesh skirting to enclose under-deck (decks ≤4 ft high) | Ember | $27.03/SF | IBHS Base |
| Metal grate replacing the first deck board against the wall | Ember | $104.13/LF | Headwaters |
| Noncombustible fence section, first 5–10 ft from the house | Flame | $60.44/SF; ~$9,670 both sides at 8 ft | Headwaters |
| Upgrade windows on the most exposed elevation to dual-pane tempered | Radiant | ~$755/window + $400–500 trim; $2,200–2,500 per short side | IBHS Plus, Syphard |
| Flat tempered-glass skylight replacing plastic dome | Ember | $1,435 ea | IBHS Plus |
| Metal kick plate on wood entry / garage door | Radiant | $120 / $266 | Headwaters |
| Bird stops at tile/metal roof edges | Ember | $20.26/SF | IBHS Base |

### Tier 3 – renovation-cycle ($15,000–100,000+)

| Measure | Pathway | Cost | Evidence |
|---|---|---|---|
| Replace wood shake/shingle roof with Class A | Ember | $4.96/SF composition ($496/square); $18.68/SF metal | IBHS Base, Headwaters "wood roofs are a $6B problem" |
| Replace combustible siding with fiber-cement / stucco / masonry | Radiant | $6.67/SF | IBHS Plus |
| Full noncombustible deck rebuild | Flame | $11.17/SF surface; >$9,000 for a typical steel deck | IBHS Plus |
| All exterior windows to multi-pane tempered | Radiant | ~$1,150–1,250 each | IBHS Plus |
| Exterior doors to metal/fiberglass with metal threshold | Radiant | $1,247–1,517 ea; sliders $2,681 metal / $9,819 fiberglass; garage $2,358–3,903 | IBHS Plus |

**Reference totals:** a minimal retrofit starts around **$2,000**; the "simple and
effective" ember-focused package IBHS and Headwaters both point to is **$10,000–15,000**;
a full retrofit of a 1,000 sq ft home ranges **$23,000–40,000** (good) to
**$60,000–100,000+** (premium assemblies).

---

## 3. Where the data actually comes from

The biggest mistake would be building this on Google satellite + Street View alone.
Roughly half of what you need is cheaper, more accurate and more reliable from
non-image sources, and a further chunk is only available from oblique aerial.

| Source | Cost | What it gives you | Reliability |
|---|---|---|---|
| **County assessor / parcel data** | Free–cheap | **Year built**, sq ft, stories, roof type sometimes, lot size | High |
| **CAL FIRE Fire Hazard Severity Zone** | Free | Moderate / High / Very High, SRA vs LRA | Authoritative |
| **USGS 3DEP lidar + DEM** | Free | Slope, aspect, slope position, **canopy height model**, building height | Very high where flown |
| **Microsoft / Google Open Buildings footprints** | Free | Exact footprint polygon, **distance to nearest structure**, parcel density | High |
| **NAIP 60 cm imagery** | Free | Land cover, canopy, gross ground cover | Medium |
| **Google Maps Static / Street View API** | ~$2–7 per 1,000 | Top-down and one street-facing elevation | Medium, see caveats |
| **Oblique aerial (Nearmap, EagleView, Vexcel)** | Paid, meaningful | 4 directions at ~7 cm — the only way to see vents, eaves, siding, deck skirting from above | High, this is what insurers use |
| **LANDFIRE / WUI layers** | Free | Fuel model, distance to wildland edge | Medium |

**The single highest-value non-image variable is year built.** California Building
Code Chapter 7A has applied to new construction in Very High FHSZ and State
Responsibility Areas since 2008. A 2015 house in a VHFHSZ almost certainly already
has a Class A roof, ember-resistant vents, ignition-resistant eaves and siding. If
you tell that owner to "install a Class A roof", your report is dead on arrival.
Use year built as a prior that **suppresses** structural recommendations and pushes
the report toward Zone 0 and landscaping, which is where those owners genuinely
still have gaps.

---

## 4. The detection matrix

Confidence key: **H** reliable enough to act on, **M** usable with a confidence
caveat in the report, **L** do not automate, ask in the survey instead.

### 4a. Computed from GIS, no vision model needed — do these first

| Variable | How | Conf | Triggers |
|---|---|---|---|
| Distance to nearest neighbouring structure | Footprint polygons, nearest-neighbour distance | H | <10 ft: structure-separation warning, prioritise wall/window/eave hardening on that elevation, back-to-back fence check. 10–30 ft: radiant-heat measures on that side |
| Structures within 30 ft on own parcel (shed, ADU, pergola) | Footprint + parcel polygon | H | Move to ≥30 ft, or 5 ft noncombustible buffer + 6 in base + 1/8 in mesh skirt each. Cap at 3 structures, 10 ft apart |
| Tree canopy overhanging the roof | Canopy height model ∩ roof polygon, or NDVI segmentation ∩ footprint buffer | **H** | Remove overhanging limbs, expect chronic gutter/valley debris → gutter guards |
| Canopy cover fraction in 0–5 ft / 5–30 ft / 30–100 ft rings | CHM in buffer rings around footprint | H | Zone-specific thinning and spacing recommendations |
| Ground slope and aspect | DEM | H | >20% slope: extend Zone 2 downslope, flag chimney/saddle position. South/west aspect: drier fuels |
| Slope position (canyon, mid-slope, ridge) | DEM terrain analysis | H | Narrative in report, drives radiant weighting |
| Distance to wildland edge / fuel type | LANDFIRE + WUI layer | H | Weights the direct-flame pathway. In dense suburbs this will be large and should *down*-weight vegetation advice |
| Driveway length and width, dead-end road | Road network + parcel | M | Access advice: 12 ft clear width, 13.5 ft vertical, turnaround for engines |
| Parcel density (structures per hectare) | Footprints | H | High density → switch report emphasis to structure-to-structure and fences |

### 4b. Top-down imagery (Google satellite / NAIP / orthophoto)

| Feature | Method | Conf | Recommendation triggered |
|---|---|---|---|
| **Roof covering class** (wood shake vs composition vs tile vs metal) | Texture + colour CNN on the roof polygon. Well-established in insurance CV | **H** for shake vs not | Wood shake → Class A replacement, the single biggest structural item ($4.96/SF+) |
| Roof debris / needle load | Segmentation on roof polygon; better as a *proxy* from canopy overhang | M | Clear roof and gutters; gutter guards |
| Roof complexity: number of planes, valley length, dormers | Roof-plane segmentation | H | Each valley and roof-to-wall intersection is a debris trap → maintenance frequency, drip edge, flashing |
| Skylight presence | Object detection, distinctive on roof plane | H | Check for plastic dome → flat tempered replacement |
| Solar panels | Object detection | H | Note: complicates roof replacement economics, mention in the report as a sequencing point |
| Deck / patio presence and footprint | Non-roof planar surface adjacent to footprint | M-H | Full deck branch of the tree (material, skirting, flashing, first-board grate) |
| Fence lines and topology | Linear feature detection; then intersect with buffer(footprint, 5 ft) | H for geometry, **L for material** | Fence touching house → replace first 5–10 ft with metal. Parallel fences <5 ft apart → back-to-back removal |
| Pool / water feature | Object detection | H | Positive signal, and a suppression source for pump-based recommendations |
| Ground cover in 0–5 ft ring | Segmentation in buffer ring | **L–M** | Eave overhang occludes the very ring you care about, and 5 ft ≈ 1.5 m is 5–10 px at Google's urban resolution. Do not assert Zone 0 compliance from overhead. Ask, or use street view |
| Stored items, firewood, RV | Object detection | L–M | Only when clearly visible in the open |
| Propane tank | Shape + shadow, distinctive in rural | M | Relocate to 30 ft or shield |

### 4c. Street View (front elevation only)

| Feature | Method | Conf | Recommendation triggered |
|---|---|---|---|
| Siding material class (stucco / fiber-cement / wood / vinyl / masonry) | Facade material classifier. Published macro-F1 0.91–0.96 on coarse classes, 0.60–0.82 on fine-grained | M-H coarse | Combustible siding → 6 in noncombustible base (cheap) now, full replacement at renovation |
| Open vs boxed eaves | Detection on the roof-wall junction | M | Open eave → enclose with noncombustible soffit (~$4,000) |
| Gable-end vent presence | Object detection | M | Mesh retrofit, or WUI-listed vent ($421 ea) |
| Foundation / crawlspace vents | Object detection | L-M, often occluded | Mesh retrofit ($229 ea if replaced) |
| Window pane count (single vs dual) | Very hard from street imagery | **L** | Ask in the survey |
| Gutter material (vinyl vs metal) | Colour/profile | L-M | Metal replacement |
| Front fence material and gate | Material classifier on the fence region | M-H | Metal near-house section |
| Mulch vs gravel in front beds | Colour/texture segmentation | M | Zone 0 conversion. Note it only tells you about the front |
| Vegetation touching the wall | Detection | M-H | Zone 0 removal |
| Address number visibility | OCR | M | 4 in reflective numbers, cheap, and it reads as expert advice |

**Street View caveats that will bite you:** the imagery is typically 1–7 years old
(a Palisades-area address may still show a house that no longer exists), it covers
one elevation only, it is routinely occluded by parked cars and hedges, and many
WUI properties in California are on private drives with no coverage at all. Budget
for a "we could not see enough" path in the UX — perhaps 20–35% of rural addresses.

### 4d. Not detectable from any imagery — these become your survey questions

This is actually the useful synthesis: **the features you cannot see are the survey.**
You need this data anyway, and asking for it is what makes the report accurate, so
the survey stops feeling like a toll and starts feeling like part of the service.

- Vent type: plain screen vs WUI-listed ember-resistant vent
- Window glazing: single, dual, tempered
- Roof underlayment and whether there are bird stops
- Deck substructure material and whether the underside is enclosed
- What is stored under the deck and in the 0–5 ft zone right now
- Attic and crawlspace access condition
- Whether the garage door has a bottom seal
- Water supply: well vs municipal, on-site tank, generator
- Insurance status, carrier, FAIR Plan, whether they have been non-renewed
- Whether they have done any hardening already, and what it cost
- Willingness to pay, and interest in an active/sprinkler system ← your actual research question

---

## 5. How to map characteristics to recommendations

Not a decision tree. A **rule table with gating and ranking** — a tree gets
unmaintainable at ~40 measures and forces mutually exclusive branches where you
actually want additive recommendations.

```
for each rule:
    if trigger_condition(detected_features, survey_answers) is TRUE
       and not suppressed_by(year_built_prior, detected_present, survey_says_done):
        emit(recommendation, priority)

priority = evidence_weight × pathway_exposure × detection_confidence / cost_band
```

- `evidence_weight` 1–3: 3 = IBHS Base requirement or a post-fire study finding,
  2 = IBHS Plus / code, 1 = plausible best practice.
- `pathway_exposure` 0–1: from the GIS layer. A dense-suburb parcel gets a high
  structure-to-structure weight and a low wildland-flame weight.
- `detection_confidence` 0–1: an L-confidence detection should never outrank an
  H-confidence one, and should be phrased as a question in the report
  ("we could not confirm your vent type — if they are plain screens, ...").
- `cost_band` 1–4 by tier above.

**Hard ordering rules that override the score:**

1. Zone 0 always appears first. It is free-to-cheap, it is the strongest consensus
   in the field, and it is about to be regulated.
2. Never emit a Tier 3 item without the Tier 0/1 items in the same pathway above it.
   "Replace your roof" as recommendation #1 is how you lose the reader.
3. Cap the report at ~8 recommendations, structured as
   **5 this weekend (free) → 2 this year → 1 at next renovation.**
   Completion rate on a 30-item list is zero.
4. Combination rules fire at elevated priority: wood fence + bark mulch at its base,
   or parallel fences <5 ft apart, or deck + stored items underneath.

### Suppression from year built (important)

| Year built | In VHFHSZ / SRA? | Suppress |
|---|---|---|
| ≥2008 | Yes | Roof class, vent type, eave enclosure, siding class recommendations — unless imagery contradicts |
| ≥2008 | No | Suppress nothing, Ch. 7A did not apply |
| 1990–2007 | Any | Suppress nothing, but soften roof language (many were re-roofed Class A) |
| <1990 | Any | Full structural branch active, wood shake probability is materially higher |

---

## 6. Three things to decide before building

**Sprinklers.** You should know what the evidence actually says before you put them
in the report. IBHS's 2024 white paper is deliberately cautious: exterior sprinklers
can pre-wet surfaces and quench embers *in optimal conditions*, but wind — which is
always present in a destructive wildfire — breaks droplets up and carries them away
from the intended coverage, and municipal pressure and grid power routinely fail
during these events. NFPA's Firewise fact sheet is similarly hedged. The "90% vs 50%
survival" figure circulating from the Palisades and Eaton fires is vendor-published,
not peer-reviewed, and has an obvious selection problem: the people who install
$20k sprinkler systems are the people who also hardened everything else.

So there is a real tension in your plan. Ordering the report by evidence puts
sprinklers well below gravel mulch and vent mesh. The lead magnet only works if the
report is credible, and a report that leads with the thing you happen to sell is
the fastest way to lose that. The version I'd suggest: keep the ranked list strictly
evidence-ordered, and put active defence in a clearly separated "active systems"
section afterward, with a plain disclosure that you have a commercial interest.
Then ask about sprinkler interest and willingness-to-pay **in the survey**, which is
what you actually wanted to learn. Undisclosed self-preferencing inside something
presented as a neutral assessment is also the kind of thing California's UCL is
written for. Your call, but make it deliberately.

**Liability framing.** A property-specific "risk assessment" tied to a named address
is close to territory occupied by licensed inspectors and insurance rating. Frame it
as educational, state that it is a remote screening and not a site inspection, do not
use language that mirrors an insurance score, and do not promise insurability
outcomes. Worth 20 minutes with a lawyer before launch, not after.

**Imagery terms.** Google's Maps Platform terms restrict caching, storing and
derivative processing of Street View and satellite tiles, including running models
over them and retaining results. Check this properly before you architect around it.
Nearmap, Vexcel and EagleView license aerial imagery specifically for this use case,
and their oblique product is the only thing that actually sees vents, eaves and deck
skirting from above. NAIP is public domain and unrestricted.

---

## 7. Suggested v1 scope

Build the GIS half first. Footprints + canopy height + DEM + assessor year built +
FHSZ gives you distance-to-neighbour, canopy overhang, Zone 0/1/2 vegetation, slope
and a code-era prior — all H-confidence, all free, no vision model, and it already
supports about 60% of the recommendation catalogue. Add one vision task: roof
material classification from top-down. Push everything else into the survey, which
is the thing you wanted to run anyway.

---

## Sources

- IBHS Wildfire Prepared Home, technical standard and How-To checklist (Base/Essential and Plus/Enhanced requirements, 5 ft noncombustible zone, vent mesh, deck, fence and structure spacing rules). Detailed checklist used here is the Aug 2023 edition; standard updated June 2025 and again June 2026 – see B.5.
- Headwaters Economics and IBHS, "Retrofitting a Home for Wildfire Resistance: Costs and Considerations", 2024 — all per-measure cost figures above.
- Syphard & Keeley, "Factors Associated with Structure Loss in the 2013–2018 California Wildfires", Fire 2(3):49; and "The role of defensible space for residential structure protection during wildfires".
- NIST, 187-experiment study on combustible fences and mulch, 2022; NIST Camp Fire reconstruction and parcel-vulnerability programme.
- FEMA Marshall Fire Mitigation Assessment Team report, 2025 — wood fences as wicks.
- California Board of Forestry and Fire Protection, Zone 0 draft regulations (AB 3074), still in draft as of mid-2026, phased implementation up to 5 years.
- PRC 4291 and CAL FIRE Zones 0/1/2; California Building Code Chapter 7A, applicable to new WUI construction since 2008.
- IBHS, "External Sprinkler Systems for Wildfire Defense" white paper, 2024; NFPA Firewise exterior sprinklers fact sheet.
- Facade material classification accuracy: OpenFACADES and related street-view attribute extraction literature.

---

## Appendix A: The incumbent scoring vendors, and what is publicly available

### Availability, short version

Neither Z-FIRE nor Cape is available to you or to a consumer. Both are B2B data
products sold under enterprise contract to insurance carriers, MGAs, reinsurers and
increasingly real-estate platforms. Neither publishes pricing. Neither has a
homeowner-facing product. There is no self-serve API tier for either.

| Vendor | Status | Who can buy | Consumer access |
|---|---|---|---|
| **ZestyAI (Z-FIRE)** | Independent, private. Reported cash-flow positive, 26 new carrier customers in the last cycle | Carriers, MGAs, reinsurers, via demo/contract. Platform at zview.zesty.ai | None |
| **Cape Analytics** | Acquired by **Moody's**, announced January 2025 | Carriers, MGAs, real estate. aPCR delivered via API or PDF | None |
| **Faura** | Independent, ~$4M raised. Closest analogue to your idea | Insurers and agents, but ships a **policyholder self-inspection tool** | Indirect, through the insurer |
| **First Street (Fire Factor)** | Nonprofit-derived, now commercial | Bulk data licence | **Free at riskfactor.com**, and embedded in Redfin and Realtor.com listings |
| Verisk FireLine, CoreLogic | Legacy hazard scores | Carriers | None |

### Z-FIRE methodology

- Two-level output. **Level 1, exposure:** likelihood the structure falls inside a
  future fire perimeter — vegetation, slope, elevation, WUI proximity, historical
  burn patterns, regional climatology. **Level 2, structure vulnerability:**
  likelihood of damage given a nearby fire — building materials, defensible space,
  surrounding fuels, extracted by computer vision.
- Inputs: high-resolution **aerial and oblique** imagery (not Street View), permit
  data for roof age, tax assessor records, topography, hydrology, climatology.
  Claims ~97% US property coverage at parcel level.
- Trained against **more than 2,000 historical wildfires** and millions of actual
  insurance claims, explicitly not simulation-based.
- Architecture: **gradient boosted machines**, chosen for non-linear interactions
  plus explainability via feature importance and SHAP values — which matters because
  regulators demand it.
- Explicitly models ember-driven and wind-driven urban conflagration, not just
  wildland flame front. Same conclusion as section 1 of this document.
- Regulatory: filing-ready in California under the CDI's pre-application required
  information determination (PRID) process, so carriers can use it in rate
  segmentation and underwriting without additional model review.

### Cape Analytics methodology

- Computer vision over high-resolution aerial imagery, ~100M+ US properties,
  monitored over time for change (new construction, alterations).
- Extracts: roof condition (discolouration, wear, patching, debris), imagery-derived
  roof age, roof material and geometry, yard debris, vegetation density and
  proximity, solar panels, living-area square footage, quality grade, and structure
  separation distance.
- Packaged as an Automated Property Condition Report (aPCR) via API or PDF, plus
  peril-specific scores for wildfire, hail and wind that blend hazard, vulnerability
  and weather.

### First Street Fire Factor — the free consumer benchmark you will be compared to

Free, 1–10 score, per address, at riskfactor.com and syndicated onto Redfin and
Realtor.com. Built from fuels, fire weather (NOAA), human influence and fire spread
modelling, projected 30 years forward under climate scenarios. It does include some
building characteristics — slope, **exterior wall type**, and defensible space —
derived from historical loss data.

**But its structure vulnerability layer is thin.** Three variables. No vents, no
eaves, no roof class, no deck, no fence, no Zone 0 detail, no actionable list.
That gap is your product. Your positioning is not "here is a score" — First Street
already gives that away free and is embedded in the listing sites. Your positioning
is **"here is what specifically on your property is wrong, and what it costs to fix."**

### Faura is the closest thing to your idea, and it is instructive

Founded 2023, ~$4M raised, partnered with Insurity, expanded to all five NATCAT
perils. It builds structure-level resilience models with **tailored mitigation plans**,
and it ships a policyholder self-inspection tool so homeowners can self-report
mitigation and qualify for discounts and grants. It sells to insurers, not consumers.

Two readings. Negative: the concept is validated and funded, and the natural buyer
is the insurer, not the homeowner. Positive: nobody is doing the direct-to-homeowner
version well, and you are not actually trying to build a durable assessment business —
you want a survey panel. Faura's existence is evidence the assessment is credible
enough to be worth an email address.

---

## Appendix B: "Safer from Wildfires" — the hook you are missing

This is the single most useful thing found in this round, and it should probably
restructure your landing page.

California Code of Regulations Title 10, §2644.9, effective October 2022, requires
any insurer that prices wildfire risk to:

1. **Give a discount for each of a defined list of mitigation actions**, filed
   separately, so credits **stack**.
2. **Disclose the property's wildfire risk score** to the homeowner — at
   application, before renewal or non-renewal, and any time the homeowner completes
   a mitigation measure and asks.
3. **Explain the score**, including how to lower it and how much it would save.
4. Honour a **right of appeal** if the homeowner believes the score is wrong,
   with escalation to CDI at 800-927-4357 if the appeal is denied.

AB 1, the Insurance and Wildfire Safety Act, effective 1 January 2026, requires CDI
to periodically review and update these regulations.

The defined list, verbatim from the CDI FAQ:

**Structure level**
- Class A fire-rated roof
- Noncombustible 6 inches at the bottom of walls
- Ember- and fire-resistant vents
- Double pane windows or added shutters
- Enclosed eaves

**Immediate surroundings**
- 5-foot ember-resistant zone around the structure
- Cleared vegetation and debris from under decks
- Move sheds and outbuildings at least 30 feet away
- Trim trees and remove brush in compliance with state and local defensible space laws

**Community level**
- Form a Firewise USA site (NFPA)
- Become a Fire Risk Reduction Community (Board of Forestry)

### Why this matters for the product

- **It is an authoritative, closed, 9-item property-level list** that maps almost
  one-to-one onto the matrix in section 4. Anchor the report to it and every
  recommendation carries an implicit "and this is legally required to earn you a
  discount."
- **It converts the offer, but not via the discount** – see B.1 below, the discounts
  are economically trivial. The hook is the **transparency and appeal right**, and the
  fact that mitigation affects whether you can get private coverage at all. That still
  targets the large population of California homeowners who have been non-renewed or
  pushed onto the FAIR Plan.
- **It gives the report a call to action that is not a purchase:** request your risk
  score from your carrier, and appeal it if you have done the work. That builds
  trust, which is what makes people answer the survey honestly.
- **It gives you a second survey axis worth more than the first:** insurance status,
  carrier, non-renewal history, FAIR Plan, whether they have ever requested their
  score or a mitigation discount. That is the segmentation that tells you who will
  actually pay for a sprinkler system.

Caveat to verify before using in copy: discount amounts vary by carrier, are filed
individually, and CDI does not publish a schedule. Do not promise a percentage.

### B.1 What the discounts are actually worth — do not build the pitch on them

Source: Ludington, Liao & Walls, "From Risk to Reward: Insurance Discounts for
Wildfire Mitigation", Resources for the Future Working Paper 25-30, December 2025.
They collected the filed discount schedules of the 25 insurers in California's top 18
groups and computed market-share-weighted averages. Note it is a working paper, not
yet peer reviewed.

**Average discount per measure, and what it is worth in dollars per year:**

| Measure | % (full premium) | $ (full premium) | $ (wildfire portion only) |
|---|---|---|---|
| Class A fire-rated roof | 1.88% | **$31.38** | $7.61 |
| 5-ft clearance | 0.84% | $13.98 | $4.70 |
| Local ordinance compliance | 0.56% | $10.15 | $6.90 |
| 5-ft noncombustible material | 0.54% | $9.05 | $4.70 |
| Multi-pane windows | 0.32% | $7.04 | $4.98 |
| Fire-resistant vents | 0.30% | $5.59 | $5.33 |
| 30-ft noncombustible structure | 0.31% | $5.83 | $5.07 |
| Enclosed eaves | 0.30% | $5.10 | $4.21 |
| Vertical clearance (6 in base) | 0.30% | $5.10 | $4.02 |
| Under-deck clearance | 0.30% | $5.10 | $4.70 |
| **All property-level measures combined** | **5.65%** | **$98.33** | **$54.07** |
| IBHS Wildfire Prepared Home (Base) | 3.84% | $56.87 | $61.67 |
| **IBHS Wildfire Prepared Home Plus** | **6.33%** | **$94.80** | $93.65 |
| Firewise USA community | 2.86% | **$46.49** | $31.52 |
| FRR community | 0.30% | $5.59 | $4.46 |
| **Maximum, property + community** | **13.15%** | **$215.78** | $101.52 |

**The implications are blunt:**

1. **Doing every single property-level mitigation earns about $98/year**, or $54 if
   your insurer discounts only the wildfire portion of the premium (most do). Against
   a $10,000–15,000 retrofit that is a 100-plus year payback. The discount cannot
   carry the pitch and you should not imply that it can.
2. **Firewise community membership ($46) is worth more than any single property-level
   action.** Joining the neighbours beats hardening your own vents on the discount
   math. Good, cheap, credible line for the report.
3. **IBHS Plus certification ($94.80) is worth roughly the same as doing every
   individual measure**, because nine insurers key their discounts off IBHS rather
   than off the item list. The certification, not the work, is what gets paid.
4. **Insurers give a flat ~0.3% to eaves, vents, windows and vertical clearance
   alike**, regardless of actual effectiveness. RFF attributes this directly to the
   knowledge gap: nobody has good per-measure expected-loss data for wildfire, unlike
   FORTIFIED for wind. That gap is, incidentally, an argument for why your dataset
   could have real value to someone.
5. **Three insurers simply stopped using wildfire risk in rating** to avoid the
   obligation, so over 500,000 California policies get no discount at all. Never
   promise a homeowner a discount.
6. RFF's own conclusion is that at current magnitudes the discounts likely function
   "more as a transfer to those who have already mitigated rather than as a strong
   incentive for new investment."

### B.2 What actually motivates the homeowner, in rank order

1. **Coverage availability.** Being non-renewed, or getting off the FAIR Plan and
   back into the private market, is worth thousands per year. Mitigation and IBHS
   certification are increasingly what makes a carrier willing to write the risk at
   all. This dwarfs the discount.
2. **Grants.** The **California Safe Homes** grant programme launched 1 January 2026
   for low- and moderate-income homeowners in high-risk areas, funding new roofs and
   defensible space, with applications expected to open in spring 2026. Separately
   the FEMA/Cal OES **California Wildfire Mitigation Program** funds community-scale
   home hardening, currently piloting in Whitmore (Shasta), Dulzura (San Diego) and
   Kelseyville-Riviera (Lake), with Tuolumne and El Dorado under consideration. Verify
   current status and eligibility before putting either in copy.
3. **The transparency and appeal right.** Most homeowners do not know their insurer
   must hand over their wildfire risk score, explain how to lower it, say what it
   would save, and accept an appeal. Telling them this is a genuine, free, useful
   service and costs you nothing.
4. **Not losing the house.** Emotional, and the strongest driver after a bad fire
   season, but it decays fast with time since the last fire.
5. The premium discount, a distant fifth.

**Landing page implication:** lead with 2 and 3, not with the discount. "Find out
your home's wildfire vulnerabilities, which grants you may qualify for, and how to
make your insurer show you their risk score" is honest, differentiated from the free
First Street score, and does not depend on a number you cannot control.

### B.3 Provenance and payback arithmetic

**Where the discount numbers come from.** All percentages and dollar figures in B.1
are Tables 3 and 4 of Ludington, Liao & Walls, RFF Working Paper 25-30 (Dec 2025).
Their method, from the paper's Appendix B:

- They collected **96 rate and rule filings**, mostly Jan 2022 – Aug 2025, from the
  CDI's public **WARFF** and **SERFF** filing systems.
- Covering **25 insurers in the top 18 groups**, roughly 90% of the California
  admitted market, plus the FAIR Plan separately.
- From each filing they extracted base rates and the itemised discount percentages.
  All insurers file discounts as percentages, so Table 3 is read more or less directly
  off the filings, then market-share weighted.
- **The dollar conversion (Table 4) is theirs, and it is an estimate.** Average
  premium = statewide earned premium over earned exposure, 2023 CDI data. For
  full-premium insurers they multiply each insurer's percentage by that insurer's
  average premium and weight by market share. For insurers that discount only the
  wildfire slice, they first estimate a "wildfire component" from the per-peril base
  rates in the filing, which they explicitly flag as rough because wildfire premiums
  do not scale proportionally from base rates.

**You cannot reproduce Table 4 with one multiplication.** Back-solving each row gives
implied average premiums from **$1,626 to $2,200, mean ~$1,767**, because each row is
weighted across a different subset of insurers. Treat the dollar figures as
order-of-magnitude, not precise.

Premiums also scale with risk and home value: the highest-risk quintile of ZIP codes
averages **$2,145** vs **$1,120** in the lowest. So in a high-risk ZIP the all-nine
discount is roughly 5.65% x $2,145 = **$121/yr**, and property-plus-community
13.15% x $2,145 = **$282/yr**. Still not close to material against retrofit cost.

**Payback, the nine measures.** Costs from Headwaters' reference home (40 x 25 ft,
1,000 sq ft, 130 LF perimeter). Cheap-compliant column takes the lowest option the
regulation permits (mesh over existing vents, shutters instead of new windows).

| Measure | Cheap-compliant | Full-quality |
|---|---:|---:|
| Class A roof | $6,300 | $6,300 |
| 6 in noncombustible base | $434 | $434 |
| Ember-resistant vents | $300 | $2,458 |
| Dual-pane windows **or** shutters | $2,807 | $12,055 |
| Enclosed eaves | $4,000 | $4,000 |
| 5 ft ember-resistant zone | $2,782 | $2,782 |
| Clear under decks | $0 | $1,081 |
| Sheds 30 ft away | $0 | $2,000 |
| Defensible space (already required by PRC 4291) | $0 | $600 |
| **Total** | **$16,622** | **$31,709** |

- Against $98.33/yr (full-premium insurer): **169 to 322 years**.
- Against $54.07/yr (wildfire-portion insurer): **307 to 586 years**.

**Payback, IBHS Plus.** IBHS Plus on an existing home is effectively a full retrofit,
Headwaters' "Better" to "Best" band, $40,000–100,000, plus $125 application, plus an
annual review ($25 self, $100 third-party), plus recertification every 3 years.

- $40,000 → **422 years**. $100,000 → **1,055 years**.
- The **$100 third-party annual review costs more than the $94.80 discount**. Net
  −$5.20/yr. At the $25 self-review it nets $69.80/yr.
- Most insurers apply the IBHS discount **in lieu of** the individual item discounts,
  not on top. So for a full-premium insurer, **IBHS Plus is worth $3.53/yr LESS than
  simply doing all nine items and self-reporting them**. For a wildfire-portion
  insurer it is $39.58/yr better.

**Conclusion: IBHS certification is not justifiable on discount economics at all.**
Its value is that nine insurers recognise it, and that it is becoming a de facto
underwriting credential for getting covered. Sell it as insurability, never as savings.

### B.4 The one genuinely free win, and the best ROI on the board

**Unclaimed discounts.** A typical post-1990 California home already has a Class A
roof and dual-pane windows. That is **$38.42/yr of discount it already qualifies for,
at zero additional spend** – and most owners have never asked for it. The remaining
seven items would cost ~$7,516 for another $59.91/yr, a 125-year payback, so the
advice is: claim what you already have, and do the rest for survival reasons, not
financial ones.

This is a strong, honest, concrete deliverable for the report: *"based on what we can
see, you already qualify for roughly $X of mitigation discount. Here is how to ask
your insurer for it, and here is your right to see and appeal your risk score."*
It costs the homeowner nothing, it is verifiable, and it buys the trust you need
before asking survey questions about spending money.

**Firewise USA is the best return available anywhere in this system:** $46.49/yr,
more than any single property-level action, for essentially no homeowner spend beyond
organising the neighbours. Put it in every report.

### B.5 IBHS Wildfire Prepared Home – current program facts (checked Aug 2026)

IBHS is the **insurance industry's own research lab** – funded by carriers, it runs a
full-scale test chamber where it burns real houses under controlled ember and wind
conditions. That is why insurers trust its standard and why nine of them key their
discounts to it. It is not a government programme and it is not a code.

| | |
|---|---|
| Levels | **Essential** (was "Base") and **Enhanced** (was "Plus"). Both names are still in circulation, renamed in the June 2026 update |
| States | 14: AZ, CA, CO, FL, ID, MT, NV, NM, OK, OR, TX, UT, WA, WY (expanded well beyond the original CA/OR) |
| Eligible | Homeowner must apply. Single-family detached, 3 stories or fewer. No townhomes or condos – those now fall under the separate **Wildfire Prepared Multifamily** standard |
| Fee | **$125 non-refundable application fee**, and not every home is eligible |
| Process | Homeowner does the work → pays and submits photos of all four sides → IBHS QA review for eligibility → third-party evaluator visits → QA review → certificate |
| Validity | 3 years, with **annual photo reviews at year 1 and year 2**, then reapply |
| Recent additions | **Wildfire Prepared Neighborhood** (piloted with KB Home in CA) and **Wildfire Prepared Multifamily**, both June 2026 |
| June 2026 changes to Home | Easier tree and shrub spacing/trimming/placement rules, clearer deck and attached-structure requirements |
| June 2025 changes | Clarified flame- and ember-resistant vents and the 0–5 ft noncombustible zone |

**Verify before use in copy:** the 2023 checklist listed annual review fees of $25
(self) and $100 (third-party). The current About page describes annual photo reviews
without stating a fee. The B.3 conclusion that the third-party review fee can exceed
the discount depends on that $100 still being current – confirm it before repeating.

**The eligibility trap, which is the important part for your product.** The 0–5 ft
noncombustible zone is the gate, and IBHS applies it strictly: all vegetation, grass,
artificial turf, wood or rubber mulch, wood or vinyl fencing, overhanging branches
and stored items gone, down to bare dirt or hardscape, and the zone extends upward to
the sky. IBHS itself warns that **protected trees may disqualify a home outright**,
and that setbacks can force homeowners to negotiate with a neighbour to clear the
5 ft on a shared boundary. Many California suburban lots simply cannot pass without
removing a tree they are not legally allowed to remove.

That matters to you in two ways. It is a real, concrete, disqualifying constraint
your assessment can detect from imagery – **canopy overhang within 5 ft of the wall
is one of your highest-confidence detections** – so you can tell someone early
whether certification is even open to them. And "can I actually get certified?" is a
much sharper survey question than "would you spend money on wildfire safety?"

---

## Appendix C: Regulatory triggers and candidate value-adds

### C.1 Zone 0 is now adopted, and it is much weaker than IBHS

**On 19 August 2026 the Board of Forestry approved the final Zone 0 rule, 8-0.**
Source: BOF August 2026 rule package, plus Insurance Journal and SF Chronicle
coverage. Applies to **State Responsibility Areas (PRC 4291) and Very High FHSZ
within Local Responsibility Areas (Gov. Code 51182)** – roughly **2 million homes**.

**Do not model this as the IBHS 5-foot rule. It is not.** The original proposal was a
fully noncombustible 5 ft perimeter. What passed is far softer:

| | Requirement |
|---|---|
| **"Safety zone"** | Noncombustible, vegetation-free. Width **flexes with the eave**: 12 in eaves → 12 in zone, 36 in eaves → 36 in zone. **Minimum 1 ft.** Where eaves are shallow: also within 2 ft of windows, doors and vents, and 5 ft of attached decks |
| **Rest of Zone 0** | "Low-combustibility", not bare. **Herbaceous plants and flowers allowed** in spaced groupings (bulbs, impatiens, begonias, petunias, poppies, yarrow, non-thatching succulents), low ground covers (blue-star creeper, beach strawberry, creeping thyme, mosses), **mowed lawn at ≤3 in**, potted plants in noncombustible pots ≤1.5 ft and moveable |
| **Trees** | **Existing trees may stay.** Maintenance only: dead wood out (immediate), branches 10 ft from chimneys and clear of eaves (immediate), branches trimmed 5 ft above roofs, ladder fuels removed from the bottom 6 ft (large trees) or lower third (small trees). Local inspector judges per tree. **No new trees planted in Zone 0** from the effective date |
| **Banned outright** | Combustible mulch, woodchips, fallen leaves and needles, firewood and stored wood in Zone 0, on roofs, or in gutters |
| **Fences and gates** | **5 ft noncombustible section where a fence attaches to the home** (Phase 2). No new combustible fences or gates in Zone 0. Repairs to existing permitted |
| **Sheds/outbuildings** | Those within Zone 0 need noncombustible roofs and walls |

**Timeline:**
- **New construction: September 2026.**
- **Immediately on effective date, existing homes:** roof and gutter debris cleared,
  dead wood removed, branches 10 ft from chimneys, no new tree planting in Zone 0.
- **Phase 1, within 3 years:** remove combustible items (firewood, mulch, woodchips,
  dead leaves and branches), remove dead/dying plants, trim trees, adjust to
  allowable vegetation in the low-combustibility area.
- **Phase 2, within 5 years,** timeline set by the local jurisdiction: the under-eave
  safety zone, replacing combustible gates, shed and fence adjustments.

**Local variation:** local fire agencies in LRAs may authorise alternative practices
with "substantially similar practical effect", and local governments may adopt
**stricter** standards. So compliance is jurisdiction-dependent, not one national rule.

**Criticism, worth knowing:** fire scientists and a Central Marin battalion chief
publicly objected that the science supports a fully noncombustible 5 ft zone, and the
insurance industry framed the rule as "a minimum standard, not the highest level of
wildfire protection." **Product implication: Zone 0 compliance and actually being
safe are now two different things, and your report can honestly say so.** That is a
genuine, defensible differentiator against a pure compliance checker.

**Procedural caveat to verify:** the Board's 8-0 vote approved the final rule text.
Confirm the Office of Administrative Law step and the exact effective date before
putting a countdown clock in the product.

### C.2 AB 38 – the sharpest hook available, and previously missed

California AB 38, in force since 1 July 2021, with a significant expansion on
**1 July 2025**:

- A seller of a home in a **High or Very High FHSZ** must give the buyer
  **documentation of a compliant defensible space inspection before close of escrow**,
  completed within 6 months of the sales contract. If unavailable, buyer and seller
  may agree in writing that the buyer obtains it within 1 year of closing.
- **Since 1 July 2025**, the seller must additionally disclose whether they completed
  any of **12 specific low-cost fire-hardening retrofits** from the **State Fire
  Marshal's Low-Cost Retrofit List** during their ownership. Examples include bird
  stops blocking the gap between roof covering and sheathing, and noncombustible
  gutter covers.
- Applies to **residential property of 1–4 units built before 1 January 2010** in
  High or Very High FHSZ.
- It is a **disclosure and documentation** duty, not a retrofit mandate.

**Why this is the strongest hook in the entire landscape:**

1. It is **already law**, not phased or pending.
2. It has a **hard deadline** – close of escrow – rather than a five-year horizon.
3. It attaches to a moment when the homeowner **has budget and is paying attention**.
4. The trigger population is **precisely definable from data you already need**:
   FHSZ class + assessor year built + unit count. You can tell someone they are
   subject to it before they know it themselves.
5. Failure has transactional consequences, which is a much sharper motivator than
   a $98 discount or a distant fire.

**Verify before building copy:** get the current 12-item Low-Cost Retrofit List from
the Office of the State Fire Marshal directly, not from a vendor blog.

### C.3 Candidate value-adds, ranked

Scored on hook strength, how automatable it is, and what it costs you to deliver.

**Tier 1 – build these**

| Value-add | Why | Data needed |
|---|---|---|
| **AB 38 transaction readiness** | Legal duty, hard deadline, budget present. "Are you selling in the next 12 months? You will need this." | FHSZ + year built + units |
| **Zone 0 phase-in clock, personalised** | ~2M homes, now real, dated deadlines. "Your Phase 1 items, your Phase 2 items, your jurisdiction's timeline." | FHSZ/SRA + imagery + geocoded jurisdiction |
| **Unclaimed discount audit + risk-score demand letter** | Free to deliver, high perceived value. Pre-written letter invoking §2644.9 so they can demand their score. **And it gives them a reason to come back to you with the score** | Detected features + survey |
| **Insurability / FAIR Plan exit assessment** | Worth thousands, unlike the discount | Survey (carrier, non-renewal) + gap list |
| **Grant eligibility screen** | California Safe Homes (Jan 2026, low/moderate income in high-risk areas), FEMA/Cal OES CWMP pilot communities, local FSC grants | FHSZ + county + income proxy |

**Tier 2 – cheap differentiators nobody else offers**

| Value-add | Why |
|---|---|
| **Ember exposure direction** | Santa Ana / Diablo wind direction plus terrain → "prioritise your north-east elevation." Computable, novel, reads as genuine expertise |
| **Access and evacuation check** | Driveway width and length, turnaround, dead-end road, second egress, address-number visibility. Computable from road network and Street View OCR. Almost nobody offers it and it feels like an expert visited |
| **Structure-separation reality check** | "Your nearest neighbouring structure is 12 ft away. That is your single largest driver and you cannot fix it alone." Honest, and leads naturally to Firewise |
| **Firewise USA starter** | $46.49/yr, more than any single property action, near-zero cost. **And it is inherently viral** – neighbourhood organising brings you more addresses and more survey responses |
| **"Would you pass a defensible space inspection?"** | PRC 4291 is law **today** and CAL FIRE inspects. Stronger compliance framing than Zone 0's five-year horizon |
| **Compliance vs. actually safe** | Given the rule was weakened, show both: "here is the legal minimum, here is what the science says." Differentiates you from a pure compliance checker |

**Tier 3 – retention, which is what you actually need for a survey panel**

- **Seasonal maintenance calendar** with pre-fire-season reminders. Keeps the list warm.
- **Product specification sheet:** exact mesh size, ASTM E2886, what to say to a contractor. Stops people buying the wrong thing, builds trust cheaply.
- **Re-scan on imagery refresh:** "new aerial imagery of your property, here is what changed."
- **Local ordinance overlay:** many jurisdictions are stricter than the state.

**Tier 4 – think hard before doing**

- **Contractor referral.** Monetisable, but it is the same neutrality problem as the sprinklers. Once the report routes to paid vendors, it stops being an assessment.
- **Neighbour comparison** ("your Zone 0 is worse than 70% of your street"). Behaviourally powerful, computable at scale, but privacy-sensitive and can anger people.

### C.4 What this means for product structure

These are not parallel features. They are **different front doors to one engine.**

Build the assessment pipeline and report generator once. Then run several landing
pages against it – AB 38 for sellers, Zone 0 clock for SRA/VHFHSZ owners, insurability
for the non-renewed, grants for low/moderate income. **Which door someone walks
through is itself research data** about what motivates California homeowners, which
is exactly the question you set out to answer.

Routing needs only three or four questions asked **before** the report:

| Question | Routes to |
|---|---|
| Selling in the next 12 months? | AB 38 readiness |
| Current insurer, and have you been non-renewed? | Insurability, FAIR Plan exit |
| Have you ever asked your insurer for your wildfire risk score? | Discount audit, demand letter |
| Household income band (optional) | Grant screen |

Those double as survey questions. The routing is the survey, and the survey is the
routing – which is the cleanest possible resolution of the tension in the original
plan, where the survey was a toll the user paid for the report.

---

## Appendix D: The formal model, reviewed

Reviewing the proposed R / a / c decomposition. The shape is right. Seven changes.

### D.1 `a` cannot be binary. Three states, plus confidence.

This is the most important change. Adoption evidence ranges from near-certain to
completely unobservable, and a binary vector throws that away and produces
confidently wrong advice ("install a Class A roof" to someone who has one).

```
a[m] ∈ {ADOPTED, NOT_ADOPTED, UNKNOWN}
conf[m] ∈ [0,1]
source[m] ∈ {GIS, AERIAL_CV, STREETVIEW_CV, ASSESSOR_PRIOR, SURVEY, USER_CONFIRMED}
```

**UNKNOWN must be a first-class output state**, not a default to NOT_ADOPTED. It is
what drives the survey questions, and it drives the report's language: "we could not
confirm your vent type from imagery. If they are plain screens rather than
WUI-listed vents, this is your cheapest high-value fix."

Rule: a low-confidence detection may never outrank a high-confidence one in the
ranked output, and anything below a confidence threshold is phrased conditionally.

### D.2 `c = R * a` measures the wrong thing. You want the gap.

`R * a` gives requirements already satisfied. The report is built from the inverse:

```
g = R ⊙ (a == NOT_ADOPTED)      # gaps: required and not done -> the action list
e = R_savings ⊙ (a == ADOPTED)  # entitlements: done but probably unclaimed
u = R ⊙ (a == UNKNOWN)          # unresolved: drives survey + conditional language
```

**`e` is a distinct and valuable output you do not currently have.** The typical
post-1990 home already qualifies for roughly $38/yr of discount nobody has claimed.
That is a free, verifiable win that costs the homeowner nothing, and it is the single
best trust-builder in the report. It comes from `a == ADOPTED`, not from a gap.

Also note R is a matrix and a is a vector, so the products broadcast down columns.
That is fine and desirable: you get a gap set **per regime**, which maps one-to-one
onto your five customer questions.

### D.3 R cells are not Yes/No. They are dated, parameterised and jurisdictional.

Your Zone 0 column already anticipates this with "required after date X". It needs to
go further, and it applies to more than Zone 0.

```
R[m][regime] = {
  status: REQUIRED | DISCLOSE_ONLY | VOLUNTARY_CREDIT | RECOMMENDED | NOT_APPLICABLE,
  effective_date: date | null,      # null = already in force
  set_by: STATE | LOCAL_JURISDICTION,
  parameter: {...} | null           # the requirement itself varies by property
}
```

Zone 0 is the proof that `parameter` is necessary: the noncombustible safety zone
**flexes with eave width** – 12 in eaves means 12 in, 36 in eaves means 36 in,
minimum 1 ft. The requirement is a function of a physical property attribute. So
**physical attributes feed R, not only `a`.** That is easy to miss.

Zone 0 also has three distinct effective dates (immediate items, Phase 1 at 3 years,
Phase 2 at up to 5 years with the local jurisdiction choosing), and local agencies may
be stricter or authorise substantially-equivalent alternatives. So `effective_date`
is partly unresolvable from state data alone. Where it is unknown, say so.

### D.4 AB 38 is two different columns, and one of them is not a requirement.

Splitting it matters because the customer message is completely different.

| Column | What it is | Message to homeowner |
|---|---|---|
| **AB38-DS** | Documented PRC 4291 defensible space inspection before close of escrow | "You must do this to sell" |
| **AB38-DISC** | Disclose which of the 12 State Fire Marshal low-cost retrofits you completed | "You will have to tell a buyer you did not do this" |

The second is a **disclosure duty, not an adoption duty**. A seller who did nothing
and says so is fully compliant. Modelling it as REQUIRED overstates the obligation
and would be a false claim in the report. Modelled correctly as DISCLOSE_ONLY it is
still motivating, just honestly so.

### D.5 Savings are not a per-measure column that sums.

Three reasons a simple additive savings column will be wrong:

1. **Most insurers apply the IBHS discount in lieu of the individual item discounts,
   not on top.** So total is roughly `max(Σ individual, IBHS_bundle)`, not a sum.
2. Carriers stack **additively or multiplicatively** depending on the filing, and
   several apply caps or multi-action bonuses.
3. **Three insurers give no discount at all** (they removed wildfire from rating),
   covering 500,000+ policies. And six discount the whole premium while the rest
   discount only the wildfire portion, which roughly halves the dollar value.

So model savings as a function, not a column:

```
savings(measure_set, carrier, premium) -> {low, point, high}
```

with carrier from the survey and premium from ZIP-level CDI data. When carrier is
unknown, return the range and say it depends. **Never return a single number, and
never promise a percentage.**

### D.6 Add a fifth column that is not a regime: evidence strength.

Your customer question 4 – "how do I increase survivability" – cannot be answered
from R at all. R encodes what regulators and insurers require, and we have already
established that this diverges from the science: Zone 0 passed in a deliberately
weakened form, and Syphard & Keeley found structural details outperform the
defensible space that regulation emphasises.

```
E[m] = {
  pathway: EMBER | RADIANT | FLAME,
  evidence_weight: 1..3,        # 3 = post-fire study or IBHS-tested, 1 = best practice
  source: citation
}
```

Question 4 ranks on `E`. Questions 1–3 rank on `R`. **Showing both, and being open
where they disagree, is your actual differentiator** against every compliance
checklist on the market.

### D.7 Ranking is missing, and the report will be unusable without it.

Gaps plus costs is not an output. A 40-item list converts at zero. You need:

```
priority[m] = E.evidence_weight × pathway_exposure(site) × conf[m] × urgency(R.effective_date)
              / cost_band[m]
```

with hard overrides: Zone 0 immediate items first, never a Tier 3 item above a
Tier 0/1 item in the same pathway, and a cap of roughly 8 recommendations shaped as
"5 this weekend, 2 this year, 1 at next renovation."

### D.8 Inputs to R(X) – the full list

Jurisdictional, drives which regimes apply:
- Geocode → **FHSZ class** (Moderate / High / Very High)
- Geocode → **responsibility area** (SRA vs LRA). Distinct from FHSZ, and Zone 0
  needs both: it applies to SRA, and to Very High FHSZ within LRA
- Geocode → **county and city** → local ordinance, Zone 0 Phase 2 timeline, local
  tree protection ordinances
- Geocode → **Firewise USA site** status (NFPA list) and **Fire Risk Reduction
  Community** status (BOF list)

Property, from assessor and parcel data:
- **Year built** (Chapter 7A prior, AB 38 pre-2010 threshold)
- **Number of units** (AB 38 applies to 1–4; IBHS Home vs Multifamily)
- **Stories** (IBHS eligibility: 3 or fewer)
- **Detached vs attached** (IBHS Home eligibility)
- Rebuilt after a fire? (implies post-2008 code)

Physical, from imagery or lidar – **these parameterise R, not just `a`**:
- **Eave depth** (sets the Zone 0 safety zone width)
- Presence of attached deck (triggers the 5 ft deck buffer clause)
- Presence of fence attaching to the structure
- Presence of shed or outbuilding within Zone 0
- Protected/heritage tree within 5 ft (potential IBHS disqualifier)

Survey, asked before the report and doubling as routing:
- **Intent to sell within 12 months** → activates AB 38
- **Owner-occupier vs landlord** → IBHS applicant eligibility
- **Current carrier, FAIR Plan status, non-renewal history** → savings and insurability
- **Household income band** (optional) → grant screen

### D.9 Two honest limits to design around

**Question 2, getting off the FAIR Plan, is the one you cannot model.** Carrier
underwriting appetite is proprietary, unpublished and changes quarterly. You can
truthfully say "these are the factors carriers look at, and here is where you stand
on them." You cannot say "do these five things and you will get covered." That is the
most legally exposed sentence in the whole product. Keep it descriptive.

**The ZIP-percentile factoid needs a population, not a lookup.** "How do I rank in my
ZIP" requires the pipeline pre-run over a distribution of properties, which is a batch
system, not an on-demand single-address service. The GIS half is genuinely
batch-computable at scale (footprints, canopy height, slope). The CV half is not,
cheaply. Consider computing percentiles from GIS-derived variables only, and saying
so, rather than implying a full-assessment comparison.

### D.10 Phase order: outputs first, not data first

Proposed: data inputs and cost → measures → outputs → functions.

The dependency runs the other way. You cannot scope the data until you know which
measures matter, and you cannot pick measures until you know what the report has to
say. Data-first tends to produce an expensive pipeline feeding a report nobody needed.

Suggested order:

1. **Outputs.** Write the actual report for three real addresses, by hand. A seller in
   a Very High FHSZ, a non-renewed owner in a dense suburb, a rural owner with acreage.
   Writing them by hand exposes every ambiguity in R, `a` and the ranking, cheaply.
2. **Measures.** The list falls out of what those three reports needed to say.
3. **Data.** Scope only what those measures require, split by confidence tier.
4. **Cost and functions.** Price the data, define `a(x)` per measure, build.

One caveat in your favour: data cost is a genuine gating constraint, since oblique
aerial licensing could change the unit economics entirely. So run a timeboxed
feasibility and pricing scan **in parallel** with step 1, but let the outputs drive
the spec rather than the other way round.
