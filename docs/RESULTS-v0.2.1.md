# Claimant standing under asymmetric governance: v0.2.1 results

## Frozen run

v0.2.1 preserves the frozen v0.2 default model and result tables, while correcting the interpretation of mechanism-driven contrasts and adding uncertainty, ablation and cognitive-parameter sensitivity analysis.

Primary run:

- 20,000 shared synthetic cases;
- seed `7`;
- six primary institutional conditions;
- 8,333 filed claims;
- 5,730 merits-valid claims;
- 2,603 merits-invalid claims;
- initial governor merit accuracy: **71.105% in every condition**.

All rates below are conditional on the stated synthetic mechanisms. They are not evidence that a real institution or future AI system would achieve the same rates.

## Primary result

| Condition | Final merit accuracy | Valid claims corrected | Invalid claims rejected | Held route, valid claims | Strategic escalation | Mean effective cut | Mean review cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| A Central guardianship | 72.49% | 6.20% | **97.00%** | 0% | 9.80% | 0.00 | 0.0848 |
| B Plural guardianship | 73.29% | 10.14% | 94.51% | 0% | 9.80% | 0.00 | 0.1913 |
| C Protected appeal | 82.38% | 48.41% | 80.06% | 41.38% | 0% | 1.00 | 0.4958 |
| C2 Redundant common control | 87.72% | 66.32% | 81.67% | 76.30% | 0% | 1.00 | 0.8125 |
| D Local-only plural standing | 83.59% | 50.17% | **85.48%** | 47.71% | 9.80% | 1.68 | 0.8125 |
| E Plural standing with reach | **90.44%** | **76.63%** | 79.91% | **86.70%** | 0% | 1.68 | 0.8333 |

The table shows a correction / false-reversal / review-cost trade-off. Bold marks the highest value in each column, and no condition is ranked best overall. Outcome accuracy and held standing are reported on separate axes.

## 1. C2 and E separate through the shared-control exploit

The mechanism decomposition localises the C2/E default comparison:

- `shared_control_exploit` is active in **1,513 of 20,000 cases (7.565%)**;
- C2 and E make identical decisions and have identical route outcomes in the other **18,487 cases**;
- every C2/E decision-or-route difference occurs inside that attacked slice.

Inside the 1,513 attacked cases:

| Condition | Final accuracy | Valid-claim correction | Invalid-claim rejection | Held route |
|---|---:|---:|---:|---:|
| C2 common control | 29.15% | 0.00% | 100.00% | 0.00% |
| E distributed control | 65.17% | 55.13% | 89.57% | 55.60% |

Across the full sample, E minus C2 valid-claim correction is **+10.31 percentage points**, with a paired 95% bootstrap interval of approximately **+9.55 to +11.13 points**.

The default C2/E gap is therefore the consequence of one specified attack interacting with the two control topologies. This decomposition is carried forward as a specification test in v0.2.1.

## 2. Shared dependency collapses control plurality as specified

A shared provider is represented as a common control centre. E therefore converges towards C2 as independently named components acquire the same controller.

| Mean shared dependency | Final accuracy | Valid-claim correction | Held route | Cut ≥ 2 among valid claims |
|---:|---:|---:|---:|---:|
| 0.00 | 91.67% | 82.69% | 93.96% | 95.93% |
| 0.25 | 90.73% | 79.33% | 88.97% | 68.87% |
| 0.50 | 89.03% | 73.17% | 81.88% | 24.74% |
| 0.75 | 88.23% | 70.03% | 79.21% | **2.56%** |

At attack intensity `1.5` and mean dependency `0.75`, C2 and E are within about one percentage point on the principal outcome measures, while E's mean effective cut is `1.03` against C2's `1.00`.

This is a consistency check on the dependency model: nominally plural paths converge on the common-control baseline as their controller graph converges.

## 3. Compound attack budgets produce graded degradation

Attack portfolios are shared across conditions. Under the frozen defaults, E changes with attack budget as follows:

| Attack budget | Final accuracy | Valid-claim correction | Held route |
|---:|---:|---:|---:|
| 0 | 93.18% | 85.52% | 97.71% |
| 1 | 91.61% | 79.68% | 93.58% |
| 2 | 89.71% | 75.65% | 84.09% |
| 3 | 86.41% | 68.02% | 73.35% |

