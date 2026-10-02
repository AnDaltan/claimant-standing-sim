#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PY=${PYTHON:-python3}
mkdir -p reproduced_results
PYTHONPATH=src "$PY" -m awas_sim.sensitivity --seeds 12 --episodes 4000 --out reproduced_results
PYTHONPATH=src "$PY" -m awas_sim.reach --episodes 10000 --seed 97 --out reproduced_results
"$PY" scripts/compare_frozen.py reproduced_results
