from pathlib import Path
import hashlib
import sys

root = Path(__file__).resolve().parents[1]
regen = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "reproduced_results"
frozen = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "results"

V02_NAMES = [
    "summary.csv", "ablations.csv", "by_attack_budget.csv", "by_attack_tactic.csv",
    "by_dependency.csv", "by_escalation.csv", "by_capability_gap.csv",
    "seed_sensitivity_summary.csv", "parameter_sweep.csv",
    "joint_dependency_attack_grid.csv", "reach_decomposition.csv",
]
V021_NAMES = [
    "summary.csv", "ablations.csv", "by_attack_budget.csv", "by_attack_tactic.csv",
    "by_dependency.csv", "by_escalation.csv", "by_capability_gap.csv",
    "paired_intervals.csv", "mechanism_decomposition.csv", "flip_sweep.csv",
    "robustness_thresholds.csv",
]

names = V021_NAMES if frozen.name == "v0_2_1" else V02_NAMES


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


checked = 0
failed = 0
for name in names:
    a = frozen / name
    b = regen / name
    if not b.exists():
        continue
    checked += 1
    ok = a.exists() and sha(a) == sha(b)
    print(f"{'MATCH' if ok else 'DIFF '}: {name}")
    failed += 0 if ok else 1

if checked == 0:
    raise SystemExit("No comparable regenerated result files found.")
if failed:
    raise SystemExit(f"{failed} regenerated file(s) differ from the frozen result set.")
print(f"Verified {checked} regenerated file(s) against frozen outputs.")