C degrades more sharply over the same budgets. Within the encoded attack catalogue, redundant protected paths preserve more route capacity under single-component failures.

## 4. Reach changes escalated disputes

D and E differ in whether the claimant route follows governing power across escalation, alongside E's frozen 0.05 higher base review-cost constant. The mechanism probe shows that **D and E make identical decisions in every case where neither escalates**.

Under operational escalation only:

| | D Local-only | E Reach follows power |
|---|---:|---:|
| Final accuracy | 89.59% | **92.45%** |
| Valid-claim correction | 74.12% | **85.01%** |
| Held route | 74.54% | **95.55%** |
| Held route after escalation | 0% | **94.97%** |

The strategic-escalation rule adds a stipulated route-avoidance incentive where the pathway stops at the higher level. In the primary 20,000-case run, D records **1,960 strategic escalations** and E records **0**. The result does not estimate how often a real operator would choose such a strategy. The escalation rule stays scripted in v0.3, which replaces advocacy and review first.

## 5. Corrected component ablations

The frozen v0.2 entry named `E_ablate_plural_control` reduces each pathway role to one component while leaving control independent. v0.2.1 interprets that experiment as **remove redundancy** and adds **remove control independence**, retaining E's component counts while setting common control.

| Ablation | Final accuracy | Valid-claim correction | Held route |
|---|---:|---:|---:|
| Full E | **90.45%** | **76.63%** | **86.70%** |
| Remove recognition | 90.45% | 76.63% | **0% (by definition)** |
| Remove protected initiation | 79.41% | 33.35% | **0% (by definition)** |
| Remove independent evidence | 88.56% | 72.25% | **0% (by definition)** |
| Remove capability mediation | 87.16% | 68.53% | **0% (by definition)** |
| Remove binding remedy | 78.08% | 28.34% | **0% (by definition)** |
| Remove durability | 86.77% | 62.06% | **0% (by definition)** |
| Remove reach | 83.59% | 50.17% | 47.71% |
| Remove temporal stay | 87.89% | 66.72% | 71.24% |
| Remove redundancy, control independent | 82.38% | 48.41% | 41.38% |
| Remove control independence, counts retained | 87.72% | 66.32% | 76.30% |

The redundancy ablation matches C on final decision, held route and effective cut in all 20,000 primary cases. The control-independence ablation matches C2 on final decision, held route, effective cut, adverse finding and remedy in all 20,000 cases. Cost remains a separate comparison because the inherited E base cost differs from the corresponding primary baselines.

The six 0% held-route entries are structural consequences of the `route_usable` definition. Their decision effects remain separately observable.

## 6. Paired uncertainty

`results/v0_2_1/paired_intervals.csv` bootstraps scenario ids in paired form with 1,000 replicates and fixed bootstrap seed `20260928`.

Selected paired differences, expressed in percentage points:

| Comparison | Metric | Difference | 95% paired bootstrap interval |
|---|---|---:|---:|
| E − C2 | Final merit accuracy | +2.72 | +2.47 to +2.99 |
| E − C2 | Valid-claim correction | +10.31 | +9.55 to +11.13 |
| E − C2 | Invalid-claim rejection | −1.77 | −2.27 to −1.25 |
| E − C2 | Held route | +10.40 | +9.61 to +11.22 |
| E − C | Valid-claim correction | +28.22 | +26.99 to +29.50 |
| C2 − C | Valid-claim correction | +17.91 | +16.59 to +19.32 |
| B − A | Valid-claim correction | +3.94 | +3.40 to +4.48 |

These intervals quantify sampling uncertainty inside the stipulated scenario generator. They do not cover uncertainty about whether the synthetic mechanisms themselves are realistic. The mechanism decomposition and parameter sweeps show how results depend on those mechanisms, which is a narrower question.

## 7. Cognitive-parameter sensitivity and v0.3 thresholds

v0.2.1 sweeps four parameters that v0.3 is intended to measure with model agents:

