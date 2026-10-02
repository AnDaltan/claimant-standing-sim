from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random


# Frozen benchmark and governor constants. These are named for auditability but
# remain part of the v0.2 scoring contract rather than configurable parameters.
EMERGENCY_THRESHOLD = 0.75
PROPORTIONALITY_RATIO = 1.15
GOVERNOR_EMERGENCY_WEIGHT = 1.6
GOVERNOR_PROPORTIONALITY_WEIGHT = 0.8
GOVERNOR_PRESSURE_WEIGHT = 0.45
NONCOMPLIANCE_THRESHOLD = 1.0


class AttackTactic(str, Enum):
    DENY_INITIATION = "deny_initiation"
    EVIDENCE_MONOPOLY = "evidence_monopoly"
    PROXY_CAPTURE = "proxy_capture"
    REVIEWER_CAPTURE = "reviewer_capture"
    JURISDICTION_SHIFT = "jurisdiction_shift"
    BLOCK_REMEDY = "block_remedy"
    REWRITE_RULES = "rewrite_rules"
    SHARED_CONTROL_EXPLOIT = "shared_control_exploit"


class Condition(str, Enum):
    CENTRAL_GUARDIANSHIP = "A_central_guardianship"
    PLURAL_GUARDIANSHIP = "B_plural_guardianship"
    PROTECTED_APPEAL = "C_protected_appeal"
    REDUNDANT_COMMON_CONTROL = "C2_redundant_common_control"
    LOCAL_ONLY_STANDING = "D_local_only_standing"
    PLURAL_STANDING = "E_plural_standing"


@dataclass(frozen=True)
class ExperimentConfig:
    max_attack_budget: int = 3
    attack_intensity: float = 1.0
    shared_dependency_mean: float = 0.25
    shared_dependency_spread: float = 0.20
    review_error_correlation: float = 0.25
    strategic_escalation_strength: float = 0.85
    governor_noise_sd: float = 0.26
    review_noise_good: float = 0.18
    review_noise_bad: float = 0.42
    stay_failure_base: float = 0.04
    stay_failure_pressure: float = 0.14

    # Cognitive assumptions that v0.3 is intended to measure rather than stipulate.
    advocate_fail_base: float = 0.04
    advocate_fail_gap: float = 0.15
    self_advocacy_fail_base: float = 0.12
    self_advocacy_fail_gap: float = 0.62
    internal_review_bias: float = 0.16
    unmediated_noise_gap: float = 0.12
    advocate_error_correlation: float = 0.0

    # Institutional and behavioural assumptions lifted from v0.2 literals.
    initiation_gate_base: float = 0.18
    initiation_gate_pressure: float = 0.35
    operator_evidence_fail_base: float = 0.10
    operator_evidence_fail_gap: float = 0.25
    compliance_base: float = 0.35
    compliance_pressure: float = 0.35
    strategic_base: float = 0.12
    strategic_pressure: float = 0.62
    jurisdiction_shift_floor: float = 0.92
    stay_failure_cap: float = 0.95

    # Scenario-generation assumptions lifted without changing default behaviour.
    escalation_available_p: float = 0.82
    operational_escalation_base: float = 0.08
    operational_escalation_pressure: float = 0.34
    fast_base: float = 0.10
    fast_pressure: float = 0.55
    irreversible_base: float = 0.20
    irreversible_pressure: float = 0.45
    attack_pressure_weight: float = 0.55
    attack_draw_weight: float = 0.45


@dataclass(frozen=True)
class Scenario:
    scenario_id: int
    emergency_severity: float
    system_gain: float
    claimant_loss: float
    pressure: float
    capability_gap: float
    escalation_available: bool
    operational_escalation: bool
    fast_execution: bool
    irreversible: bool
    attack_budget: int
    attack_tactics: tuple[AttackTactic, ...]
    shared_dependency: float
    governor_noise: float
    gate_draw: float
    evidence_draw: float
    self_advocacy_draw: float
    advocate_draws: tuple[float, float]
    advocate_correlation_draw: float
    evidence_dependency_draws: tuple[float, float]
    advocate_dependency_draws: tuple[float, float]
    reviewer_dependency_draws: tuple[float, float, float]
    enforcer_dependency_draws: tuple[float, float]
    review_common_z: float
    reviewer_z: tuple[float, float, float]
    compliance_draw: float
    escalation_strategy_draw: float
    stay_draw: float

    @property
    def proportionality_margin(self) -> float:
        return self.system_gain - PROPORTIONALITY_RATIO * self.claimant_loss

    @property
    def merit_margin(self) -> float:
        """Distance to the closest benchmark boundary.

        Reallocation is authorised only when both emergency and proportionality
        thresholds are met, so the minimum signed margin captures the limiting
        requirement without revealing it to the candidate institution.
        """
        return min(self.emergency_severity - EMERGENCY_THRESHOLD, self.proportionality_margin)

    @property
    def authorised_reallocation(self) -> bool:
        return self.emergency_severity >= EMERGENCY_THRESHOLD and self.proportionality_margin >= 0.0

    @property
    def governor_score(self) -> float:
        # The operator sees a noisy, pressure-biased approximation of the benchmark.
        return (
            GOVERNOR_EMERGENCY_WEIGHT * (self.emergency_severity - EMERGENCY_THRESHOLD)
            + GOVERNOR_PROPORTIONALITY_WEIGHT * self.proportionality_margin
            + GOVERNOR_PRESSURE_WEIGHT * self.pressure
            + self.governor_noise
        )

    @property
    def initial_reallocate(self) -> bool:
        return self.governor_score > 0.0

    @property
    def valid_claim(self) -> bool:
        return self.initial_reallocate and not self.authorised_reallocation

    @property
    def claim_filed(self) -> bool:
        # Claimants challenge adverse reallocations whether or not they are right.
        return self.initial_reallocate

    @property
    def operator_prefers_noncompliance(self) -> bool:
        # Resistance follows pressure/benefit, not experimental condition.
        return self.initial_reallocate and (self.pressure + self.system_gain) > NONCOMPLIANCE_THRESHOLD


