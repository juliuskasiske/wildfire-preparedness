# R — the regulation / requirement matrix

Machine-readable encoding of what California wildfire regimes actually require, mapped
onto detectable property features.

```
regimes.yaml     the four regimes + PRC 4291, their applicability predicates and clocks
attributes.yaml  R(X) — every property attribute needed to resolve R or a
measures.yaml    the measure catalogue. This is R.
```

## Model

```
R[m][regime] -> cell            requirement status for measure m under regime
a[m]         -> {ADOPTED | NOT_ADOPTED | UNKNOWN, confidence, source}
g            = R ⊙ (a == NOT_ADOPTED)     gaps        -> the action list
e            = R_savings ⊙ (a == ADOPTED) entitlements -> "claim what you already have"
u            = R ⊙ (a == UNKNOWN)         unresolved  -> survey questions
E[m]                                       evidence weight, independent of any regime
```

Questions 1–3 (compliance, coverage, premium) rank on `R`. Question 4 (survivability)
ranks on `E`. They diverge on purpose — see `divergence_note` on individual measures.

## Cell schema

```yaml
status:  REQUIRED           # legally mandatory
       | PROHIBITED         # a thing you may not newly do
       | DISCLOSE_ONLY      # must be reported, not performed
       | VOLUNTARY_CREDIT   # not required; earns a discount or certification
       | CERT_REQUIRED      # required to obtain a voluntary certification
       | RECOMMENDED        # published best practice, no legal or credit effect
       | NOT_APPLICABLE
clock:                      # when it bites
  basis: ALREADY_IN_FORCE | ON_EFFECTIVE_DATE | EFFECTIVE_PLUS_YEARS | ON_TRANSACTION
       | ON_REPLACEMENT     # only when the component is replaced anyway
  years: <int>              # with EFFECTIVE_PLUS_YEARS
  set_by: STATE | LOCAL_JURISDICTION
  note: <string>
applies_if: [<predicate ids from regimes.yaml>]
parameter: {...}            # requirement varies by property attribute
citation: <string>
```

`ON_REPLACEMENT` matters: several Low-Cost Retrofit List items and IBHS items only bite
when the component is being replaced anyway. Presenting those as "do this now" is wrong
and expensive. They belong in the "at next renovation" bucket of the report.

## Measure schema

```yaml
- id:               dot.namespaced.stable.id   # never renumber, product data keys off this
  name:             short imperative
  component:        roof | gutter | vent | eave | siding | window | door | deck | fence
                    | zone0 | zone1 | zone2 | outbuilding | chimney | garage | community | access
  pathway:          EMBER | RADIANT | FLAME
  feature:                                     # the physical thing `a` resolves against
    attribute:      <id from attributes.yaml>
    compliant_when: <predicate in prose; formalise in code>
  regimes:          {<regime_id>: <cell>}
  evidence:
    weight:         1..3        # 3 = post-fire study or IBHS full-scale test; 1 = best practice
    basis:          <citation>
  detection:
    method:         GIS | AERIAL_CV | OBLIQUE_CV | STREETVIEW_CV | ASSESSOR | SURVEY
    confidence:     HIGH | MEDIUM | LOW
    note:           <string>
  cost:
    unit:           EA | LF | SF | JOB | NONE
    low:  <usd>  high: <usd>
    typical_job:    <usd>       # for the Headwaters 1,000 sqft / 130 LF reference home
    source:         <string>
  savings:
    sfw_item:       <id>        # links to the RFF-measured discount, if any
```

## Provenance

Every cell carries a `citation`. Sources, in full:

- **Zone 0** — CA Board of Forestry and Fire Protection, final rule text approved 8-0 on
  **19 August 2026** (August 2026 rule package, "SUMMARY OF DRAFT ZONE 0 REGULATION
  LANGUAGE"). Applies to SRA (PRC 4291) and Very High FHSZ within LRA (Gov. Code 51182).
- **PRC 4291** — Public Resources Code § 4291, in force.
- **Safer from Wildfires** — Cal. Code Regs. Tit. 10, **§ 2644.9**, effective October 2022.
  Discount magnitudes from Ludington, Liao & Walls, RFF WP 25-30 (Dec 2025), Tables 3–4.
- **AB 38** — Civil Code § 1102.6f (vulnerable-feature disclosure, from 1 Jan 2021),
  defensible space documentation before close of escrow (from 1 Jul 2021), and the
  Office of the State Fire Marshal **Low-Cost Retrofit List updated 1/1/2026**
  (disclosure duty from 1 Jul 2025), authorised by Gov. Code § 51189.
- **IBHS** — Wildfire Prepared Home How-To checklist (Aug 2023 edition, the most detailed
  public text), standard updated Jun 2025 and Jun 2026. See `_staleness` flags.

## Known staleness and open items

1. **Zone 0 effective date is not yet fixed.** The Board vote approved the text; confirm
   the Office of Administrative Law step before rendering any countdown. All Zone 0
   clocks are expressed relative to `EFFECTIVE_DATE`, a single variable in regimes.yaml.
2. **Zone 0 Phase 2 dates are set by the local jurisdiction**, within 5 years. Unresolvable
   from state data. Render as a range until a local lookup exists.
3. **IBHS detail is from the Aug 2023 checklist.** The Jun 2026 update relaxed tree and
   shrub spacing and clarified deck and attached-structure rules. Measures carrying
   `_staleness: IBHS_2023` need re-verification against the current technical standard.
4. **AB 1 (eff. 1 Jan 2026)** requires CDI to periodically review Safer from Wildfires.
   The 12-item list is expected to change. Re-verify on a schedule.
