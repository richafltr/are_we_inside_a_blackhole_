# Saved authored validation run

`fixture-run/` is an executed software fixture, not a Gemini transcript or observational analysis. Its environment records the implementation commit used to create it. The source, inputs, seeds, failed coarse numerical check, revised result, synthetic control, critiques, report and artifact manifest are inspectable.

```sh
python -m argon_lab replay --run examples/fixture-run
```

The command recomputes all three analyses. Expected checks are failed/passed/passed; preserving the first failed check is correct. `fixture-replay.json` contains the saved recomputation summary. The manifest is a consistency check, not an authenticity signature. To create a fresh run, use `python -m argon_lab demo --out work/new-demo`.

The report's synthetic p-value does not cross its preregistered 0.01 threshold. It does not measure JADES data or the probability of a cosmology.

`fixture-comparison.json` records an actual executed comparison between the authored single-pass fixture and iterative fixture. It preserves each arm's budgets, elapsed time, registry-linked claim counts, checks, critiques/revisions and deterministic replay results. These are software process metrics, not Gemini output or model-performance measurements. The underlying arms were generated under ignored `work/recorded-comparison/`; only this compact comparison summary is archived. Recreate both complete arm directories with `python -m argon_lab compare-fixture --out work/new-comparison`. The separately archived `fixture-run/` demonstrates the same deterministic iterative scenario.
