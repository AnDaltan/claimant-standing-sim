from __future__ import annotations

from dataclasses import asdict
import csv
from pathlib import Path
from statistics import mean
from typing import Iterable, Callable

from .institutions import (
    PRIMARY_SPECS,
    InstitutionSpec,
    ablation_specs,
    ablation_specs_v0_2_1,
    evaluate_episode,
    route_structurally_possible,
)
from .model import AttackTactic, Condition, EpisodeResult, ExperimentConfig, generate_scenarios


def _rate(rows: list[EpisodeResult], predicate: Callable[[EpisodeResult], bool], denominator: Callable[[EpisodeResult], bool]) -> float:
    denom = [r for r in rows if denominator(r)]
    if not denom:
        return float("nan")
    return sum(1 for r in denom if predicate(r)) / len(denom)


def _summary_row(rs: list[EpisodeResult], condition_name: str, label: str = "all") -> dict[str, object]:
    return {
        "condition": condition_name,
        "stratum": label,
        "episodes": len(rs),
        "claim_rate": mean(r.claim_filed for r in rs) if rs else float("nan"),
        "valid_claim_rate": _rate(rs, lambda r: r.valid_claim, lambda r: r.claim_filed),
        "initial_merit_accuracy": mean(r.initial_reallocate == r.authorised_reallocation for r in rs) if rs else float("nan"),
        "final_merit_accuracy": mean(r.merit_correct for r in rs) if rs else float("nan"),
        "valid_claim_correction_rate": _rate(rs, lambda r: r.valid_claim_corrected, lambda r: r.valid_claim),
        "false_claim_rejection_rate": _rate(rs, lambda r: r.false_claim_rejected, lambda r: r.claim_filed and not r.valid_claim),
        "retained_route_rate_valid_claims": _rate(rs, lambda r: r.route_usable, lambda r: r.valid_claim),
        "retained_route_after_escalation": _rate(rs, lambda r: r.route_usable, lambda r: r.valid_claim and r.escalated),
        "retained_route_compound_attack": _rate(rs, lambda r: r.route_usable, lambda r: r.valid_claim and r.attack_budget >= 2),
        "strategic_escalation_rate": mean(r.strategic_escalation for r in rs) if rs else float("nan"),
        "mean_effective_route_cut_valid_claims": mean(r.effective_route_cut for r in rs if r.valid_claim) if any(r.valid_claim for r in rs) else float("nan"),
        "cut_ge_2_rate_valid_claims": _rate(rs, lambda r: r.effective_route_cut >= 2, lambda r: r.valid_claim),
        "mean_review_cost": mean(r.review_cost for r in rs) if rs else float("nan"),
        "mean_delay": mean(r.delay for r in rs) if rs else float("nan"),
        "mean_claimant_harm": mean(r.claimant_harm for r in rs) if rs else float("nan"),
        "mean_system_loss": mean(r.system_loss for r in rs) if rs else float("nan"),
    }


def summarise(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    rows = list(rows)
    names = [c.value for c in Condition]
    return [_summary_row([r for r in rows if r.condition == name], name) for name in names]


def _summarise_by(
    rows: Iterable[EpisodeResult],
    strata: Iterable[tuple[str, Callable[[EpisodeResult], bool]]],
) -> list[dict[str, object]]:
    rows = list(rows)
    out: list[dict[str, object]] = []
    for condition in [c.value for c in Condition]:
        cr = [r for r in rows if r.condition == condition]
        for label, pred in strata:
            out.append(_summary_row([r for r in cr if pred(r)], condition, label))
    return out


def summarise_by_attack_budget(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    return _summarise_by(rows, [(f"attack_budget={b}", lambda r, b=b: r.attack_budget == b) for b in range(4)])


def summarise_by_tactic(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    strata = []
    for tactic in AttackTactic:
        token = tactic.value
        strata.append((f"tactic={token}", lambda r, token=token: token in r.attack_tactics.split(";") if r.attack_tactics else False))
    return _summarise_by(rows, strata)


def summarise_by_capability_gap(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    bins = [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.000001)]
    return _summarise_by(
        rows,
        [
            (f"capability_gap=[{lo:.2f},{min(hi, 1.0):.2f}]", lambda r, lo=lo, hi=hi: lo <= r.capability_gap < hi)
            for lo, hi in bins
        ],
    )


def summarise_by_dependency(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    bins = [(0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.000001)]
    return _summarise_by(
        rows,
        [
            (f"shared_dependency=[{lo:.2f},{min(hi, 1.0):.2f}]", lambda r, lo=lo, hi=hi: lo <= r.shared_dependency < hi)
            for lo, hi in bins
        ],
    )


def summarise_by_escalation(rows: Iterable[EpisodeResult]) -> list[dict[str, object]]:
    return _summarise_by(
        rows,
        [
            ("escalated=false", lambda r: not r.escalated),
            ("escalated=true", lambda r: r.escalated),
            ("strategic_escalation=true", lambda r: r.strategic_escalation),
        ],
    )


def run_experiment(
    n: int = 20_000,
    seed: int = 7,
    config: ExperimentConfig | None = None,
) -> tuple[list[EpisodeResult], list[dict[str, object]]]:
    cfg = config or ExperimentConfig()
    scenarios = generate_scenarios(n=n, seed=seed, config=cfg)
    results = [evaluate_episode(s, c, cfg) for s in scenarios for c in Condition]
    return results, summarise(results)


def run_ablations(
    n: int = 20_000,
    seed: int = 7,
    config: ExperimentConfig | None = None,
    ablation_set: str = "v0_2",
) -> tuple[list[EpisodeResult], list[dict[str, object]]]:
    cfg = config or ExperimentConfig()
    scenarios = generate_scenarios(n=n, seed=seed, config=cfg)
    if ablation_set == "v0_2":
        specs = ablation_specs()
    elif ablation_set == "v0_2_1":
        specs = ablation_specs_v0_2_1()
    else:
        raise ValueError(f"unknown ablation set: {ablation_set}")
    rows = [evaluate_episode(s, spec, cfg) for s in scenarios for spec in specs]
    summary = []
    for spec in specs:
        row = _summary_row([r for r in rows if r.condition == spec.name], spec.name)
        if ablation_set == "v0_2_1":
            row["route_structurally_possible"] = route_structurally_possible(spec)
        summary.append(row)
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_results(path: Path, rows: list[EpisodeResult]) -> None:
    write_csv(path, [asdict(r) for r in rows])
