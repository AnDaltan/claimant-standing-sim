from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .experiment import run_experiment, write_csv
from .model import Condition, ExperimentConfig

KEEP = [
    "final_merit_accuracy",
    "valid_claim_correction_rate",
    "false_claim_rejection_rate",
    "retained_route_rate_valid_claims",
    "retained_route_after_escalation",
    "strategic_escalation_rate",
    "mean_review_cost",
    "mean_claimant_harm",
    "mean_system_loss",
]


def main() -> None:
    p = argparse.ArgumentParser(description="Decompose the AWAS reach effect")
    p.add_argument("--episodes", type=int, default=10_000)
    p.add_argument("--seed", type=int, default=97)
    p.add_argument("--out", type=Path, default=Path("results"))
    args = p.parse_args()

    base = ExperimentConfig()
    regimes = [
        ("operational_only", replace(base, attack_intensity=0.0, strategic_escalation_strength=0.0)),
        ("attacks_no_opportunistic", replace(base, attack_intensity=1.0, strategic_escalation_strength=0.0)),
        ("opportunistic_no_attacks", replace(base, attack_intensity=0.0, strategic_escalation_strength=0.85)),
        ("full_v0_2", base),
    ]

    out: list[dict[str, object]] = []
    focus = {Condition.LOCAL_ONLY_STANDING.value, Condition.PLURAL_STANDING.value}
    for label, cfg in regimes:
        _, summary = run_experiment(args.episodes, args.seed, cfg)
        for row in summary:
            if row["condition"] in focus:
                out.append({"regime": label, "condition": row["condition"], **{k: row[k] for k in KEEP}})

    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "reach_decomposition.csv", out)


if __name__ == "__main__":
    main()
