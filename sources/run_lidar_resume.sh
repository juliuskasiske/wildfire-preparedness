#!/bin/bash
cd /Users/juliuskasiske/Documents/artesia/signup-product
# wait for the overture extract to finish so they don't fight for bandwidth
while pgrep -f run_overture >/dev/null; do sleep 20; done
URL="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_2025LosAngelesPostWildfire_C25/CA_2025LosAngelesPostWildfire_1/LAZ/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz"
OUT=data/lidar/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz
for i in 1 2 3 4 5; do
  curl -sS -L -C - --max-time 1800 --retry 3 -o "$OUT" "$URL" && break
  echo "  retry $i (have $(stat -f%z "$OUT" 2>/dev/null || echo 0) bytes)"; sleep 5
done
echo "LIDAR2025 DONE $(stat -f%z "$OUT" | awk '{printf "%.1fMB", $1/1e6}') -> $OUT"
