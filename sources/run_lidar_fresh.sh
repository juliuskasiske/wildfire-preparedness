#!/bin/bash
cd /Users/juliuskasiske/Documents/artesia/signup-product
while pgrep -f run_overture >/dev/null; do sleep 30; done   # don't contend for bandwidth
URL="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_2025LosAngelesPostWildfire_C25/CA_2025LosAngelesPostWildfire_1/LAZ/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz"
OUT=data/lidar/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz
for i in 1 2 3 4 5; do
  rm -f "$OUT"                      # server has no byte-range support: always restart clean
  if curl -sS -L --max-time 2400 --speed-time 120 --speed-limit 10000 -o "$OUT" "$URL"; then
    echo "LIDAR2025 DONE $(stat -f%z "$OUT" | awk '{printf "%.1fMB",$1/1e6}') -> $OUT"; exit 0
  fi
  echo "  attempt $i failed, retrying clean"; sleep 10
done
echo "LIDAR2025 FAILED after 5 clean attempts"
