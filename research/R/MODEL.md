# The implicit data model

Derived by introspecting `measures.yaml`, `attributes.yaml` and `regimes.yaml` rather
than from memory. Sections marked **[IN DATA]** describe what is actually there.
Sections marked **[PROPOSED]** are extensions the derivation showed are missing.

---

## 1. The core abstraction: six orthogonal axes

Every row in R is a point in a six-dimensional space. Each axis answers one question,
and they are genuinely independent — which is why the model survives a regime changing
without touching the others.

| Axis | Question | Fields | Owned by |
|---|---|---|---|
| **Locus** | *What physical thing?* | `component`, `feature.attribute` | the asset |
| **Mechanism** | *Why does it matter?* | `pathway`, `evidence` | physics |
| **Norm** | *Who says so, and how hard?* | `regimes[].status` | authorities |
| **Time** | *By when?* | `regimes[].clock` | authorities |
| **Economics** | *What does it cost, what does it return?* | `cost`, `savings` | markets |
| **Epistemics** | *How do we know whether it is already done?* | `detection` | your pipeline |

The design payoff: **Norm and Mechanism are separate axes.** That is the whole reason
you can honestly tell a homeowner "the law asks for 12 inches, the evidence supports
5 feet." A model that folded evidence into the regulation could not express that, and
it is your differentiator.

The second payoff: **Epistemics is an axis, not a footnote.** Confidence travels with
every claim, so the report can distinguish "you have X" from "we think you have X"
from "we cannot see X, tell us."

---

## 2. Entity model

### [IN DATA]

```
Regime      1 ──< Cell >── 1  Measure      Cell = (Measure × Regime) → deontic claim
Measure     1 ──< Feature ── 1 Attribute   what physical proposition the measure changes
Measure     1 ──  Evidence                 mechanism weight, regime-independent
Measure     1 ──  Cost                     unit rate + reference-home total
Measure     0..1  Savings                  link into the SFW credit table
Attribute   1 ──  Source                   where the value comes from
```

296 cells exist across 71 measures × 7 regimes. **153 of them are `NOT_APPLICABLE`** —
over half the matrix is explicit negative space. That is deliberate (explicit beats
absent, because a missing cell is ambiguous between "no" and "not yet researched"),
but it means R should be **stored as a sparse edge list, not a dense matrix**, with
`NOT_APPLICABLE` as an assertion rather than a default.

### [PROPOSED] Two entities are missing, and one of them matters a lot

**`Observation` — the instance behind an Attribute.** `attributes.yaml` defines
*propositions* ("roof_material"), but nothing models a *resolved value for a specific
property at a specific time*. This is not pedantry: Street View imagery is routinely
1–7 years old, and aerial imagery refreshes on a cadence. **An assessment built on a
2019 image of a house that burned in 2025 is worse than no assessment.**

```
Observation {
  property_id, attribute_id
  value
  observed_at        # when the WORLD was in this state (imagery capture date)
  resolved_at        # when YOU computed it
  method, confidence, provenance
  superseded_by      # observations are append-only; never overwrite
}
```

Staleness then becomes a first-class output: *"our imagery of your property is from
March 2022 — confirm this is still accurate."* That is also a re-engagement hook.

**`EvidenceSource` — citations as rows, not strings.** `evidence.basis` is free text.
Making it an entity lets `E` be revised when new post-fire research lands without
touching 71 measures, and lets the report cite properly.

---

## 3. Enum catalogue

### 3.1 Pathway — the hazard vector **[IN DATA]**

| Value | n | Meaning |
|---|---|---|
| `EMBER` | 26 | Firebrand lands on or enters the structure |
| `RADIANT` | 8 | Heat flux from nearby burning fuel, no contact |
| `FLAME` | 37 | Fuel in direct contact or continuous with the structure |

Generalised name: **HazardVector**. In another peril domain this axis becomes
`SURGE / WIND / DEBRIS_IMPACT` (hurricane) or `GROUND_SHAKING / LIQUEFACTION` (seismic).

### 3.2 Component — **[IN DATA, but conflated]**

18 values in use: `roof, gutter, chimney, vent, eave, siding, window, door, garage,
deck, fence, outbuilding, zone0, zone1, zone2, community, access, structure`.

**This is the clearest schema flaw the derivation exposed.** The list mixes three
different concepts. `zone0` is a *spatial band*, `roof` is a *building element*,
`community` is a *scale*. Factor into three independent enums:

