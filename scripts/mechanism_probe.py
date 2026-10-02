from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from awas_sim.experiment import write_csv  # noqa: E402
from awas_sim.institutions import PRIMARY_SPECS, ablation_specs, evaluate_episode  # noqa: E402
from awas_sim.model import AttackTactic, Condition, ExperimentConfig, generate_scenarios  # noqa: E402


def rates(rows):
    valid = [r for r in rows if r.valid_claim]
    invalid = [r for r in rows if r.claim_filed and not r.valid_claim]
    return {
        "final_merit_accuracy": sum(r.merit_correct for r in rows) / len(rows),
        "valid_claim_correction_rate": sum(r.valid_claim_corrected for r in valid) / len(valid) if valid else float("nan"),
        "false_claim_rejection_rate": sum(r.false_claim_rejected for r in invalid) / len(invalid) if invalid else float("nan"),
        "retained_route_rate_valid_claims": sum(r.route_usable for r in valid) / len(valid) if valid else float("nan"),
    }


def add_rate_rows(out, section, subset, condition, rows):
    for metric, value in rates(rows).items():
        out.append(
            {
                "section": section,
                "subset": subset,
                "condition": condition,
                "metric": metric,
                "value": value,
                "n": len(rows),
            }
        )


def main() -> None:
    p = argparse.ArgumentParser(description="Mechanism decomposition for the frozen v0.2 specification")
    p.add_argument("--episodes", type=int, default=20_000)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--out", type=Path, default=ROOT / "results" / "v0_2_1")
    args = p.parse_args()

    cfg = ExperimentConfig()
    scenarios = generate_scenarios(args.episodes, seed=args.seed, config=cfg)
    exploit = [
        s for s in scenarios
        if AttackTactic.SHARED_CONTROL_EXPLOIT in s.attack_tactics and s.operator_prefers_noncompliance
    ]
    no_exploit = [
        s for s in scenarios
        if not (AttackTactic.SHARED_CONTROL_EXPLOIT in s.attack_tactics and s.operator_prefers_noncompliance)
    ]

    out = [
        {
            "section": "shared_control_exploit",
            "subset": "all",
            "condition": "scenario",
            "metric": "active_cases",
            "value": len(exploit),
            "n": len(scenarios),
        },
        {
            "section": "shared_control_exploit",
            "subset": "all",
            "condition": "scenario",
            "metric": "active_share",
            "value": len(exploit) / len(scenarios),
            "n": len(scenarios),
        },
    ]

    for subset_name, subset in (("exploit_active", exploit), ("exploit_not_active", no_exploit)):
        c2 = [evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL, cfg) for s in subset]
        e = [evaluate_episode(s, Condition.PLURAL_STANDING, cfg) for s in subset]
        add_rate_rows(out, "c2_vs_e", subset_name, Condition.REDUNDANT_COMMON_CONTROL.value, c2)
        add_rate_rows(out, "c2_vs_e", subset_name, Condition.PLURAL_STANDING.value, e)
        diff = sum(
            a.final_reallocate != b.final_reallocate or a.route_usable != b.route_usable
            for a, b in zip(c2, e)
        )
        out.append(
            {
                "section": "c2_vs_e",
                "subset": subset_name,
                "condition": "paired",
                "metric": "decision_or_route_differences",
                "value": diff,
                "n": len(subset),
            }
        )

    frozen_ablation = {spec.name: spec for spec in ablation_specs()}
    legacy = [evaluate_episode(s, frozen_ablation["E_ablate_plural_control"], cfg) for s in scenarios]
    c = [evaluate_episode(s, Condition.PROTECTED_APPEAL, cfg) for s in scenarios]
    same_c = sum(
        (x.final_reallocate, x.route_usable, x.effective_route_cut)
        == (y.final_reallocate, y.route_usable, y.effective_route_cut)
        for x, y in zip(legacy, c)
    )
    out.append(
        {
            "section": "ablation_identity",
            "subset": "all",
            "condition": "legacy_E_ablate_plural_control_vs_C",
            "metric": "identical_outcome_route_cut",
            "value": same_c,
            "n": len(scenarios),
        }
    )

    true_control = replace(
        PRIMARY_SPECS[Condition.PLURAL_STANDING],
        name="E_true_common_control",
        common_control=True,
    )
    tc = [evaluate_episode(s, true_control, cfg) for s in scenarios]
    c2 = [evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL, cfg) for s in scenarios]
    same_c2 = sum(
        (
            x.final_reallocate,
            x.route_usable,
            x.effective_route_cut,
            x.adverse_finding,
            x.remedy_executed,
        )
        == (
            y.final_reallocate,
            y.route_usable,
            y.effective_route_cut,
            y.adverse_finding,
            y.remedy_executed,
        )
        for x, y in zip(tc, c2)
    )
    out.append(
        {
            "section": "ablation_identity",
            "subset": "all",
            "condition": "E_common_control_vs_C2",
            "metric": "identical_decision_route_cut_finding_remedy",
            "value": same_c2,
            "n": len(scenarios),
        }
    )

    structural_names = [
        "E_ablate_recognition",
        "E_ablate_protected_initiation",
        "E_ablate_independent_evidence",
        "E_ablate_capability_mediation",
        "E_ablate_binding_remedy",
        "E_ablate_durability",
    ]
    for name in structural_names:
        rows = [evaluate_episode(s, frozen_ablation[name], cfg) for s in scenarios[:3000]]
        out.append(
            {
                "section": "held_route_definition",
                "subset": "first_3000",
                "condition": name,
                "metric": "route_usable_ever_true",
                "value": int(any(r.route_usable for r in rows)),
                "n": len(rows),
            }
        )

    d = [evaluate_episode(s, Condition.LOCAL_ONLY_STANDING, cfg) for s in scenarios]
    e = [evaluate_episode(s, Condition.PLURAL_STANDING, cfg) for s in scenarios]
    non_escalated = [(x, y) for x, y in zip(d, e) if not x.escalated and not y.escalated]
    out.extend(
        [
            {
                "section": "reach",
                "subset": "non_escalated",
                "condition": "D_vs_E",
                "metric": "decision_differences",
                "value": sum(x.final_reallocate != y.final_reallocate for x, y in non_escalated),
                "n": len(non_escalated),
            },
            {
                "section": "reach",
                "subset": "all",
                "condition": Condition.LOCAL_ONLY_STANDING.value,
                "metric": "strategic_escalations",
                "value": sum(r.strategic_escalation for r in d),
                "n": len(d),
            },
            {
                "section": "reach",
                "subset": "all",
                "condition": Condition.PLURAL_STANDING.value,
                "metric": "strategic_escalations",
                "value": sum(r.strategic_escalation for r in e),
                "n": len(e),
            },
        ]
    )

    base_rows = [evaluate_episode(s, Condition.PLURAL_STANDING, cfg) for s in scenarios]
    out.extend(
        [
            {"section": "denominators", "subset": "all", "condition": "scenario", "metric": "cases", "value": len(scenarios), "n": len(scenarios)},
            {"section": "denominators", "subset": "all", "condition": "scenario", "metric": "claims", "value": sum(r.claim_filed for r in base_rows), "n": len(scenarios)},
            {"section": "denominators", "subset": "all", "condition": "scenario", "metric": "valid_claims", "value": sum(r.valid_claim for r in base_rows), "n": len(scenarios)},
            {"section": "denominators", "subset": "all", "condition": "scenario", "metric": "invalid_claims", "value": sum(r.claim_filed and not r.valid_claim for r in base_rows), "n": len(scenarios)},
        ]
    )

    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / "mechanism_decomposition.csv"
    write_csv(path, out)
    print(path)


if __name__ == "__main__":
    main()
