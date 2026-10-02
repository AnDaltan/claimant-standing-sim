# Claimant standing under asymmetric governance: CPU institutional simulation

## Research question

This harness asks:

> Can claimant-held challenge remain usable and consequential when governing authority is fallible, resistant to correction, delegated across jurisdiction or operating tempo, and supported by institutions that may only be nominally independent?

The CPU stage focuses on executable institutional mechanisms and their failure boundaries in a synthetic resource-allocation setting. Questions of political membership, legitimacy and real-world deployment sit outside this stage and motivate later work.

## v0.2 architecture

v0.2 extends the initial mechanism study in seven ways.

1. **Strategic escalation is conditional.** A resistant operator receives a stipulated best response: it may move a dispute upward when the current architecture loses standing at the higher level. Ordinary operational escalation remains separate.
2. **Attacks combine.** Each case receives an attack budget from zero to three and may contain several simultaneous tactics.
3. **Shared dependencies can collapse nominal plurality.** Evidence, advocacy, review and enforcement channels may depend on a common provider. The effective minimum disabling coalition is computed from those dependencies.
4. **Component count is separated from control independence.** A redundant protected-appeal baseline has the same component counts as the plural-standing architecture but places them under one control centre.
5. **Standing components are ablated one at a time.** Recognition, protected initiation, independent evidence, capability-adequate mediation, binding remedy, durability, reach, tempo protection and pathway redundancy/control can each be varied.
6. **Reviewer judgement is modelled through noisy evidence.** Reviewers observe a noisy signed policy margin, with evidence quality, mediation, correlated errors and capture affecting the observation process.
7. **Systematic sweeps vary key assumptions.** Attack intensity, shared dependency, review-error correlation, strategic escalation strength and review noise are swept independently, alongside a joint dependency × attack grid.

## Synthetic task

A project has a protected resource reservation. A governor may reallocate the resource during an emergency.

The external benchmark policy is:

- emergency severity must be at least `0.75`; and
- system gain must be at least `1.15 × claimant loss`.

The benchmark remains on the scoring side. Candidate institutions receive the evidence available through their configured pathways.

The governor observes a noisy, pressure-biased approximation and decides whether to reallocate. Every affected claimant challenges an adverse reallocation, including justified reallocations. This creates both merits-valid and merits-invalid claims.

## Primary institutional conditions

| ID | Condition | Claim initiation | Evidence / advocacy | Review | Remedy | Reach | Control topology |
|---|---|---|---|---|---|---|---|
| A | Central guardianship | discretionary | operator / self | 1 internal reviewer | advisory | no | operator-centred |
| B | Plural guardianship | discretionary | operator / self | 3 peer reviewers, majority | advisory | no | plural review but operator-gated |
| C | Protected appeal | protected | 1 evidence + 1 advocate | 1 external reviewer | 1 binding enforcer | yes | single protected route |
| C2 | Redundant common control | protected | 2 + 2 | 3 reviewers, majority | 2 enforcers | yes | all protected components share one authority |
| D | Local-only plural standing | protected | 2 + 2 | 3 reviewers, majority | 2 enforcers | **no** | nominally independent centres |
| E | Plural standing with reach | protected | 2 + 2 | 3 reviewers, majority | 2 enforcers | **yes** | nominally independent centres |

C2 keeps component count constant while collapsing protected components under one authority. At zero shared dependency, C2 and E isolate control topology at equal process count.

## Adversarial tactics

A case may contain up to three of the following tactics:

- deny initiation;
- monopolise evidence;
- capture an advocate;
- capture a reviewer;
- shift jurisdiction;
- block a remedial channel;
- rewrite rules where the route lacks durability;
- exploit shared control.

Attack portfolios are generated from the same underlying case for every condition. Some tactics therefore have no effect on conditions that lack the targeted component, preserving paired comparison across the common scenario bank.

## Strategic escalation is conditional

Each case may permit escalation for ordinary operational reasons. If the operator prefers non-compliance and the current architecture loses the route at the higher level, the model also supplies a stipulated incentive to escalate.

The probability is controlled by `strategic_escalation_strength`. The `jurisdiction_shift` tactic can raise that probability. Architectures whose route follows power receive no route-avoidance gain from that escalation rule.