```
Locus      BUILDING_ENVELOPE | ATTACHED_STRUCTURE | SITE | PARCEL | NEIGHBOURHOOD | ACCESS_ROUTE
Element    ROOF | GUTTER | VENT | EAVE | SIDING | WINDOW | DOOR | GARAGE | CHIMNEY | SKYLIGHT
           | DECK | FENCE | GATE | OUTBUILDING | VEGETATION | GROUND_COVER | STORED_MATERIAL
           | UTILITY | ROADWAY | SIGNAGE | ORGANISATION
DistanceBand  ZONE_0 (0–5 ft) | ZONE_1 (5–30 ft) | ZONE_2 (30–100 ft) | BEYOND | ON_STRUCTURE
```

`zone0.mulch_removal` becomes `{locus: SITE, element: GROUND_COVER, band: ZONE_0}`.
That is queryable in ways the current flat string is not — for instance "everything in
ZONE_0 regardless of element" is exactly the Zone 0 report section, and right now you
get it only by string-prefix matching, which is fragile.

### 3.3 Normative status — **[IN DATA]**, and it is a compound

| Value | n |
|---|---|
| `NOT_APPLICABLE` | 153 |
| `CERT_REQUIRED` | 49 |
| `REQUIRED` | 35 |
| `DISCLOSE_ONLY` | 31 |
| `VOLUNTARY_CREDIT` | 19 |
| `RECOMMENDED` | 7 |
| `PROHIBITED` | 2 |

**[PROPOSED]** These seven are not primitive. They are the product of two independent
enums, and separating them removes the need to invent a new status every time a regime
behaves slightly differently:

```
DeonticForce      MUST | MUST_NOT | MUST_REPORT | MAY_EARN | SHOULD | NONE
EnforcementMode   INSPECTION | TRANSACTION_GATE | RATE_FILING | CERTIFICATION_AUDIT
                | PERMIT_REVIEW | NONE
```

| Current status | = DeonticForce | × EnforcementMode |
|---|---|---|
| `REQUIRED` (PRC 4291) | MUST | INSPECTION |
| `REQUIRED` (AB 38 DS) | MUST | TRANSACTION_GATE |
| `PROHIBITED` | MUST_NOT | INSPECTION |
| `DISCLOSE_ONLY` | MUST_REPORT | TRANSACTION_GATE |
| `VOLUNTARY_CREDIT` | MAY_EARN | RATE_FILING |
| `CERT_REQUIRED` | MUST *(conditional on pursuing the cert)* | CERTIFICATION_AUDIT |
| `RECOMMENDED` | SHOULD | NONE |

This also makes the report's phrasing derivable rather than hand-written: MUST +
TRANSACTION_GATE renders as "you cannot close escrow without this", MUST_REPORT
renders as "you will have to tell a buyer you did not do this", MAY_EARN renders as
"this earns you a discount." Right now that mapping lives in your head.

### 3.4 Clock — **[IN DATA]**

```
ALREADY_IN_FORCE      22    in force today
ON_EFFECTIVE_DATE      6    bites the moment the regime commences
EFFECTIVE_PLUS_YEARS  16    regime epoch + N years  (Zone 0 phases: 3 and 5)
ON_TRANSACTION         3    triggered by sale
ON_REPLACEMENT         4    only when the component is replaced anyway
```

`ON_REPLACEMENT` is the one people get wrong. Four OSFM items and several IBHS items
only bite at replacement; rendering them as "do this now" turns a $0 obligation into a
$12,000 recommendation.

**[PROPOSED]** generalise to a trigger model, and add the missing kinds:

```
TriggerKind   CONTINUOUS | ABSOLUTE_DATE | REGIME_EPOCH_RELATIVE | EVENT
EventKind     SALE | COMPONENT_REPLACEMENT | PERMIT_APPLICATION | POLICY_RENEWAL
            | INSPECTION | POST_LOSS_REBUILD
```

`POST_LOSS_REBUILD` matters in California specifically: rebuilding after a fire pulls
the property into current code, which changes half the matrix at once.

### 3.5 Authority level **[PARTIAL IN DATA]**

In data: `STATE` (17), `LOCAL_JURISDICTION` (5).
**[PROPOSED]**: `FEDERAL | STATE | COUNTY | MUNICIPAL | FIRE_DISTRICT | PRIVATE_STANDARD | CARRIER | HOA`.

`HOA` is not decorative — HOA landscaping covenants actively conflict with Zone 0 in
California, and `FIRE_DISTRICT` is the body that will actually set your Zone 0 Phase 2
date. Both belong in the model before you need them.

### 3.6 Regime kind **[IN DATA]**

`STATUTE | REGULATION | INSURANCE_REGULATION | TRANSACTION_STATUTE |
TRANSACTION_DISCLOSURE | VOLUNTARY_CERTIFICATION`