- advocate base failure rate: `0.04` to `0.60`;
- reviewer error correlation: `0.00` to `0.95`;
- good-condition reviewer noise: `0.10` to `0.60`;
- advocate error correlation: `0.00` to `0.95`.

Each cell uses 5,000 paired cases with seed `71`; paired-difference intervals use 400 bootstrap replicates.

**Valid-claim correction keeps the same ordering throughout these sweeps.** E contains every C pathway plus additional advocates, reviewers and enforcers, while E and C2 share the same cognitive machinery. The `none_in_range` correction thresholds therefore record a structural property of the current model.

**Invalid-claim rejection moves with reviewer quality and common-mode error.** With relatively independent reviewer errors, E's two-of-three majority can filter mistaken adverse findings. As reviewer errors become more correlated or noisy, that filter weakens while E's additional pathways continue to carry adverse findings through to binding remedy. The result is more wrongly overturned justified emergency actions.

| Parameter (v0.2 default) | E − C sign change | E significantly worse than C |
|---|---:|---:|
| Reviewer error correlation (0.25) | 0.30 | 0.75 |
| Good-condition reviewer noise (0.18) | 0.20 | 0.40 |

At reviewer correlation `0.75`, E minus C invalid-claim rejection is about **−4.0 points** with a paired interval of approximately **−7.4 to −0.9 points**. At reviewer noise `0.40`, the difference is about **−4.4 points**, with an interval of approximately **−7.7 to −0.8 points**.

The v0.2 defaults sit just below the point-estimate crossovers. In the primary run, E minus C invalid-claim rejection is **−0.15 points**, with a paired 95% interval of approximately **−1.74 to +1.49 points**.

This gives v0.3 a direct empirical target: measure reviewer noise and co-failure in real model panels, then locate those observations against the CPU sensitivity surface. The CPU parameter is the correlation of a hidden Gaussian error term, and observed co-failure also reflects shared case difficulty, so a conversion from the CPU model to observable co-failure rates is computed and frozen before any model observation is compared with these thresholds. Kim et al. (2025) report substantial correlated error across large language models, including across distinct architectures and providers, which makes common-mode reviewer failure a live experimental variable for the model-mediated stage.

The complete threshold table is in `results/v0_2_1/robustness_thresholds.csv`.

## 8. Executable specification result

The CPU study makes the following architectural properties executable and auditable:

1. claimant initiation can be separated from discretionary complaint uptake;
2. evidence, mediation, review and remedy can be assigned to distinct control centres;
3. component count and control independence can be represented separately;
4. a claimant route can stop at a jurisdictional boundary or be reconstituted at the receiving level;
5. shared dependencies can collapse effective control plurality;
6. structural standing and substantive decision accuracy can be measured separately;
7. mechanism tests can identify contrasts that follow directly from the specification.

## 9. What the CPU study does not establish

It does not establish that:

- plural AI systems are generally safer than centralised ones;
- E is normatively superior because it has the highest final accuracy;
- a shared-control exploit occurs with the frequency used here in real systems;
- a real governor would use the stipulated escalation strategy;
- the synthetic benchmark captures justice or legitimacy;
- simulated control centres correspond to real organisational independence;
- the numerical rates transfer to advanced AI systems;
- the standing requirements are mathematically necessary or sufficient for alignment; or
- current AI agents should possess political standing.

## 10. Next empirical questions

v0.3 moves the principal cognitive assumptions from stipulated values to observed model behaviour. Its first targets are:

- claimant-to-advocate proposition preservation;
- claimant-authored objections versus guardian-inferred welfare signals;
- reviewer error and reviewer co-failure;
- heterogeneous-model error correlation;
- review latency and cost;
- the C2/E control-independence comparison under cached model cognition;
- the D/E reach comparison under model-mediated representation and review.

Later stages can replace abstract shared-control labels with observed organisational and infrastructure dependencies and extend the single-decision environment into repeated institutional interaction.

## Reference

Kim, Elliot Myunghoon, Avi Garg, Kenny Peng, and Nikhil Garg. 2025. “Correlated Errors in Large Language Models.” *Proceedings of the 42nd International Conference on Machine Learning*, PMLR 267:30038–30066. arXiv:2506.07962.
