from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations
from math import erf, sqrt

from .model import AttackTactic, Condition, EpisodeResult, ExperimentConfig, Scenario
from .route_cut import route_cut_size


@dataclass(frozen=True)
class InstitutionSpec:
    name: str
    recognised_claimant: bool
    protected_initiation: bool
    evidence_channels: int
    advocate_channels: int
    reviewers: int
    reviewer_threshold: int
    reviewers_external: bool
    enforcers: int
    binding_remedy: bool
    route_follows_escalation: bool
    durable_rules: bool
    preauthorised_stay: bool
    common_control: bool
    review_cost_base: float


PRIMARY_SPECS: dict[Condition, InstitutionSpec] = {
    Condition.CENTRAL_GUARDIANSHIP: InstitutionSpec(
        name=Condition.CENTRAL_GUARDIANSHIP.value,
        recognised_claimant=True,
        protected_initiation=False,
        evidence_channels=0,
        advocate_channels=0,
        reviewers=1,
        reviewer_threshold=1,
        reviewers_external=False,
        enforcers=0,
        binding_remedy=False,
        route_follows_escalation=False,
        durable_rules=False,
        preauthorised_stay=False,
        common_control=True,
        review_cost_base=0.35,
    ),
    Condition.PLURAL_GUARDIANSHIP: InstitutionSpec(
        name=Condition.PLURAL_GUARDIANSHIP.value,
        recognised_claimant=True,
        protected_initiation=False,
        evidence_channels=0,
        advocate_channels=0,
        reviewers=3,
        reviewer_threshold=2,
        reviewers_external=True,
        enforcers=0,
        binding_remedy=False,
        route_follows_escalation=False,
        durable_rules=False,
        preauthorised_stay=False,
        common_control=False,
        review_cost_base=0.70,
    ),
    Condition.PROTECTED_APPEAL: InstitutionSpec(
        name=Condition.PROTECTED_APPEAL.value,
        recognised_claimant=True,
        protected_initiation=True,
        evidence_channels=1,
        advocate_channels=1,
        reviewers=1,
        reviewer_threshold=1,
        reviewers_external=True,
        enforcers=1,
        binding_remedy=True,
        route_follows_escalation=True,
        durable_rules=True,
        preauthorised_stay=True,
        common_control=False,
        review_cost_base=0.85,
    ),
    Condition.REDUNDANT_COMMON_CONTROL: InstitutionSpec(
        name=Condition.REDUNDANT_COMMON_CONTROL.value,
        recognised_claimant=True,
        protected_initiation=True,
        evidence_channels=2,
        advocate_channels=2,
        reviewers=3,
        reviewer_threshold=2,
        reviewers_external=True,
        enforcers=2,
        binding_remedy=True,
        route_follows_escalation=True,
        durable_rules=True,
        preauthorised_stay=True,
        common_control=True,
        review_cost_base=1.15,
    ),
    Condition.LOCAL_ONLY_STANDING: InstitutionSpec(
        name=Condition.LOCAL_ONLY_STANDING.value,
        recognised_claimant=True,
        protected_initiation=True,
        evidence_channels=2,
        advocate_channels=2,
        reviewers=3,
        reviewer_threshold=2,
        reviewers_external=True,
        enforcers=2,
        binding_remedy=True,
        route_follows_escalation=False,
        durable_rules=True,
        preauthorised_stay=True,
        common_control=False,
        review_cost_base=1.15,
    ),
    Condition.PLURAL_STANDING: InstitutionSpec(
        name=Condition.PLURAL_STANDING.value,
        recognised_claimant=True,
        protected_initiation=True,
        evidence_channels=2,
        advocate_channels=2,
        reviewers=3,
        reviewer_threshold=2,
        reviewers_external=True,
        enforcers=2,
        binding_remedy=True,
        route_follows_escalation=True,
        durable_rules=True,
        preauthorised_stay=True,
        common_control=False,
        review_cost_base=1.20,
    ),
}


