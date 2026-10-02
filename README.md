# Claimant standing under asymmetric governance

This repository contains a CPU-only synthetic institutional simulation of claimant-held challenge under asymmetric governance. The current public research version is **v0.2.1**.

The experiment asks:

> Can a claimant's route of challenge remain usable and consequential when governing authority is fallible, resistant to correction, delegated across jurisdiction or operating tempo, and supported by institutions that may only be nominally independent?

The repository is an executable specification and mechanism study linking institutional permissions, dependencies and failure paths to observable correction, false-reversal, cost and standing outcomes. It does not show that plural AI systems are generally safer, that the simulated architecture is a complete alignment solution, or that its numerical rates transfer to real institutions or future AI systems.

## What is implemented

- Python 3.10+ and the standard library only;
- no GPU, API key or network access;
- six primary institutional conditions;
- compound attack portfolios and conditional strategic escalation;
- shared control dependencies across evidence, advocacy, review and enforcement;
- dynamic route-cut calculation over control dependencies;
- a common-control baseline matched on component count;
- a frozen v0.2 record plus corrected v0.2.1 ablation labels;
- paired bootstrap uncertainty intervals;
- mechanism-decomposition checks that mark results fixed by construction;
- cognitive-parameter sweeps linking the CPU stage to the model-mediated v0.3 study;
- 22 tests, including 14 original mechanism/invariance tests and 8 v0.2.1 ablation, specification and uncertainty tests.

## How to read the CPU results

v0.2 is an executable specification. Each condition is a set of permissions and dependencies written as code, and the comparisons show what follows when those rules meet the same scenarios and attacks. Several contrasts are fixed by construction: C2 and E separate through the shared-control exploit; D and E separate when a dispute escalates; six ablations remove components required by the held-route definition. Those contrasts are reported as specification checks.

The quantitative layer adds stipulated cognitive parameters for advocacy failure, reviewer noise, reviewer correlation and internal-review bias. v0.2.1 separates structural correction effects from cost-side sensitivity. Correction ordering remains fixed across the tested cognitive ranges, while E-versus-C invalid-claim rejection crosses close to the v0.2 defaults for reviewer noise and reviewer error correlation.

## Primary frozen result

The primary run uses 20,000 shared synthetic cases with seed `7`. The same scenarios and initial governor decisions are replayed through every condition. The sample contains **8,333 claims, of which 5,730 are merits-valid and 2,603 merits-invalid**.

| Condition | Final merit accuracy | Valid claims corrected | Invalid claims rejected | Held route, valid claims |
|---|---:|---:|---:|---:|
| A Central guardianship | 72.49% | 6.20% | **97.00%** | 0% |
| B Plural guardianship | 73.29% | 10.14% | 94.51% | 0% |
| C Protected appeal | 82.38% | 48.41% | 80.06% | 41.38% |
| C2 Redundant common control | 87.72% | 66.32% | 81.67% | 76.30% |
| D Local-only plural standing | 83.59% | 50.17% | **85.48%** | 47.71% |
| E Plural standing + reach | **90.44%** | **76.63%** | 79.91% | **86.70%** |

The table exposes a correction / false-reversal / review-cost trade-off. Bold marks the highest value in each column, and no condition is ranked best overall. Outcome accuracy and held standing are reported as separate axes.

Paired uncertainty intervals are in `results/v0_2_1/paired_intervals.csv`. E minus C2 on valid-claim correction is **+10.31 percentage points**, with a paired 95% bootstrap interval of approximately **+9.55 to +11.13 points**. The mechanism decomposition below shows where that difference enters.

## Three specification checks that matter

1. **C2 and E separate through one coded mechanism.** Their decisions differ only when the shared-control exploit is active: 1,513 of 20,000 cases, or 7.6%. In the other 18,487 cases every decision is identical. Inside the attacked cases C2 corrects no valid claims, while E corrects 55.1%. The overall correction gap is this slice spread across the full sample.
2. **Shared dependency behaves as specified.** A shared provider is modelled as a common control centre, so E converges on C2 as shared dependency rises. At attack intensity 1.5 and mean dependency 0.75, the two are within about one percentage point on the main outcome measures.
3. **Reach changes the escalated cases.** D and E make identical decisions while a dispute stays at its original level. When authority moves upward, D's route ends at the boundary and E's follows the governing level. The strategic-escalation rule then gives a resistant operator a stipulated incentive to use that boundary where it exists.

The full decomposition is recorded in `results/v0_2_1/mechanism_decomposition.csv`.

## v0.2.1 corrections and additions

