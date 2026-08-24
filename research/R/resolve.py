#!/usr/bin/env python3
"""Demo resolver: R(X) -> applicable cells, with clocks resolved. Not the product, a proof."""
import yaml
from datetime import date

M = yaml.safe_load(open('research/R/measures.yaml'))['measures']
G = yaml.safe_load(open('research/R/regimes.yaml'))

ZONE0_EFFECTIVE = date(2026, 10, 1)   # PLACEHOLDER — pending OAL confirmation

def applies(regime, X):
    r = G['regimes'][regime]
    for pid in (r.get('applies_if') or []):
        p = G['predicates'][pid]['expr']
        if not eval(p, {}, dict(X, CARRIERS_WITHOUT_WILDFIRE_RATING=set(), IBHS_STATES={'CA'})):
            return False
    return True

def deadline(cell, regime):
    c = cell.get('clock') or {}
    b = c.get('basis') or G['regimes'][regime].get('clock')   # fall back to regime default
    if b == 'ALREADY_IN_FORCE': return "in force now"
    if b == 'ON_EFFECTIVE_DATE': return f"{ZONE0_EFFECTIVE}"
    if b == 'EFFECTIVE_PLUS_YEARS':
        y = c['years']; d = ZONE0_EFFECTIVE.replace(year=ZONE0_EFFECTIVE.year + y)
        s = " (local jurisdiction sets, up to)" if c.get('set_by') == 'LOCAL_JURISDICTION' else ""
        return f"by {d}{s}"
    if b == 'ON_TRANSACTION': return "before close of escrow"
    if b == 'ON_REPLACEMENT': return "only when replacing anyway"
    return "-"

X = dict(  # 1968 single-family in Altadena-like density, Very High FHSZ, LRA, seller
    fhsz='VERY_HIGH', responsibility_area='LRA', year_built=1968, dwelling_units=1,
    stories=1, structure_type='SINGLE_FAMILY_DETACHED', state='CA', is_owner_occupier=True,
    intent_to_sell_12mo=True, carrier='ExampleMutual',
)

print("PROPERTY:", ", ".join(f"{k}={v}" for k,v in X.items() if k in
      ('fhsz','responsibility_area','year_built','intent_to_sell_12mo')))
active = [r for r in G['regimes'] if applies(r, X)]
print("ACTIVE REGIMES:", ", ".join(active), "\n")

rows = []
for m in M:
    for r, cell in m.get('regimes', {}).items():
        if r not in active: continue
        st = cell.get('status')
        if st in ('NOT_APPLICABLE', 'RECOMMENDED'): continue
        rows.append((st, r, deadline(cell, r), m['id'], m['cost']['typical_job'],
                     m['evidence']['weight'], m['detection']['confidence']))

order = {'REQUIRED':0,'PROHIBITED':1,'DISCLOSE_ONLY':2,'CERT_REQUIRED':3,'VOLUNTARY_CREDIT':4}
rows.sort(key=lambda x: (order[x[0]], x[4], -x[5]))

cur = None
for st, r, dl, mid, cost, ev, conf in rows:
    if st != cur: print(f"\n--- {st} ({sum(1 for x in rows if x[0]==st)}) ---"); cur = st
    print(f"  {mid:42} {r:11} {dl:34} ${cost:>6,}  E{ev} {conf}")

print(f"\n{len(rows)} applicable cells across {len({x[3] for x in rows})} distinct measures.")
free = sorted({x[3] for x in rows if x[4]==0})
print(f"\nFREE ACTIONS ({len(free)}) — the 'this weekend' bucket:")
for f in free: print("  " + f)
