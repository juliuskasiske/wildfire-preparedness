#!/bin/bash
cd /Users/juliuskasiske/Documents/artesia/signup-product
U="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CA_2025LosAngelesPostWildfire_C25/CA_LAPostWildfire_Palisades_C25/LAZ/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz"
O=data/lidar/USGS_LPC_CA_2025LosAngelesPostWildfire_C25_11SLT003585037680.laz
for i in $(seq 1 12); do
  rm -f "$O"
  if curl -sS -L --http1.1 --max-time 3000 --speed-time 180 --speed-limit 5000 -o "$O" "$U"; then
    S=$(stat -f%z "$O"); if [ "$S" -gt 50000000 ]; then
      echo "LIDAR2025 DONE $(echo $S|awk '{printf "%.1fMB",$1/1e6}')"; exit 0; fi
    echo "  attempt $i: short file $S bytes"
  else echo "  attempt $i: transfer failed"; fi
  sleep 20
done
echo "LIDAR2025 EXHAUSTED"
