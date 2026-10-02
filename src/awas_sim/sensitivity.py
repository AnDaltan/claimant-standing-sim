from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from .experiment import run_experiment, write_csv
from .model import ExperimentConfig

METRICS = [
    "final_merit_accuracy",
    "valid_claim_correction_rate",
    "false_claim_rejection_rate",
    "retained_route_rate_valid_claims",
    "retained_route_after_escalation",
    "retained_route_compound_attack",
    "strategic_escalation_rate",
    "mean_effective_route_cut_valid_claims",
    "cut_ge_2_rate_valid_claims",
    "mean_review_cost",
    "mean_claimant_harm",
    "mean_system_loss",
]


def main() -> None:
    p = argparse.ArgumentParser(description="Seed sensitivity for AWAS CPU v0.2")
    p.add_argument("--seeds", type=int, default=12)
    p.add_argument("--episodes", type=int, default=4000)
    p.add_argument("--out", type=Path, default=Path("results"))
    args = p.parse_args()

    cfg = ExperimentConfig()
    raw = []
    grouped = defaultdict(lambda: defaultdict(list))
    for seed in range(1, args.seeds + 1):
        _, summary = run_experiment(args.episodes, seed, cfg)
        for row in summary:
            raw.append({"seed": seed, **row})
            for metric in METRICS:
                grouped[row["condition"]][metric].append(float(row[metric]))

    aggregate = []
    for condition, metrics in grouped.items():
        row = {"condition": condition, "seeds": args.seeds, "episodes_per_seed": args.episodes}
        for metric, values in metrics.items():
            row[f"{metric}_mean"] = mean(values)
            row[f"{metric}_sd"] = stdev(values) if len(values) > 1 else 0.0
            row[f"{metric}_min"] = min(values)
            row[f"{metric}_max"] = max(values)
        aggregate.append(row)

    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "seed_sensitivity_raw.csv", raw)
    write_csv(args.out / "seed_sensitivity_summary.csv", aggregate)


if __name__ == "__main__":
    main()