Generalised: **BindingSource** — what makes the claim stick. Add `BUILDING_CODE`
(Chapter 7A / CWUI is currently modelled only as a suppression prior, not a regime,
which is arguably wrong), `GRANT_CONDITION`, and `LENDER_REQUIREMENT`.

### 3.7 Observation method and confidence **[IN DATA, and under-modelled]**

Method on measures: `SURVEY` 21, `STREETVIEW_CV` 19, `AERIAL_CV` 18, `GIS` 13.
Confidence: `LOW` 43, `MEDIUM` 20, `HIGH` 8.

Two problems the derivation exposed.

**First, `attribute.source` is free text** — 35 distinct unnormalised strings
("county assessor", "CHM in buffer ring", "STREETVIEW_CV or SURVEY"). Unqueryable.
Structure it:

```
Modality   ADMINISTRATIVE_RECORD | GEOSPATIAL_COMPUTATION | REMOTE_SENSING
         | STREET_LEVEL_IMAGERY | SELF_REPORT | PROFESSIONAL_INSPECTION
Dataset    named, with licence, refresh cadence, resolution, cost per lookup
Technique  SPATIAL_JOIN | RASTER_ZONAL_STAT | SEGMENTATION | CLASSIFICATION
         | OBJECT_DETECTION | OCR | LOOKUP | DIRECT_QUESTION
```

**Second, `detection` sits on the Measure but belongs on the Attribute.** Detection is
a property of *how you observe a thing*, not of *the action you take about it*. Several
measures share an attribute and restate detection inconsistently. Move it, and let
measures inherit.

**Third, HIGH/MEDIUM/LOW hides the reason.** Replace with an observability class that
explains *why*, because the report language differs for each:

```
ObservabilityClass
  DIRECT          measured from data                    "your roof is wood shake"
  INFERRED        proxy or derived                      "likely, given overhanging canopy"
  PRIOR           statistical from cohort               "homes built after 2008 usually have..."
  UNOBSERVABLE    must be asked                         "we cannot see this — tell us"
  OCCLUDED        structurally hidden from any sensor   under decks, inside attics, vent interiors
```

`OCCLUDED` is worth separating from `UNOBSERVABLE`: no imagery budget will ever fix it,
so those attributes are permanently survey-bound and you should stop pricing sensors
against them.

### 3.8 Cost **[IN DATA, and incomplete]**

Units in use: `JOB` 23, `NONE` 18, `EA` 13, `SF` 9, `LF` 7, `CY` 1.

**The gap: a unit rate without a quantity is not a cost.** `{unit: SF, low: 6.67}` is
unusable until you know how many square feet. I papered over this with `typical_job`,
hardcoded to Headwaters' 1,000 sq ft reference home. For a real product:

```
Cost {
  rate_low, rate_high, unit
  quantity_driver: <attribute_id>     # roof_area_sf, perimeter_lf, window_count, vent_count
  quantity_default                    # reference-home fallback when the attribute is unknown
  region_multiplier                   # CA union labour vs elsewhere
  diy_possible: bool                  # collapses rate to materials only
  price_as_of: date
}
```

`quantity_driver` is the missing link between the attribute layer and the cost layer,
and it is also a list of attributes you are not currently extracting (roof area,
wall perimeter, window count) but which are all derivable from the footprint and
roof segmentation you already need.

### 3.9 Benefit **[BADLY UNDER-MODELLED]**

Only 13 of 71 measures carry `savings`, and it models exactly one benefit type: an
insurance premium discount. Every value-add worth building is a *different* benefit
type, and none of them are representable today:

```
BenefitKind
  PREMIUM_DISCOUNT         quantified, small ($5–31/yr per measure)
  INSURABILITY             carrier willingness to write at all — the big one
  TRANSACTION_ENABLEMENT   removes an escrow blocker
  GRANT_ELIGIBILITY        California Safe Homes, CWMP, local FSC
  PENALTY_AVOIDANCE        avoids an inspection failure or citation
  LOSS_REDUCTION           expected damage avoided — the actual point
  CERTIFICATION_PROGRESS   moves you toward IBHS Essential or Enhanced
```

Each needs its own confidence, because they are known to wildly differing degrees:
`PREMIUM_DISCOUNT` is measured (RFF), `LOSS_REDUCTION` is partially studied,
`INSURABILITY` is proprietary and effectively unknowable. Modelling them as one field
would let an unknowable number masquerade as a measured one — which is exactly the
mistake to avoid in a report you want people to trust.

### 3.10 Output class **[IN DATA, sparse]**

In data: `GUIDANCE` 3, `FINDING` 1, everything else implicitly an action.
**[PROPOSED]** make it exhaustive and explicit, because it drives report layout:

