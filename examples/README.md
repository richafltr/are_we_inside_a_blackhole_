# Saved authored validation run

`fixture-run/` is an executed software fixture, not a Gemini transcript or observational analysis. Its environment records the implementation commit used to create it. The source, inputs, seeds, failed coarse numerical check, revised result, synthetic control, critiques, report and artifact manifest are inspectable.

```sh
python -m argon_lab replay --run examples/fixture-run
```

The command recomputes all three analyses. Expected checks are failed/passed/passed; preserving the first failed check is correct. `fixture-replay.json` contains the saved recomputation summary. The manifest is a consistency check, not an authenticity signature. To create a fresh run, use `python -m argon_lab demo --out work/new-demo`.

The report's synthetic p-value does not cross its preregistered 0.01 threshold. It does not measure JADES data or the probability of a cosmology.
