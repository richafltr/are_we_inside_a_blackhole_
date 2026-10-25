# Scientific dry-lab report

Mode: **fixture**.

Fixture mode is authored software validation, not a Gemini response or observational analysis. Live mode records unreviewed model-authored claims; citation validation does not establish their scientific truth.

No probability of a black-hole universe is computed by this laboratory.

- **computed**: The revised toy flat matter+Lambda calculation gives age 0.284005 Gyr at z14.44 and passes its analytic numerical check. This does not reproduce the paper cosmology or compare cosmologies.
  - [naidu-momz14](evidence.json): arXiv:2505.11263v2 (2026-01-28); [primary source](https://arxiv.org/abs/2505.11263v2).
  - [exp-002 result](experiments/exp-002/execution.json) · [code](experiments/exp-002/experiment.py) · [checks](experiments/exp-002/checks.json)
- **computed**: Synthetic control generated 145 of256 labels in one direction with injected selection probability .65. The conditional unbiased-null two-sided p-value is 0.0389518; it concerns the toy process only. The preregistered .01 rejection threshold is not crossed in this seeded realization.
  - [synthetic-selection-control](evidence.json): generator-v1; [primary source](repo:argon_lab/fixture.py).
  - [shamir-jades](evidence.json): arXiv:2502.18781v1 (2025-02-26); MNRAS 538(1),76 (2025); [primary source](https://arxiv.org/abs/2502.18781v1).
  - [exp-003 result](experiments/exp-003/execution.json) · [code](experiments/exp-003/experiment.py) · [checks](experiments/exp-003/checks.json)
- **limitation**: The three supplied paper summaries lack the object-level data, selection functions and quantitative alternative predictions needed for cosmological model comparison. This authored fixture tests the laboratory and supplies no black-hole-universe likelihood.
  - [finner-xlssc122](evidence.json): arXiv:2508.08356v1 (2025-08-11); journal DOI ae1d80; [primary source](https://arxiv.org/abs/2508.08356v1).
  - [naidu-momz14](evidence.json): arXiv:2505.11263v2 (2026-01-28); [primary source](https://arxiv.org/abs/2505.11263v2).
  - [shamir-jades](evidence.json): arXiv:2502.18781v1 (2025-02-26); MNRAS 538(1),76 (2025); [primary source](https://arxiv.org/abs/2502.18781v1).

## Unresolved questions

- Which quantitative black-hole cosmology makes a prediction distinct from a specified standard model?
- Can primary catalogs and uncertainties be imported with valid reuse terms?
- Would calibrated selection controls explain directional imbalance in independent fields?

Paper summaries are not measurement catalogs. Toy flat matter+Lambda ages omit radiation and do not reproduce the paper's adopted cosmology. Synthetic direction counts are not JADES measurements. A numerical tail probability is conditional on a toy null, never a cosmological posterior.
