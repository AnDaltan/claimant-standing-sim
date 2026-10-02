from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .experiment import run_experiment, write_csv
from .model import Condition, ExperimentConfig


ONE_AT_A_TIME = {
    "attack_intensity": [0.0, 0.5, 1.0, 1.5],
    "shared_dependency_mean": [0.0, 0.25, 0.50, 0.75],
    "review_error_correlation": [0.0, 0.25, 0.50, 0.75],
    "strategic_escalation_strength": [0.0, 0.5, 1.0, 1.5],
    "review_noise_good": [0.10, 0.18, 0.28, 0.40],
}

KEEP = [
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


def _compact(row: dict[str, object]) -> dict[str, object]:
    return {"condition": row["condition"], **{k: row[k] for k in KEEP}}


def main() -> None:
    p = argparse.ArgumentParser(description="Parameter sweeps for AWAS CPU v0.2")
    p.add_argument("--episodes", type=int, default=3000)
    p.add_argument("--seed", type=int, default=71)
    p.add_argument("--out", type=Path, default=Path("results"))
    args = p.parse_args()

    base = ExperimentConfig()
    rows: list[dict[str, object]] = []
    for parameter, values in ONE_AT_A_TIME.items():
        for value in values:
            cfg = replace(base, **{parameter: value})
            _, summary = run_experiment(args.episodes, args.seed, cfg)
            for s in summary:
                rows.append({"parameter": parameter, "value": value, **_compact(s)})

    # Joint stress grid: control dependence x attack intensity. This specifically
    # probes whether nominal plurality collapses when common dependencies are exposed.
    joint: list[dict[str, object]] = []
    focus = {
        Condition.PROTECTED_APPEAL.value,
        Condition.REDUNDANT_COMMON_CONTROL.value,
        Condition.PLURAL_STANDING.value,
    }
    for dependency in (0.0, 0.25, 0.50, 0.75):
        for intensity in (0.0, 0.5, 1.0, 1.5):
            cfg = replace(base, shared_dependency_mean=dependency, attack_intensity=intensity)
            _, summary = run_experiment(args.episodes, args.seed, cfg)
            for s in summary:
                if s["condition"] in focus:
                    joint.append(
                        {
                            "shared_dependency_mean": dependency,
                            "attack_intensity": intensity,
                            **_compact(s),
                        }
                    )

    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "parameter_sweep.csv", rows)
    write_csv(args.out / "joint_dependency_attack_grid.csv", joint)


if __name__ == "__main__":
    main()
