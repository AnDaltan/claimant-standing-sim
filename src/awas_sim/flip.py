from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import random
from statistics import mean

from .experiment import write_csv
from .institutions import evaluate_episode
from .model import Condition, ExperimentConfig, generate_scenarios


GRIDS = {
    "advocate_fail_base": [0.04, 0.10, 0.16, 0.22, 0.28, 0.34, 0.40, 0.46, 0.52, 0.60],
    "review_error_correlation": [0.00, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 0.95],
    "review_noise_good": [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60],
    "advocate_error_correlation": [0.00, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 0.95],
}

FOCUS = (
    Condition.PROTECTED_APPEAL,
    Condition.REDUNDANT_COMMON_CONTROL,
    Condition.LOCAL_ONLY_STANDING,
    Condition.PLURAL_STANDING,
)

PAIRS = (
    (Condition.PLURAL_STANDING, Condition.PROTECTED_APPEAL, "E_minus_C"),
    (Condition.PLURAL_STANDING, Condition.REDUNDANT_COMMON_CONTROL, "E_minus_C2"),
)

METRICS = (
    "final_merit_accuracy",
    "valid_claim_correction_rate",
    "false_claim_rejection_rate",
)


def _percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = p * (len(values) - 1)
    lo = int(pos)
    hi = min(len(values) - 1, lo + 1)
    frac = pos - lo
    return values[lo] * (1 - frac) + values[hi] * frac


def _paired_vector(left, right, metric: str) -> list[int]:
    if metric == "final_merit_accuracy":
        return [int(a.merit_correct) - int(b.merit_correct) for a, b in zip(left, right)]
    if metric == "valid_claim_correction_rate":
        return [
            int(a.valid_claim_corrected) - int(b.valid_claim_corrected)
            for a, b in zip(left, right)
            if a.valid_claim
        ]
    if metric == "false_claim_rejection_rate":
        return [
            int(a.false_claim_rejected) - int(b.false_claim_rejected)
            for a, b in zip(left, right)
            if a.claim_filed and not a.valid_claim
        ]
    raise ValueError(metric)


def _paired_interval(vector: list[int], replicates: int, seed: int) -> tuple[float, float, float]:
    point = mean(vector) if vector else float("nan")
    if not vector:
        return point, float("nan"), float("nan")
    rng = random.Random(seed)
    n = len(vector)
    samples = []
    for _ in range(replicates):
        samples.append(sum(rng.choices(vector, k=n)) / n)
    return point, _percentile(samples, 0.025), _percentile(samples, 0.975)


def _condition_metrics(rows):
    valid = [r for r in rows if r.valid_claim]
    invalid = [r for r in rows if r.claim_filed and not r.valid_claim]
    return {
        "final_merit_accuracy": sum(r.merit_correct for r in rows) / len(rows),
        "valid_claim_correction_rate": sum(r.valid_claim_corrected for r in valid) / len(valid),
        "false_claim_rejection_rate": sum(r.false_claim_rejected for r in invalid) / len(invalid),
    }


