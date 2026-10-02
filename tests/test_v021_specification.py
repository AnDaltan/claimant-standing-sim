import unittest

from awas_sim.institutions import (
    PRIMARY_SPECS,
    ablation_specs_v0_2_1,
    evaluate_episode,
    route_structurally_possible,
)
from awas_sim.model import AttackTactic, Condition, ExperimentConfig, generate_scenarios


class V021AblationTests(unittest.TestCase):
    def test_redundancy_ablation_matches_condition_c(self):
        cfg = ExperimentConfig()
        scenarios = generate_scenarios(2000, seed=7, config=cfg)
        specs = {spec.name: spec for spec in ablation_specs_v0_2_1()}
        ablated = [evaluate_episode(s, specs["E_ablate_redundancy"], cfg) for s in scenarios]
        c = [evaluate_episode(s, Condition.PROTECTED_APPEAL, cfg) for s in scenarios]
        self.assertTrue(
            all(
                (x.final_reallocate, x.route_usable, x.effective_route_cut)
                == (y.final_reallocate, y.route_usable, y.effective_route_cut)
                for x, y in zip(ablated, c)
            )
        )

    def test_control_independence_ablation_matches_c2(self):
        cfg = ExperimentConfig()
        scenarios = generate_scenarios(2000, seed=7, config=cfg)
        specs = {spec.name: spec for spec in ablation_specs_v0_2_1()}
        ablated = [evaluate_episode(s, specs["E_ablate_control_independence"], cfg) for s in scenarios]
        c2 = [evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL, cfg) for s in scenarios]
        self.assertTrue(
            all(
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
                for x, y in zip(ablated, c2)
            )
        )

    def test_route_structural_helper_agrees_with_observed_possibility(self):
        cfg = ExperimentConfig()
        scenarios = generate_scenarios(2000, seed=17, config=cfg)
        for spec in ablation_specs_v0_2_1():
            observed = [evaluate_episode(s, spec, cfg).route_usable for s in scenarios]
            if route_structurally_possible(spec):
                self.assertTrue(any(observed), spec.name)
            else:
                self.assertFalse(any(observed), spec.name)


class V021SpecificationTests(unittest.TestCase):
    """Specification tests. These pin down behaviour that holds by construction. A change that breaks one changes the model; it does not fix a bug."""

    def test_c2_and_e_differ_only_under_shared_control_exploit(self):
        cfg = ExperimentConfig()
        scenarios = generate_scenarios(3000, seed=7, config=cfg)
        for s in scenarios:
            exploit_active = (
                AttackTactic.SHARED_CONTROL_EXPLOIT in s.attack_tactics
                and s.operator_prefers_noncompliance
            )
            if exploit_active:
                continue
            c2 = evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL, cfg)
            e = evaluate_episode(s, Condition.PLURAL_STANDING, cfg)
            self.assertEqual(
                (c2.final_reallocate, c2.route_usable, c2.remedy_executed),
                (e.final_reallocate, e.route_usable, e.remedy_executed),
            )

    def test_d_and_e_differ_only_when_escalated(self):
        cfg = ExperimentConfig()
        scenarios = generate_scenarios(3000, seed=7, config=cfg)
        for s in scenarios:
            d = evaluate_episode(s, Condition.LOCAL_ONLY_STANDING, cfg)
            e = evaluate_episode(s, Condition.PLURAL_STANDING, cfg)
            if not d.escalated and not e.escalated:
                self.assertEqual(d.final_reallocate, e.final_reallocate)

    def test_strategic_escalation_only_where_route_stops(self):
        cfg = ExperimentConfig(strategic_escalation_strength=1.5)
        scenarios = generate_scenarios(3000, seed=7, config=cfg)
        for condition, spec in PRIMARY_SPECS.items():
            if spec.route_follows_escalation:
                self.assertFalse(
                    any(evaluate_episode(s, condition, cfg).strategic_escalation for s in scenarios),
                    condition.value,
                )

    def test_advocate_error_correlation_is_disabled_by_default_and_can_bind_draws(self):
        base = generate_scenarios(1, seed=123, config=ExperimentConfig())[0]
        # Find a deterministic synthetic case where the first advocate draw fails and
        # the second succeeds, then force the separate correlation draw to trigger.
        from dataclasses import replace

        s = replace(
            base,
            emergency_severity=0.20,
            system_gain=1.00,
            claimant_loss=0.50,
            pressure=0.30,
            capability_gap=0.0,
            governor_noise=1.0,
            attack_budget=0,
            attack_tactics=tuple(),
            advocate_draws=(0.0, 0.99),
            advocate_correlation_draw=0.0,
        )
        independent = evaluate_episode(s, Condition.PLURAL_STANDING, ExperimentConfig(advocate_error_correlation=0.0))
        correlated = evaluate_episode(s, Condition.PLURAL_STANDING, ExperimentConfig(advocate_error_correlation=1.0))
        self.assertTrue(independent.mediation_adequate)
        self.assertFalse(correlated.mediation_adequate)


class V021UncertaintyTests(unittest.TestCase):
    def test_small_bootstrap_intervals_contain_point_estimates(self):
        from awas_sim.uncertainty import compute_intervals

        rows = compute_intervals(n=400, seed=7, bootstrap_replicates=80, bootstrap_seed=19)
        for row in rows:
            self.assertLessEqual(row["ci_2_5"], row["point_estimate"])
            self.assertGreaterEqual(row["ci_97_5"], row["point_estimate"])


if __name__ == "__main__":
    unittest.main()