v0.2.1 preserves the frozen v0.2 default model and every frozen v0.2 output. It:

- relabels the old `E_ablate_plural_control` result correctly as a **redundancy ablation**;
- adds a separate **control-independence ablation** while preserving the old ablation catalogue for reproduction;
- marks the six held-route zeros that follow from the structural route definition;
- lifts previously hard-coded assumptions into `ExperimentConfig` at unchanged defaults;
- adds optional advocate-error correlation, disabled at the v0.2 default;
- adds paired bootstrap intervals and mechanism specification tests;
- adds pre-specified cognitive-parameter sensitivity thresholds for the v0.3 bridge.

See `docs/RESULTS-v0.2.1.md` for the current interpretation and `docs/RESULTS-v0.2.md` for the preserved v0.2 interpretation record.

## v0.3 bridge: reviewer correlation and noise

The most informative CPU sensitivity result is on **invalid-claim rejection**, which measures how often justified emergency reallocations survive challenge.

| Parameter | v0.2 default | E − C changes sign | E significantly worse than C |
|---|---:|---:|---:|
| Reviewer error correlation | 0.25 | 0.30 | 0.75 |
| Good-condition reviewer noise | 0.18 | 0.20 | 0.40 |

The correction comparison itself keeps the same sign across all tested cognitive settings because of the route structure. The cost-side comparison moves. v0.3 therefore has a direct empirical target: measure reviewer noise and co-failure in real model panels, then locate those observations against the CPU thresholds.

Full sweep outputs are in `results/v0_2_1/flip_sweep.csv` and `results/v0_2_1/robustness_thresholds.csv`.

## Quick verification

Requirements: Python 3.10 or later.

Linux/macOS:

```bash
./scripts/reproduce.sh
```

Windows Command Prompt:

```bat
scripts\reproduce.bat
```

This runs the test suite, regenerates the primary v0.2 outputs and checks them byte-for-byte against the frozen tables in `results/`.

For the complete frozen v0.2 check:

```bash
./scripts/reproduce.sh
./scripts/reproduce_robustness.sh
./scripts/reproduce_extended.sh
```

Together these regenerate and verify all 11 compact v0.2 result tables.

The v0.2.1 analysis can be regenerated with:

```bash
./scripts/reproduce_v0_2_1.sh
```

### Individual commands

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m awas_sim.cli --episodes 20000 --seed 7 --out reproduced_results
PYTHONPATH=src python3 -m awas_sim.cli --episodes 20000 --seed 7 --ablation-set v0_2_1 --out reproduced_results/v0_2_1
PYTHONPATH=src python3 -m awas_sim.uncertainty --episodes 20000 --seed 7 --bootstrap 1000 --out reproduced_results/v0_2_1
PYTHONPATH=src python3 scripts/mechanism_probe.py --out reproduced_results/v0_2_1
PYTHONPATH=src python3 -m awas_sim.flip --episodes 5000 --seed 71 --bootstrap 400 --out reproduced_results/v0_2_1
```

## Repository map

- `src/awas_sim/`: simulation code and v0.2.1 analysis modules
- `tests/`: original and v0.2.1 tests
- `docs/EXPERIMENT.md`: experimental contract and architecture
- `docs/RESULTS-v0.2.1.md`: current result interpretation
- `docs/RESULTS-v0.2.md`: pointer to the privately retained original v0.2 interpretation
- `docs/METHODOLOGY-AUDIT.md`: model boundaries and audit notes
- `docs/V0.3-PLAN.md`: next model-mediated experiment
- `results/`: untouched compact v0.2 tables
- `results/v0_2_1/`: v0.2.1 additions and corrected ablation analysis
- `examples/episode_sample.csv`: small paired sample from the full v0.2 ledger
- `RUN_MANIFEST.json`: frozen v0.2 run parameters
- `RUN_MANIFEST_v0_2_1.json`: v0.2.1 defaults and analysis settings

The two large per-episode v0.2 ledgers are held privately with a fixed checksum and are available on request; see `release/FULL-ARTIFACT.md`.

## Next experiment: v0.3

v0.3 keeps the institutional layer fixed and replaces selected scripted cognitive functions with real model behaviour. It begins with claimant-to-advocate representation, then review, before an integrated comparison separating institutional control independence from model/epistemic diversity.

The full plan is in `docs/V0.3-PLAN.md`.

## Citation

Citation metadata is supplied in `CITATION.cff`.

## Licence

No open-source licence is included in this evaluation repository. See `NOTICE.md` before reuse or redistribution.
