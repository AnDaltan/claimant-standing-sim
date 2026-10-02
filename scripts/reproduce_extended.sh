#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PY=${PYTHON:-python3}
mkdir -p reproduced_results
PYTHONPATH=src "$PY" -m awas_sim.sweep --episodes 3000 --seed 71 --out reproduced_results
"$PY" scripts/compare_frozen.py reproduced_results
