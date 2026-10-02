#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PY=${PYTHON:-python3}
rm -rf reproduced_results
mkdir -p reproduced_results
PYTHONPATH=src "$PY" -m unittest discover -s tests -v
PYTHONPATH=src "$PY" -m awas_sim.cli --episodes 20000 --seed 7 --out reproduced_results
"$PY" scripts/compare_frozen.py reproduced_results
