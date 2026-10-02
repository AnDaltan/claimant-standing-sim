# Repository provenance

This repository is the compact public research surface for the CPU claimant-standing simulation.

## Frozen v0.2 record

The compact CSV files directly under `results/` remain the frozen v0.2 result set. `RUN_MANIFEST.json` remains the frozen v0.2 run manifest. The default command path continues to regenerate those files byte-for-byte.

The v0.2.1 source revision exposes existing literals through `ExperimentConfig`, adds disabled-by-default sensitivity machinery, and adds new analysis paths. Defaults remain unchanged, and the full v0.2 reproduction verifies all 11 compact frozen result tables exactly.

The original v0.2 interpretation document is retained in the private frozen archive. `docs/RESULTS-v0.2.md` is a public provenance pointer to that record and to the current v0.2.1 interpretation.

## v0.2.1 additions

The following files or areas are new or revised in v0.2.1:

- `src/awas_sim/model.py`: existing literals lifted into configuration; optional advocate-error correlation added at default zero;
- `src/awas_sim/institutions.py`: corrected ablation catalogue and structural-route audit helper added; frozen catalogue retained;
- `src/awas_sim/experiment.py` and `cli.py`: selectable v0.2/v0.2.1 ablation sets;
- `src/awas_sim/uncertainty.py`: paired bootstrap analysis;
- `src/awas_sim/flip.py`: cognitive-parameter sensitivity sweep and cost-side thresholds;
- `tests/test_v021_specification.py`: ablation, specification and uncertainty tests;
- `scripts/mechanism_probe.py`: explicit mechanism decomposition;
- `results/v0_2_1/`: corrected ablations and new analysis outputs;
- `README.md`, `CHANGELOG.md`, `docs/EXPERIMENT.md`, `docs/METHODOLOGY-AUDIT.md`, `docs/RESULTS-v0.2.1.md` and release guidance: current framing and public navigation;
- `RUN_MANIFEST_v0_2_1.json`: full v0.2.1 default and analysis settings.

## Full frozen archive

The original full v0.2 archive contains the large per-episode ledgers and the original documentation. It is retained privately with a fixed checksum for provenance and is available on request. See `release/FULL-ARTIFACT.md`.
