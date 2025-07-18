#!/bin/bash

set -xe

mkdir -p output

python3.exe chirp_to_zone.py \
    --in ./input/chirp.csv \
    --out ./input/Analog__phl.csv \
    --zone "Analog-PHL"

python3.exe cps-import-builder/cps-import-builder.py \
    --inputdir ./input \
    --outputdir ./output \
    --cps 878

python3.exe cps-import-builder/cps-import-builder.py \
    --inputdir ./input \
    --outputdir ./output \
    --cps uv380