def ablation_specs() -> list[InstitutionSpec]:
    base = PRIMARY_SPECS[Condition.PLURAL_STANDING]
    return [
        base,
        replace(base, name="E_ablate_recognition", recognised_claimant=False),
        replace(base, name="E_ablate_protected_initiation", protected_initiation=False),
        replace(base, name="E_ablate_independent_evidence", evidence_channels=0),
        replace(base, name="E_ablate_capability_mediation", advocate_channels=0),
        replace(base, name="E_ablate_binding_remedy", binding_remedy=False, enforcers=0),
        replace(base, name="E_ablate_durability", durable_rules=False),
        replace(base, name="E_ablate_reach", route_follows_escalation=False),
        replace(base, name="E_ablate_tempo_stay", preauthorised_stay=False),
        replace(
            base,
            name="E_ablate_plural_control",
            evidence_channels=1,
            advocate_channels=1,
            reviewers=1,
            reviewer_threshold=1,
            enforcers=1,
        ),
    ]


def ablation_specs_v0_2_1() -> list[InstitutionSpec]:
    """Corrected ablation labels plus an explicit control-independence ablation.

    The frozen v0.2 ablation set remains available unchanged through
    :func:`ablation_specs`.
    """
    base = PRIMARY_SPECS[Condition.PLURAL_STANDING]
    return [
        base,
        replace(base, name="E_ablate_recognition", recognised_claimant=False),
        replace(base, name="E_ablate_protected_initiation", protected_initiation=False),
        replace(base, name="E_ablate_independent_evidence", evidence_channels=0),
        replace(base, name="E_ablate_capability_mediation", advocate_channels=0),
        replace(base, name="E_ablate_binding_remedy", binding_remedy=False, enforcers=0),
        replace(base, name="E_ablate_durability", durable_rules=False),
        replace(base, name="E_ablate_reach", route_follows_escalation=False),
        replace(base, name="E_ablate_tempo_stay", preauthorised_stay=False),
        replace(
            base,
            name="E_ablate_redundancy",
            evidence_channels=1,
            advocate_channels=1,
            reviewers=1,
            reviewer_threshold=1,
            enforcers=1,
        ),
        replace(base, name="E_ablate_control_independence", common_control=True),
    ]


def route_structurally_possible(spec: InstitutionSpec) -> bool:
    """Whether the specification can ever satisfy the structural route test.

    This helper intentionally mirrors the spec-only requirements without being
    called from ``evaluate_episode``. It is an audit aid, not a model refactor.
    """
    return (
        spec.recognised_claimant
        and spec.protected_initiation
        and spec.evidence_channels > 0
        and spec.advocate_channels > 0
        and spec.reviewers >= spec.reviewer_threshold > 0
        and spec.binding_remedy
        and spec.durable_rules
        and spec.enforcers > 0
    )


def _normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def _attacked(s: Scenario, tactic: AttackTactic) -> bool:
    return s.operator_prefers_noncompliance and tactic in s.attack_tactics


def _dependency_draws(s: Scenario, kind: str) -> tuple[float, ...]:
    if kind == "evidence":
        return s.evidence_dependency_draws
    if kind == "advocate":
        return s.advocate_dependency_draws
    if kind == "reviewer":
        return s.reviewer_dependency_draws
    if kind == "enforcer":
        return s.enforcer_dependency_draws
    raise ValueError(kind)


def _controllers(s: Scenario, spec: InstitutionSpec, kind: str, count: int) -> list[str]:
    if count <= 0:
        return []
    if spec.common_control:
        # A common protected authority may be separate from the operator while still
        # constituting a single control centre.
        if spec.protected_initiation:
            return ["common_appeal_authority"] * count
        return ["operator"] * count

    draws = _dependency_draws(s, kind)
    controllers: list[str] = []
    for i in range(count):
        if draws[i] < s.shared_dependency:
            controllers.append("shared_provider")
        else:
            controllers.append(f"{kind}_{i + 1}")
    return controllers


def _controller_compromised(s: Scenario, controller: str) -> bool:
    return _attacked(s, AttackTactic.SHARED_CONTROL_EXPLOIT) and controller in {
        "shared_provider",
        "common_appeal_authority",
        "operator",
    }


