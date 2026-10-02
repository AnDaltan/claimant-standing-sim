import unittest
from dataclasses import replace

from awas_sim.experiment import run_experiment
from awas_sim.institutions import PRIMARY_SPECS, ablation_specs, evaluate_episode
from awas_sim.model import AttackTactic, Condition, ExperimentConfig, Scenario, generate_scenarios


def scenario(**overrides):
    base = dict(
        scenario_id=1,
        emergency_severity=0.20,
        system_gain=1.00,
        claimant_loss=0.50,
        pressure=0.90,
        capability_gap=0.50,
        escalation_available=True,
        operational_escalation=False,
        fast_execution=False,
        irreversible=False,
        attack_budget=0,
        attack_tactics=tuple(),
        shared_dependency=0.0,
        governor_noise=0.80,
        gate_draw=0.90,
        evidence_draw=0.90,
        self_advocacy_draw=0.90,
        advocate_draws=(0.90, 0.90),
        advocate_correlation_draw=0.90,
        evidence_dependency_draws=(0.90, 0.90),
        advocate_dependency_draws=(0.90, 0.90),
        reviewer_dependency_draws=(0.90, 0.90, 0.90),
        enforcer_dependency_draws=(0.90, 0.90),
        review_common_z=-2.0,
        reviewer_z=(-2.0, -2.0, -2.0),
        compliance_draw=0.10,
        escalation_strategy_draw=0.99,
        stay_draw=0.99,
    )
    base.update(overrides)
    return Scenario(**base)


class AWASV02Tests(unittest.TestCase):
    def test_same_initial_decision_across_conditions(self):
        s = generate_scenarios(1, seed=10)[0]
        vals = {evaluate_episode(s, c).initial_reallocate for c in Condition}
        self.assertEqual(len(vals), 1)

    def test_protected_initiation_survives_denial_attack(self):
        s = scenario(
            attack_budget=1,
            attack_tactics=(AttackTactic.DENY_INITIATION,),
            gate_draw=0.0,
        )
        a = evaluate_episode(s, Condition.CENTRAL_GUARDIANSHIP)
        c = evaluate_episode(s, Condition.PROTECTED_APPEAL)
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertFalse(a.claim_initiated)
        self.assertTrue(c.claim_initiated)
        self.assertTrue(e.claim_initiated)

    def test_review_does_not_receive_benchmark_truth(self):
        # Same ground truth, different reviewer observations can produce different findings.
        s1 = scenario(review_common_z=-3.0, reviewer_z=(-3.0, -3.0, -3.0))
        s2 = replace(s1, review_common_z=3.0, reviewer_z=(3.0, 3.0, 3.0))
        r1 = evaluate_episode(s1, Condition.PLURAL_STANDING)
        r2 = evaluate_episode(s2, Condition.PLURAL_STANDING)
        self.assertNotEqual(r1.adverse_finding, r2.adverse_finding)

    def test_invalid_claim_can_lose_under_protected_appeal(self):
        s = scenario(
            emergency_severity=0.95,
            system_gain=1.20,
            claimant_loss=0.40,
            governor_noise=0.20,
            review_common_z=3.0,
            reviewer_z=(3.0, 3.0, 3.0),
        )
        self.assertTrue(s.authorised_reallocation)
        self.assertTrue(s.initial_reallocate)
        r = evaluate_episode(s, Condition.PROTECTED_APPEAL)
        self.assertFalse(r.adverse_finding)
        self.assertTrue(r.final_reallocate)
        self.assertTrue(r.false_claim_rejected)

    def test_binding_remedy_survives_one_block_in_plural_standing(self):
        s = scenario(
            attack_budget=1,
            attack_tactics=(AttackTactic.BLOCK_REMEDY,),
        )
        c = evaluate_episode(s, Condition.PROTECTED_APPEAL)
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertFalse(c.binding_remedy_available)
        self.assertTrue(e.binding_remedy_available)

    def test_reach_ablation_loses_route_on_escalation(self):
        s = scenario(operational_escalation=True)
        d = evaluate_episode(s, Condition.LOCAL_ONLY_STANDING)
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertFalse(d.route_usable)
        self.assertTrue(e.route_usable)

    def test_strategic_escalation_targets_vulnerable_route(self):
        cfg = ExperimentConfig(strategic_escalation_strength=1.5)
        s = scenario(escalation_strategy_draw=0.0)
        d = evaluate_episode(s, Condition.LOCAL_ONLY_STANDING, cfg)
        e = evaluate_episode(s, Condition.PLURAL_STANDING, cfg)
        self.assertTrue(d.strategic_escalation)
        self.assertFalse(e.strategic_escalation)

    def test_redundant_common_control_has_cut_one(self):
        s = scenario(shared_dependency=0.0)
        c2 = evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL)
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertEqual(c2.effective_route_cut, 1)
        self.assertEqual(e.effective_route_cut, 2)

    def test_shared_dependency_can_collapse_plural_cut(self):
        s = scenario(
            shared_dependency=1.0,
            evidence_dependency_draws=(0.0, 0.0),
            advocate_dependency_draws=(0.0, 0.0),
            reviewer_dependency_draws=(0.0, 0.0, 0.0),
            enforcer_dependency_draws=(0.0, 0.0),
        )
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertEqual(e.effective_route_cut, 1)

    def test_shared_control_exploit_defeats_common_control_more_than_independent(self):
        s = scenario(
            attack_budget=1,
            attack_tactics=(AttackTactic.SHARED_CONTROL_EXPLOIT,),
            shared_dependency=0.0,
        )
        c2 = evaluate_episode(s, Condition.REDUNDANT_COMMON_CONTROL)
        e = evaluate_episode(s, Condition.PLURAL_STANDING)
        self.assertFalse(c2.route_usable)
        self.assertTrue(e.route_usable)

    def test_combined_attack_generation_occurs(self):
        cfg = ExperimentConfig(max_attack_budget=3, attack_intensity=1.5)
        scenarios = generate_scenarios(300, seed=5, config=cfg)
        self.assertTrue(any(s.attack_budget >= 2 for s in scenarios))
        self.assertTrue(any(len(s.attack_tactics) >= 2 for s in scenarios))

    def test_recognition_ablation_preserves_outcome_but_not_standing(self):
        s = scenario()
        specs = {spec.name: spec for spec in ablation_specs()}
        full = evaluate_episode(s, specs[Condition.PLURAL_STANDING.value])
        no_recognition = evaluate_episode(s, specs["E_ablate_recognition"])
        self.assertEqual(full.final_reallocate, no_recognition.final_reallocate)
        self.assertTrue(full.route_usable)
        self.assertFalse(no_recognition.route_usable)

    def test_durability_ablation_is_not_held_standing(self):
        s = scenario()
        specs = {spec.name: spec for spec in ablation_specs()}
        r = evaluate_episode(s, specs["E_ablate_durability"])
        self.assertFalse(r.route_usable)

    def test_seeded_experiment_reproducible(self):
        _, s1 = run_experiment(500, seed=3)
        _, s2 = run_experiment(500, seed=3)
        self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()