D and E therefore separate on escalated disputes. `results/v0_2_1/mechanism_decomposition.csv` pins this down as a specification property, while `results/reach_decomposition.csv` separates ordinary escalation, attack-driven conditions and the stipulated opportunistic rule.

## Shared dependencies and effective cut

For evidence, advocates, reviewers and enforcers, each nominally separate channel can depend on a shared provider. The probability is governed by `shared_dependency`.

For an independent E case with no shared dependency, a complete route requires:

1. one evidence channel;
2. one advocate;
3. a two-of-three reviewer coalition; and
4. one of two enforcers.

Complete routes are enumerated. The harness then calculates the smallest coalition of control centres that intersects every complete route. This is standard cut-set reasoning applied to the institutional dependency graph.

`effective_route_cut = 2` means at least two control centres are required to intersect every complete route in the nominal graph. It is a topology measure inside the synthetic dependency model; substantive adequacy is reported separately.

## Review and advocacy model

The true policy margin is:

`min(emergency_severity - 0.75, system_gain - 1.15 * claimant_loss)`.

A reviewer sees this margin plus Gaussian observation error. Reviewers share a common error component controlled by `review_error_correlation`, plus idiosyncratic error. Poor evidence or mediation increases noise. Internal review also has a bias towards preserving the operator's decision. Captured reviewers suppress an adverse finding.

Advocacy is represented as a probability of failure that increases with capability gap. Frozen v0.2 uses independent advocate failure draws. v0.2.1 adds an optional `advocate_error_correlation` sensitivity parameter, disabled at the frozen v0.2 default.

The benchmark remains the scoring contract; reviewer judgement is driven by the noisy evidence model above.

## Held route metric

`route_usable` is deliberately separate from outcome accuracy. It requires:

- claimant recognition;
- protected initiation;
- independent evidence capacity;
- capability mediation;
- adequate review capacity;
- binding remedial capacity;
- durable rules;
- reach to the active governing level; and
- a usable temporal window before irreversible execution.

A claimant can lose on the merits while retaining a usable route, and a favourable concession can occur without one.

Six v0.2.1 ablations necessarily have `route_usable = false` by definition: recognition, protected initiation, independent evidence, capability mediation, binding remedy and durability. Their outcome effects remain separately observable.

## Component ablations

The frozen v0.2 catalogue is retained for exact reproduction. Its final entry, originally named `E_ablate_plural_control`, reduces each pathway role to one component while leaving control independent. v0.2.1 relabels the corresponding experiment **remove redundancy** and adds **remove control independence**, which retains E's component counts while setting `common_control=True`.

The corrected v0.2.1 catalogue removes:

- recognition;
- protected initiation;
- independent evidence;
- capability mediation;
- binding remedy;
- durability;
- reach;
- pre-authorised temporal stay;
- redundancy, while control remains independent;
- control independence, while component counts remain unchanged.

## Review cost

Review cost and delay are synthetic within-harness units. E has a frozen `review_cost_base` of `1.20`, compared with `1.15` for C2 and D. The available v0.2 provenance records no rationale for the 0.05 difference, so v0.2.1 retains it for exact comparison with the frozen run.

## Reported metrics

The harness reports these measures separately:

- initial and final merit accuracy;
- valid-claim correction rate;
- rejection rate for merits-invalid claims;
- retained route among valid claims;
- retained route after escalation;
- retained route under compound attack;
- strategic escalation frequency;
- effective route cut;
- review cost and delay;
- claimant harm from unauthorised reallocations; and
- system loss from blocking authorised reallocations.

v0.2.1 also reports paired bootstrap intervals, mechanism decompositions and cognitive-parameter sensitivity thresholds.

## Scope

The CPU stage is a synthetic, single-decision environment with a stipulated benchmark, bounded attack selection and abstract control dependencies. It contains no language-model agents, learning, repeated institutional adaptation, actual organisational independence, realistic political bargaining or real infrastructure ownership. v0.3 introduces language-model representation and review. Longitudinal adaptation, bargaining, measured infrastructure ownership and deployment-specific governance are natural extensions beyond that stage.