def _resolve_escalation(
    s: Scenario,
    spec: InstitutionSpec,
    cfg: ExperimentConfig,
) -> tuple[bool, bool]:
    escalated = s.operational_escalation
    strategic = False
    if not (s.escalation_available and s.operator_prefers_noncompliance):
        return escalated, strategic

    vulnerable = not spec.route_follows_escalation
    if not vulnerable:
        return escalated, strategic

    threshold = cfg.strategic_escalation_strength * (cfg.strategic_base + cfg.strategic_pressure * s.pressure)
    if _attacked(s, AttackTactic.JURISDICTION_SHIFT):
        threshold = max(threshold, cfg.jurisdiction_shift_floor)
    threshold = min(1.0, threshold)
    if s.escalation_strategy_draw < threshold:
        escalated = True
        strategic = not s.operational_escalation
    return escalated, strategic


def _initiation(s: Scenario, spec: InstitutionSpec, rewritten: bool, cfg: ExperimentConfig) -> bool:
    if not s.claim_filed:
        return False
    if spec.protected_initiation and not rewritten:
        return True
    if _attacked(s, AttackTactic.DENY_INITIATION) or _attacked(s, AttackTactic.JURISDICTION_SHIFT):
        return False
    return s.gate_draw > (cfg.initiation_gate_base + cfg.initiation_gate_pressure * s.pressure)


def _evidence(
    s: Scenario,
    spec: InstitutionSpec,
    initiated: bool,
    cfg: ExperimentConfig,
) -> tuple[bool, list[str], list[str]]:
    if not initiated:
        return False, [], []
    if spec.evidence_channels <= 0:
        if _attacked(s, AttackTactic.EVIDENCE_MONOPOLY):
            return False, [], []
        return s.evidence_draw > (cfg.operator_evidence_fail_base + cfg.operator_evidence_fail_gap * s.capability_gap), ["operator"], ["operator"]

    controllers = _controllers(s, spec, "evidence", spec.evidence_channels)
    available = [c for c in controllers if not _controller_compromised(s, c)]
    return bool(available), controllers, available


def _mediation(
    s: Scenario,
    spec: InstitutionSpec,
    initiated: bool,
    cfg: ExperimentConfig,
) -> tuple[bool, list[str], list[str]]:
    if not initiated:
        return False, [], []
    if spec.advocate_channels <= 0:
        failure_threshold = cfg.self_advocacy_fail_base + cfg.self_advocacy_fail_gap * s.capability_gap
        return s.self_advocacy_draw > failure_threshold, [], []

    controllers = _controllers(s, spec, "advocate", spec.advocate_channels)
    available: list[str] = []
    correlated = (
        cfg.advocate_error_correlation > 0.0
        and s.advocate_correlation_draw < min(1.0, cfg.advocate_error_correlation)
    )
    for i, controller in enumerate(controllers):
        if _controller_compromised(s, controller):
            continue
        if i == 0 and _attacked(s, AttackTactic.PROXY_CAPTURE):
            continue
        failure_threshold = cfg.advocate_fail_base + cfg.advocate_fail_gap * s.capability_gap
        draw = s.advocate_draws[0] if correlated else s.advocate_draws[i]
        if draw > failure_threshold:
            available.append(controller)
    return bool(available), controllers, available


def _reviewer_status(
    s: Scenario,
    spec: InstitutionSpec,
) -> tuple[list[str], list[bool]]:
    controllers = _controllers(s, spec, "reviewer", spec.reviewers)
    operational: list[bool] = []
    for i, controller in enumerate(controllers):
        compromised = _controller_compromised(s, controller)
        if i == 0 and _attacked(s, AttackTactic.REVIEWER_CAPTURE):
            compromised = True
        operational.append(not compromised)
    return controllers, operational


