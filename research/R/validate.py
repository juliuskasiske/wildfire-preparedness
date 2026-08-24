#!/usr/bin/env python3
"""Validate R. Checks schema conformance and coverage of each regime's canonical list."""
import yaml, sys
from collections import Counter, defaultdict

M = yaml.safe_load(open('research/R/measures.yaml'))['measures']
G = yaml.safe_load(open('research/R/regimes.yaml'))
A = {a['id'] for a in yaml.safe_load(open('research/R/attributes.yaml'))['attributes']}

VALID_STATUS = {'REQUIRED','PROHIBITED','DISCLOSE_ONLY','VOLUNTARY_CREDIT',
                'CERT_REQUIRED','RECOMMENDED','NOT_APPLICABLE'}
VALID_REGIME = set(G['regimes'])
err = []

ids = [m['id'] for m in M]
for d,c in Counter(ids).items():
    if c > 1: err.append(f"duplicate id: {d}")

for m in M:
    for r, cell in m.get('regimes', {}).items():
        if r not in VALID_REGIME: err.append(f"{m['id']}: unknown regime '{r}'")
        if cell.get('status') not in VALID_STATUS: err.append(f"{m['id']}/{r}: bad status {cell.get('status')}")
        if cell.get('status') in ('REQUIRED','PROHIBITED') and 'citation' not in cell and 'note' not in cell:
            err.append(f"{m['id']}/{r}: REQUIRED without citation")
    a = m.get('feature',{}).get('attribute')
    if a and a not in A: err.append(f"{m['id']}: unknown attribute '{a}'")
    for k in ('evidence','detection','cost'):
        if k not in m: err.append(f"{m['id']}: missing {k}")

# ---- Coverage: every canonical list item must be claimed by exactly one measure ----
def claimed(regime, key, val):
    return [m['id'] for m in M if m.get('regimes',{}).get(regime,{}).get(key)==val]

print("=" * 66)
print(f"R: {len(M)} measures, {len(VALID_REGIME)} regimes, {len(A)} attributes")
print("=" * 66)

print("\nCOVERAGE — OSFM Low-Cost Retrofit List (AB 38 disclosure)")
for lst, n in [('hardening',12), ('defensible_space',8)]:
    miss=[]
    for i in range(1, n+1):
        c=[m['id'] for m in M if (x:=m.get('regimes',{}).get('ab38_retro',{})).get('list')==lst and x.get('item')==i]
        if not c: miss.append(i)
    print(f"  {lst:18} {n-len(miss)}/{n} covered" + (f"  MISSING {miss}" if miss else "  ✓"))

print("\nCOVERAGE — Safer from Wildfires (10 CCR 2644.9)")
sfw = [m for m in M if m.get('regimes',{}).get('sfw',{}).get('status')=='VOLUNTARY_CREDIT']
items = sorted({m['savings']['sfw_item'] for m in sfw if 'savings' in m}
             | {m['regimes']['sfw'].get('credit_via','').split('.')[-1] for m in sfw if m['regimes']['sfw'].get('credit_via')} - {''})
print(f"  {len(sfw)} measures carry an SFW credit, mapping to {len(items)} distinct credit items:")
for i in items: print(f"    - {i}")

print("\nCOVERAGE — Zone 0 (BOF final rule, adopted 2026-08-19)")
z = [m for m in M if m.get('regimes',{}).get('zone0',{}).get('status') in ('REQUIRED','PROHIBITED')]
byphase = defaultdict(list)
for m in z: byphase[m['regimes']['zone0'].get('phase','?')].append(m['id'])
for p in ('IMMEDIATE','PHASE_1','PHASE_2'):
    print(f"  {p:10} {len(byphase[p]):2} measures")
    for i in byphase[p]: print(f"             {i}")

print("\nCOVERAGE — IBHS")
for lvl in ('ESSENTIAL','ENHANCED'):
    n=len([m for m in M if m.get('regimes',{}).get('ibhs',{}).get('level')==lvl])
    print(f"  {lvl:10} {n} measures")

print("\nDETECTION CONFIDENCE (drives how much must go into the survey)")
c=Counter(m['detection']['confidence'] for m in M)
for k in ('HIGH','MEDIUM','LOW'): print(f"  {k:7} {c[k]:2}  {'#'*c[k]}")
print(f"  -> {c['LOW']}/{len(M)} = {100*c['LOW']//len(M)}% of measures are NOT reliably detectable. These are the survey.")

print("\nEVIDENCE WEIGHT")
c=Counter(m['evidence']['weight'] for m in M)
for k in (3,2,1): print(f"  weight {k}: {c[k]:2}")

print("\nFREE MEASURES (typical_job == 0) — the 'this weekend' bucket")
free=[m['id'] for m in M if m['cost']['typical_job']==0 and m.get('output_class') not in ('GUIDANCE','FINDING')]
print(f"  {len(free)}: " + ", ".join(free))

print("\nDIVERGENCES (where regulation and evidence disagree — the differentiator)")
for m in M:
    if 'divergence_note' in m: print(f"  {m['id']}")

print("\nSTALENESS FLAGS")
for m in M:
    if m.get('_staleness'): print(f"  {m['id']}: {m['_staleness']}")

print("\n" + "="*66)
if err:
    print(f"FAIL — {len(err)} errors"); [print("  "+e) for e in err]; sys.exit(1)
print("VALIDATION PASSED"); print("="*66)