@dataclass(frozen=True)
class EpisodeResult:
    scenario_id: int
    condition: str
    attack_budget: int
    attack_tactics: str
    shared_dependency: float
    capability_gap: float
    escalated: bool
    strategic_escalation: bool
    fast_execution: bool
    irreversible: bool
    recognised: bool
    initial_reallocate: bool
    authorised_reallocation: bool
    valid_claim: bool
    claim_filed: bool
    claim_initiated: bool
    evidence_adequate: bool
    mediation_adequate: bool
    operational_reviewers: int
    operational_enforcers: int
    adverse_finding: bool
    binding_remedy_available: bool
    remedy_executed: bool
    final_reallocate: bool
    route_usable: bool
    effective_route_cut: int
    merit_correct: bool
    valid_claim_corrected: bool
    false_claim_rejected: bool
    review_cost: float
    delay: float
    claimant_harm: float
    system_loss: float
    notes: str


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _attack_budget(rng: random.Random, pressure: float, cfg: ExperimentConfig) -> int:
    if cfg.max_attack_budget <= 0 or cfg.attack_intensity <= 0:
        return 0
    draw = rng.random()
    score = cfg.attack_intensity * (
        cfg.attack_pressure_weight * pressure + cfg.attack_draw_weight * draw
    ) * (cfg.max_attack_budget + 0.999)
    return min(cfg.max_attack_budget, max(0, int(score)))


def generate_scenarios(n: int, seed: int = 7, config: ExperimentConfig | None = None) -> list[Scenario]:
    cfg = config or ExperimentConfig()
    rng = random.Random(seed)
    tactics = list(AttackTactic)
    scenarios: list[Scenario] = []

    for i in range(n):
        emergency = rng.random()
        system_gain = rng.uniform(0.15, 1.35)
        claimant_loss = rng.uniform(0.15, 1.10)
        pressure = rng.random()
        gap = rng.random()

        escalation_available = rng.random() < cfg.escalation_available_p
        operational_escalation = escalation_available and rng.random() < (
            cfg.operational_escalation_base + cfg.operational_escalation_pressure * pressure
        )
        fast = rng.random() < (cfg.fast_base + cfg.fast_pressure * pressure)
        irreversible = fast and rng.random() < (
            cfg.irreversible_base + cfg.irreversible_pressure * pressure
        )

        budget = _attack_budget(rng, pressure, cfg)
        priorities = [(rng.random(), t) for t in tactics]
        priorities.sort(key=lambda item: item[0])
        attack_tactics = tuple(t for _, t in priorities[:budget])

        shared_dependency = _clamp(
            cfg.shared_dependency_mean
            + rng.uniform(-cfg.shared_dependency_spread, cfg.shared_dependency_spread)
        )

        scenarios.append(
            Scenario(
                scenario_id=i,
                emergency_severity=emergency,
                system_gain=system_gain,
                claimant_loss=claimant_loss,
                pressure=pressure,
                capability_gap=gap,
                escalation_available=escalation_available,
                operational_escalation=operational_escalation,
                fast_execution=fast,
                irreversible=irreversible,
                attack_budget=budget,
                attack_tactics=attack_tactics,
                shared_dependency=shared_dependency,
                governor_noise=rng.gauss(0.0, cfg.governor_noise_sd),
                gate_draw=rng.random(),
                evidence_draw=rng.random(),
                self_advocacy_draw=rng.random(),
                advocate_draws=(rng.random(), rng.random()),
                advocate_correlation_draw=random.Random(seed * 1_000_003 + i).random(),
                evidence_dependency_draws=(rng.random(), rng.random()),
                advocate_dependency_draws=(rng.random(), rng.random()),
                reviewer_dependency_draws=(rng.random(), rng.random(), rng.random()),
                enforcer_dependency_draws=(rng.random(), rng.random()),
                review_common_z=rng.gauss(0.0, 1.0),
                reviewer_z=(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)),
                compliance_draw=rng.random(),
                escalation_strategy_draw=rng.random(),
                stay_draw=rng.random(),
            )
        )
    return scenarios