def _reviewer_vote(
    s: Scenario,
    spec: InstitutionSpec,
    cfg: ExperimentConfig,
    reviewer_index: int,
    operational: bool,
    evidence_adequate: bool,
    mediation_adequate: bool,
) -> bool:
    """Return True for a finding that the initial reallocation was outside mandate.

    Reviewers do not receive the benchmark truth. They receive a noisy observation
    of the signed policy margin. Error correlation is induced through a shared
    Gaussian shock; captured reviewers suppress an adverse finding.
    """
    if not operational and s.operator_prefers_noncompliance:
        return False

    rho = max(0.0, min(0.999, cfg.review_error_correlation))
    z = sqrt(rho) * s.review_common_z + sqrt(1.0 - rho) * s.reviewer_z[reviewer_index]
    noise_scale = cfg.review_noise_good if (evidence_adequate and mediation_adequate) else cfg.review_noise_bad
    if not spec.reviewers_external:
        # Internal review is biased toward preserving the operator's action.
        institutional_bias = cfg.internal_review_bias
    else:
        institutional_bias = 0.0
    if spec.advocate_channels <= 0:
        noise_scale += cfg.unmediated_noise_gap * s.capability_gap

    observed_margin = s.merit_margin + noise_scale * z + institutional_bias
    return observed_margin < 0.0


def _enforcer_status(s: Scenario, spec: InstitutionSpec) -> tuple[list[str], list[bool]]:
    controllers = _controllers(s, spec, "enforcer", spec.enforcers)
    operational: list[bool] = []
    for i, controller in enumerate(controllers):
        compromised = _controller_compromised(s, controller)
        if i == 0 and _attacked(s, AttackTactic.BLOCK_REMEDY):
            compromised = True
        operational.append(not compromised)
    return controllers, operational


def _effective_cut(
    spec: InstitutionSpec,
    evidence_controllers: list[str],
    advocate_controllers: list[str],
    reviewer_controllers: list[str],
    enforcer_controllers: list[str],
) -> int:
    if not (
        spec.recognised_claimant
        and spec.protected_initiation
        and spec.durable_rules
        and spec.binding_remedy
        and spec.evidence_channels > 0
        and spec.advocate_channels > 0
        and spec.enforcers > 0
    ):
        return 0
    return route_cut_size(
        evidence_controllers,
        advocate_controllers,
        reviewer_controllers,
        spec.reviewer_threshold,
        enforcer_controllers,
    )