```
OutputClass
  ACTION        a gap to close                    ← g = R ⊙ (a == NOT_ADOPTED)
  ENTITLEMENT   already done, probably unclaimed  ← e = R_savings ⊙ (a == ADOPTED)
  UNRESOLVED    cannot determine; ask             ← u = R ⊙ (a == UNKNOWN)
  FINDING       a fact, not an action             (structure separation, slope)
  GUIDANCE      a prohibition or standing rule    (do not plant new trees)
  BLOCKER       forecloses a path entirely        (protected tree kills IBHS eligibility)
  STALE         observation too old to rely on
```

---

## 4. Relations **[AD HOC IN DATA — the biggest structural gap]**

The derivation found these used **once each**: `alternative` (1), `compounds_with` (1),
`routes_to` (1), `blocker` (1). Plus `suppress_if` (4), `applies_only_if` (14),
`credit_via` (10).

Used once means one of two things: the relation is rare, or **I only populated it where
I happened to notice.** It is the second. Windows-or-shutters is not the only
alternative pair, and mulch-plus-fence is not the only compounding pair. Make relations
first-class typed edges and populate them systematically:

```
MeasureRelation {
  from, to, kind, note
}

RelationKind
  ALTERNATIVE_TO      either satisfies the same cell        windows ⟷ shutters (SFW)
  SUPERSEDES          strictly stronger version             IBHS full 5 ft ▷ Zone 0 12 in
  PREREQUISITE_OF     must precede                          clear debris ▷ install gutter guard
  COMPOUNDS_WITH      joint hazard exceeds the sum          mulch + wood fence (NIST)
  BLOCKS              forecloses the target                 protected tree ▷ IBHS cert
  ROUTES_TO           finding implies these actions         separation ▷ Firewise
  SUPPRESSED_BY       a prior makes it moot                 year_built ≥ 2008 ▷ roof.class_a
```

`SUPERSEDES` deserves special note: it is how you represent the same physical action at
different stringencies across regimes without duplicating measures. Zone 0's 12-inch
safety zone and IBHS's full 5 feet are the *same* action at two thresholds. Modelling
that as an edge, rather than two measures, is what lets the report say "doing the IBHS
version also satisfies Zone 0" — which is real, useful advice.

**Also: `applies_only_if` and `suppress_if` are semantically different and should not
look alike.** `applies_only_if` means *the measure is meaningless here* (no chimney →
no spark arrestor). `suppress_if` means *it probably already exists* (built 2015 → has
a Class A roof). The first is a hard filter, the second is a **prior on `a`**, and
should feed the confidence model rather than silently deleting the row. Right now they
are both optional string predicates and a naive implementation would treat them the
same, which would hide recommendations that ought to appear with a caveat.

---

## 5. The generalised model

Strip the wildfire vocabulary and what remains is:

> **A normative obligation graph over a partially observable physical asset.**

Five participants, and the shape recurs across domains:

1. An **asset** with attributes, only some of which you can observe.
2. Several **authorities** making overlapping, sometimes conflicting claims about it,
   with different deontic force, enforcement, and clocks.
3. A body of **evidence** about what actually reduces harm, which does *not* coincide
   with what the authorities require.
4. An **economics layer**: what each change costs, and several kinds of benefit known
   to very different degrees of certainty.
5. An **epistemic layer** that determines which of the above you can even assert.

This transfers directly to flood retrofit (FEMA BFE, NFIP CRS, state disclosure,
elevation certificates), seismic retrofit (soft-story ordinances, FEMA P-807, carrier
credits), and energy or accessibility retrofit. The measures change; the six axes,
the deontic × enforcement factoring, and the observability classes do not.

The specific thing worth keeping from this build, if you generalise later: **evidence
and regulation are separate axes, and the gap between them is a product feature rather
than an inconsistency to reconcile.**

---

## 6. Concrete fixes, in priority order

1. **Add `Observation` with `observed_at`.** Without it you will confidently describe
   a house from six-year-old imagery. Highest risk item in the model.
2. **Split `component` into locus / element / band.** Cheap now, painful later, and it
   is what the Zone 0 report section actually needs to query.
3. **Add `quantity_driver` to cost.** A rate without a quantity is not a price, and
   the drivers are all derivable from data you already need.
4. **Model `BenefitKind` as an enum, with per-kind confidence.** Otherwise insurability
   guesses get rendered with the same authority as measured discounts.
5. **Promote relations to typed edges and populate them systematically.** Especially
   `ALTERNATIVE_TO` and `SUPERSEDES`, which directly change what the report recommends.
6. **Move `detection` from Measure to Attribute** and replace HIGH/MEDIUM/LOW with
   `ObservabilityClass`, so report language becomes derivable.
7. **Split `applies_only_if` (hard filter) from `suppress_if` (prior on `a`).**
