"""CAL FIRE hazard and responsibility layers. All free, public, no key."""
import os, json
from arcgis import download, count

BASE = "https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/ArcGIS/rest/services"

LAYERS = {
  "fhsz_sra": dict(service="fhsz24_1", layer=0,
    title="Fire Hazard Severity Zones in State Responsibility Areas (2024)",
    feeds=["fhsz"], note="SRA portion. FHSZ_Description in {Moderate, High, Very High}."),
  "fhsz_lra": dict(service="FHSALRA25_v1_All", layer=0,
    title="Fire Hazard Severity Zones in Local Responsibility Areas (map dated 2025-03-24)",
    feeds=["fhsz"], note="LRA portion, all rollout phases. Zone 0 applies in LRA only where VERY HIGH."),
  "fhsz_realestate": dict(service="fhsz24_5", layer=0,
    title="FHSZ for Real Estate Inspections",
    feeds=["fhsz_ab38"], note="CAL FIRE's own AB 38 layer. Use THIS for transaction questions."),
  "responsibility_area": dict(service="SRA22_2", layer=0,
    title="State / Local / Federal Responsibility Areas (2022)",
    feeds=["responsibility_area"], note="SRA|LRA|FRA. Distinct from FHSZ; Zone 0 needs both."),
}

def fetch(key, outdir="data/raw", log=print):
    spec = LAYERS[key]
    out = os.path.join(outdir, f"calfire_{key}.geojson")
    log(f"  {key}: {spec['title']}")
    fc = download(BASE, spec["service"], spec["layer"], out=out, log=log)
    return out, fc["_meta"]
