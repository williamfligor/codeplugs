#!/bin/bash

set -xe

mkdir -p output

python3.exe cps-import-builder/cps-import-builder.py \
    --inputdir ./input \
    --outputdir ./output \
    --cps 878

python3.exe cps-import-builder/cps-import-builder.py \
    --inputdir ./input \
    --outputdir ./output \
    --cps uv380
