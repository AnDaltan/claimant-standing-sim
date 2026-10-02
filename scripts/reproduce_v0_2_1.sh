#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
PY=${PYTHON:-python3}
OUT=reproduced_results/v0_2_1
rm -rf "$OUT"
mkdir -p "$OUT"
PYTHONPATH=src "$PY" -m unittest discover -s tests -v
PYTHONPATH=src "$PY" -m awas_sim.cli --episodes 20000 --seed 7 --ablation-set v0_2_1 --out "$OUT"
PYTHONPATH=src "$PY" -m awas_sim.uncertainty --episodes 20000 --seed 7 --bootstrap 1000 --bootstrap-seed 20260928 --out "$OUT"
PYTHONPATH=src "$PY" scripts/mechanism_probe.py --episodes 20000 --seed 7 --out "$OUT"
PYTHONPATH=src "$PY" -m awas_sim.flip --episodes 5000 --seed 71 --bootstrap 400 --bootstrap-seed 20260929 --out "$OUT"
"$PY" scripts/compare_frozen.py "$OUT" results/v0_2_1
