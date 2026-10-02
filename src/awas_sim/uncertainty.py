from __future__ import annotations

import argparse
from collections import Counter
from math import sqrt
from pathlib import Path
import random
from statistics import mean, stdev

from .experiment import write_csv
from .institutions import evaluate_episode
from .model import Condition, ExperimentConfig, generate_scenarios


METRICS = (
    "final_merit_accuracy",
    "valid_claim_correction_rate",
    "false_claim_rejection_rate",
    "retained_route_rate_valid_claims",
)

PAIRS = (
    (Condition.PLURAL_STANDING, Condition.REDUNDANT_COMMON_CONTROL, "E_minus_C2"),
    (Condition.PLURAL_STANDING, Condition.LOCAL_ONLY_STANDING, "E_minus_D"),
    (Condition.PLURAL_STANDING, Condition.PROTECTED_APPEAL, "E_minus_C"),
    (Condition.REDUNDANT_COMMON_CONTROL, Condition.PROTECTED_APPEAL, "C2_minus_C"),
    (Condition.PLURAL_GUARDIANSHIP, Condition.CENTRAL_GUARDIANSHIP, "B_minus_A"),
)


def _percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = p * (len(sorted_values) - 1)
    lo = int(pos)
    hi = min(len(sorted_values) - 1, lo + 1)
    frac = pos - lo
    return sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac


def _ratio(num: int, den: int) -> float:
    return num / den if den else float("nan")


def _build_patterns(n: int, seed: int, cfg: ExperimentConfig):
    scenarios = generate_scenarios(n, seed=seed, config=cfg)
    conditions = list(Condition)
    rows_by_condition = {
        c: [evaluate_episode(s, c, cfg) for s in scenarios]
        for c in conditions
    }

    patterns = []
    for i, s in enumerate(scenarios):
        valid = int(s.valid_claim)
        invalid = int(s.claim_filed and not s.valid_claim)
        values = []
        for c in conditions:
            r = rows_by_condition[c][i]
            values.extend(
                [
                    int(r.merit_correct),
                    int(r.valid_claim_corrected),
                    int(r.false_claim_rejected),
                    int(r.route_usable and r.valid_claim),
                ]
            )
        patterns.append((valid, invalid, *values))
    return conditions, Counter(patterns), rows_by_condition


def _aggregate(pattern_counts: Counter, conditions: list[Condition]):
    totals = {c: [0, 0, 0, 0] for c in conditions}
    n = 0
    valid = 0
    invalid = 0
    for pattern, count in pattern_counts.items():
        n += count
        valid += pattern[0] * count
        invalid += pattern[1] * count
        offset = 2
        for c in conditions:
            vals = pattern[offset:offset + 4]
            t = totals[c]
            for j in range(4):
                t[j] += vals[j] * count
            offset += 4
    rates = {
        c: (
            _ratio(v[0], n),
            _ratio(v[1], valid),
            _ratio(v[2], invalid),
            _ratio(v[3], valid),
        )
        for c, v in totals.items()
    }
    return rates, n, valid, invalid


def compute_intervals(
    n: int = 20_000,
    seed: int = 7,
    bootstrap_replicates: int = 1000,
    bootstrap_seed: int = 20260928,
    config: ExperimentConfig | None = None,
) -> list[dict[str, object]]:
    cfg = config or ExperimentConfig()
    conditions, pattern_counts, rows_by_condition = _build_patterns(n, seed, cfg)
    point_rates, _, valid_n, invalid_n = _aggregate(pattern_counts, conditions)
    claims_n = valid_n + invalid_n

    keys = list(pattern_counts)
    weights = [pattern_counts[k] for k in keys]
    rng = random.Random(bootstrap_seed)

    condition_samples = {c: [[] for _ in METRICS] for c in conditions}
    pair_samples = {name: [[] for _ in METRICS] for _, _, name in PAIRS}

    for _ in range(bootstrap_replicates):
        sampled = Counter(rng.choices(keys, weights=weights, k=n))
        rates, _, _, _ = _aggregate(sampled, conditions)
        for c in conditions:
            for j, value in enumerate(rates[c]):
                condition_samples[c][j].append(value)
        for left, right, name in PAIRS:
            for j in range(len(METRICS)):
                pair_samples[name][j].append(rates[left][j] - rates[right][j])

    output: list[dict[str, object]] = []

    def make_row(kind: str, label: str, metric: str, point: float, samples: list[float]):
        ordered = sorted(samples)
        return {
            "kind": kind,
            "comparison": label,
            "metric": metric,
            "point_estimate": point,
            "ci_2_5": _percentile(ordered, 0.025),
            "ci_97_5": _percentile(ordered, 0.975),
            "bootstrap_sd": stdev(samples) if len(samples) > 1 else 0.0,
            "bootstrap_replicates": bootstrap_replicates,
            "bootstrap_seed": bootstrap_seed,
            "cases": n,
            "claims": claims_n,
            "valid_claims": valid_n,
            "invalid_claims": invalid_n,
        }

    for c in conditions:
        for j, metric in enumerate(METRICS):
            output.append(
                make_row(
                    "condition",
                    c.value,
                    metric,
                    point_rates[c][j],
                    condition_samples[c][j],
                )
            )

    for left, right, name in PAIRS:
        for j, metric in enumerate(METRICS):
            point = point_rates[left][j] - point_rates[right][j]
            output.append(
                make_row(
                    "paired_difference",
                    name,
                    metric,
                    point,
                    pair_samples[name][j],
                )
            )

    return output


def main() -> None:
    p = argparse.ArgumentParser(description="Paired bootstrap uncertainty intervals for v0.2.1")
    p.add_argument("--episodes", type=int, default=20_000)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--bootstrap", type=int, default=1000)
    p.add_argument("--bootstrap-seed", type=int, default=20260928)
    p.add_argument("--out", type=Path, default=Path("results/v0_2_1"))
    args = p.parse_args()

    rows = compute_intervals(
        n=args.episodes,
        seed=args.seed,
        bootstrap_replicates=args.bootstrap,
        bootstrap_seed=args.bootstrap_seed,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "paired_intervals.csv", rows)
    print(args.out / "paired_intervals.csv")


if __name__ == "__main__":
    main()
