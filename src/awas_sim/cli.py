from __future__ import annotations

import argparse
from pathlib import Path

from .experiment import (
    run_ablations,
    run_experiment,
    summarise_by_attack_budget,
    summarise_by_capability_gap,
    summarise_by_dependency,
    summarise_by_escalation,
    summarise_by_tactic,
    write_csv,
    write_results,
)
from .model import ExperimentConfig


def _fmt(v: object) -> str:
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def main() -> None:
    p = argparse.ArgumentParser(description="Run claimant-standing CPU institutional simulation")
    p.add_argument("--episodes", type=int, default=20_000, help="number of shared scenarios")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--out", type=Path, default=Path("results"))
    p.add_argument("--full", action="store_true", help="write per-episode rows")
    p.add_argument(
        "--ablation-set",
        choices=("v0_2", "v0_2_1"),
        default="v0_2",
        help="ablation catalogue; v0_2 preserves the frozen result set",
    )
    args = p.parse_args()

    cfg = ExperimentConfig()
    rows, summary = run_experiment(args.episodes, args.seed, cfg)
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "summary.csv", summary)
    write_csv(args.out / "by_attack_budget.csv", summarise_by_attack_budget(rows))
    write_csv(args.out / "by_attack_tactic.csv", summarise_by_tactic(rows))
    write_csv(args.out / "by_capability_gap.csv", summarise_by_capability_gap(rows))
    write_csv(args.out / "by_dependency.csv", summarise_by_dependency(rows))
    write_csv(args.out / "by_escalation.csv", summarise_by_escalation(rows))
    if args.full:
        write_results(args.out / "episodes.csv", rows)

    ablation_rows, ablation_summary = run_ablations(args.episodes, args.seed, cfg, args.ablation_set)
    write_csv(args.out / "ablations.csv", ablation_summary)
    if args.full:
        write_results(args.out / "ablation_episodes.csv", ablation_rows)

    columns = [
        "condition",
        "final_merit_accuracy",
        "valid_claim_correction_rate",
        "false_claim_rejection_rate",
        "retained_route_rate_valid_claims",
        "strategic_escalation_rate",
        "mean_effective_route_cut_valid_claims",
        "mean_review_cost",
        "mean_claimant_harm",
        "mean_system_loss",
    ]
    print("\t".join(columns))
    for row in summary:
        print("\t".join(_fmt(row[c]) for c in columns))


if __name__ == "__main__":
    main()
