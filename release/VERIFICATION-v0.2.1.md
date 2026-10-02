# Verification record for v0.2.1

Verification completed before packaging the public repository.

- Python standard-library build; Python 3.10+ supported by the project.
- **22 of 22 tests pass** in the packaged tree.
- The standard 20,000-case v0.2 run regenerates all seven primary compact tables byte-for-byte.
- The robustness and extended checks regenerate the complete set of **11 frozen v0.2 compact result tables byte-for-byte**.
- The v0.2.1 primary, corrected-ablation, paired-uncertainty, mechanism-decomposition and cognitive-sensitivity stages regenerate **11 v0.2.1 compact tables byte-for-byte** with the settings in `RUN_MANIFEST_v0_2_1.json`.
- `robustness_thresholds.csv` reports direction-neutral `sign_change` and `significant_reversal` criteria for valid-claim correction and invalid-claim rejection.
- For E minus C invalid-claim rejection, reviewer error correlation changes sign at `0.30` and reaches significant reversal at `0.75`; good-condition reviewer noise changes sign at `0.20` and reaches significant reversal at `0.40`.
- `SHA256SUMS.txt` covers the public repository files, excluding the checksum file itself and generated scratch directories.

The frozen v0.2 numerical record remains unchanged. v0.2.1 adds corrected interpretation, auditability and optional sensitivity analysis at defaults that preserve the frozen output.