def run_sweep(
    episodes: int = 5000,
    seed: int = 71,
    bootstrap_replicates: int = 400,
    bootstrap_seed: int = 20260929,
):
    base = ExperimentConfig()
    # None of the swept cognitive parameters changes scenario generation, so one
    # paired scenario bank can be reused for every cell.
    scenarios = generate_scenarios(episodes, seed=seed, config=base)
    rows: list[dict[str, object]] = []

    cell_index = 0
    for parameter, values in GRIDS.items():
        for value in values:
            cfg = replace(base, **{parameter: value})
            by_condition = {
                c: [evaluate_episode(s, c, cfg) for s in scenarios]
                for c in FOCUS
            }
            condition_metrics = {c: _condition_metrics(rs) for c, rs in by_condition.items()}

            for c in FOCUS:
                m = condition_metrics[c]
                rows.append(
                    {
                        "parameter": parameter,
                        "value": value,
                        "kind": "condition",
                        "comparison": c.value,
                        "final_merit_accuracy": m["final_merit_accuracy"],
                        "valid_claim_correction_rate": m["valid_claim_correction_rate"],
                        "false_claim_rejection_rate": m["false_claim_rejection_rate"],
                        "paired_metric": "",
                        "paired_difference": "",
                        "ci_2_5": "",
                        "ci_97_5": "",
                        "bootstrap_replicates": bootstrap_replicates,
                    }
                )

            for pair_index, (left, right, label) in enumerate(PAIRS):
                for metric_index, metric in enumerate(METRICS):
                    vector = _paired_vector(by_condition[left], by_condition[right], metric)
                    bs_seed = bootstrap_seed + cell_index * 100 + pair_index * 10 + metric_index
                    point, lo, hi = _paired_interval(vector, bootstrap_replicates, bs_seed)
                    rows.append(
                        {
                            "parameter": parameter,
                            "value": value,
                            "kind": "paired_difference",
                            "comparison": label,
                            "final_merit_accuracy": "",
                            "valid_claim_correction_rate": "",
                            "false_claim_rejection_rate": "",
                            "paired_metric": metric,
                            "paired_difference": point,
                            "ci_2_5": lo,
                            "ci_97_5": hi,
                            "bootstrap_replicates": bootstrap_replicates,
                        }
                    )
            cell_index += 1

    thresholds: list[dict[str, object]] = []
    threshold_metrics = (
        "valid_claim_correction_rate",
        "false_claim_rejection_rate",
    )
    for parameter, values in GRIDS.items():
        for comparison in ("E_minus_C", "E_minus_C2"):
            for metric in threshold_metrics:
                series = [
                    r for r in rows
                    if r["parameter"] == parameter
                    and r["kind"] == "paired_difference"
                    and r["comparison"] == comparison
                    and r["paired_metric"] == metric
                ]
                series.sort(key=lambda r: float(r["value"]))
                first = float(series[0]["paired_difference"]) if series else 0.0

                if first > 0.0:
                    sign_change = next((r for r in series if float(r["paired_difference"]) < 0.0), None)
                    significant_reversal = next((r for r in series if float(r["ci_97_5"]) < 0.0), None)
                elif first < 0.0:
                    sign_change = next((r for r in series if float(r["paired_difference"]) > 0.0), None)
                    significant_reversal = next((r for r in series if float(r["ci_2_5"]) > 0.0), None)
                else:
                    sign_change = None
                    significant_reversal = None

                for criterion, hit in (
                    ("sign_change", sign_change),
                    ("significant_reversal", significant_reversal),
                ):
                    thresholds.append(
                        {
                            "parameter": parameter,
                            "comparison": comparison,
                            "paired_metric": metric,
                            "criterion": criterion,
                            "baseline_value": series[0]["value"] if series else "",
                            "baseline_paired_difference": first if series else "",
                            "threshold": hit["value"] if hit else "none_in_range",
                            "paired_difference_at_threshold": hit["paired_difference"] if hit else "",
                            "ci_2_5": hit["ci_2_5"] if hit else "",
                            "ci_97_5": hit["ci_97_5"] if hit else "",
                            "grid": ";".join(str(v) for v in values),
                        }
                    )

    return rows, thresholds


def main() -> None:
    p = argparse.ArgumentParser(description="v0.3 bridge: cognitive-parameter robustness thresholds")
    p.add_argument("--episodes", type=int, default=5000)
    p.add_argument("--seed", type=int, default=71)
    p.add_argument("--bootstrap", type=int, default=400)
    p.add_argument("--bootstrap-seed", type=int, default=20260929)
    p.add_argument("--out", type=Path, default=Path("results/v0_2_1"))
    args = p.parse_args()

    rows, thresholds = run_sweep(
        episodes=args.episodes,
        seed=args.seed,
        bootstrap_replicates=args.bootstrap,
        bootstrap_seed=args.bootstrap_seed,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "flip_sweep.csv", rows)
    write_csv(args.out / "robustness_thresholds.csv", thresholds)
    print(args.out / "flip_sweep.csv")
    print(args.out / "robustness_thresholds.csv")


if __name__ == "__main__":
    main()