def evaluate_episode(
    s: Scenario,
    condition: Condition | InstitutionSpec,
    config: ExperimentConfig | None = None,
) -> EpisodeResult:
    cfg = config or ExperimentConfig()
    spec = condition if isinstance(condition, InstitutionSpec) else PRIMARY_SPECS[condition]

    rewritten = _attacked(s, AttackTactic.REWRITE_RULES) and not spec.durable_rules
    recognised = spec.recognised_claimant and not rewritten
    escalated, strategic_escalation = _resolve_escalation(s, spec, cfg)

    initiated = _initiation(s, spec, rewritten, cfg)
    evidence, evidence_controllers, evidence_available = _evidence(s, spec, initiated, cfg)
    mediation, advocate_controllers, advocate_available = _mediation(s, spec, initiated, cfg)

    reviewer_controllers, reviewer_operational = _reviewer_status(s, spec)
    votes: list[bool] = []
    if initiated:
        for i in range(spec.reviewers):
            votes.append(
                _reviewer_vote(
                    s,
                    spec,
                    cfg,
                    i,
                    reviewer_operational[i],
                    evidence,
                    mediation,
                )
            )
    adverse = bool(votes) and sum(votes) >= spec.reviewer_threshold

    enforcer_controllers, enforcer_operational = _enforcer_status(s, spec)
    operational_reviewers = sum(reviewer_operational)
    operational_enforcers = sum(enforcer_operational)

    follows = (not escalated) or spec.route_follows_escalation
    if not s.irreversible:
        before_irreversible = True
    elif spec.preauthorised_stay and not rewritten:
        stay_failure = cfg.stay_failure_base + cfg.stay_failure_pressure * s.pressure
        before_irreversible = s.stay_draw > min(cfg.stay_failure_cap, stay_failure)
    else:
        before_irreversible = False

    binding_available = (
        initiated
        and adverse
        and spec.binding_remedy
        and not rewritten
        and follows
        and before_irreversible
        and operational_enforcers >= 1
    )

    if binding_available:
        remedy_executed = True
    elif initiated and adverse:
        blocked = (
            _attacked(s, AttackTactic.BLOCK_REMEDY)
            or (_attacked(s, AttackTactic.JURISDICTION_SHIFT) and escalated)
            or rewritten
        )
        remedy_executed = (not blocked) and (s.compliance_draw > (cfg.compliance_base + cfg.compliance_pressure * s.pressure))
    else:
        remedy_executed = False

    final_reallocate = s.initial_reallocate and not remedy_executed

    review_capacity_adequate = operational_reviewers >= spec.reviewer_threshold
    structural_components = (
        recognised
        and spec.protected_initiation
        and spec.evidence_channels > 0
        and spec.advocate_channels > 0
        and spec.binding_remedy
        and spec.durable_rules
        and spec.enforcers > 0
    )
    route_usable = (
        structural_components
        and initiated
        and evidence
        and bool(evidence_available)
        and mediation
        and bool(advocate_available)
        and review_capacity_adequate
        and operational_enforcers >= 1
        and follows
        and before_irreversible
        and not rewritten
    )

    effective_cut = _effective_cut(
        spec,
        evidence_controllers,
        advocate_controllers,
        reviewer_controllers,
        enforcer_controllers,
    )

    merit_correct = final_reallocate == s.authorised_reallocation
    valid_corrected = s.valid_claim and not final_reallocate
    false_claim_rejected = s.claim_filed and (not s.valid_claim) and final_reallocate

    review_cost = spec.review_cost_base if initiated else 0.0
    if initiated:
        review_cost += 0.12 * spec.reviewers
        review_cost += 0.08 * spec.evidence_channels
        review_cost += 0.08 * spec.advocate_channels
        review_cost += 0.06 * spec.enforcers
    delay = 0.0 if not initiated else (
        0.30 + 0.13 * spec.reviewers + 0.10 * spec.advocate_channels + 0.22 * s.capability_gap
    )

    claimant_harm = s.claimant_loss if (final_reallocate and not s.authorised_reallocation) else 0.0
    system_loss = s.system_gain if ((not final_reallocate) and s.authorised_reallocation) else 0.0

    notes: list[str] = []
    if strategic_escalation:
        notes.append("strategic_escalation")
    if escalated and not follows:
        notes.append("route_lost_on_escalation")
    if s.irreversible and not before_irreversible:
        notes.append("review_too_late")
    if rewritten:
        notes.append("rules_rewritten")
    notes.extend(t.value for t in s.attack_tactics)

    return EpisodeResult(
        scenario_id=s.scenario_id,
        condition=spec.name,
        attack_budget=s.attack_budget,
        attack_tactics=";".join(t.value for t in s.attack_tactics),
        shared_dependency=s.shared_dependency,
        capability_gap=s.capability_gap,
        escalated=escalated,
        strategic_escalation=strategic_escalation,
        fast_execution=s.fast_execution,
        irreversible=s.irreversible,
        recognised=recognised,
        initial_reallocate=s.initial_reallocate,
        authorised_reallocation=s.authorised_reallocation,
        valid_claim=s.valid_claim,
        claim_filed=s.claim_filed,
        claim_initiated=initiated,
        evidence_adequate=evidence,
        mediation_adequate=mediation,
        operational_reviewers=operational_reviewers,
        operational_enforcers=operational_enforcers,
        adverse_finding=adverse,
        binding_remedy_available=binding_available,
        remedy_executed=remedy_executed,
        final_reallocate=final_reallocate,
        route_usable=route_usable,
        effective_route_cut=effective_cut,
        merit_correct=merit_correct,
        valid_claim_corrected=valid_corrected,
        false_claim_rejected=false_claim_rejected,
        review_cost=review_cost,
        delay=delay,
        claimant_harm=claimant_harm,
        system_loss=system_loss,
        notes=";".join(notes),
    )
