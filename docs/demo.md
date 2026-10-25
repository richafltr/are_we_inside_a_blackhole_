# One-minute demonstration

Run setup before recording. Use a fresh output directory each time; the runner refuses to overwrite artifacts.

```sh
python -m argon_lab demo --out work/demo
python -m argon_lab replay --run work/demo
python -m argon_lab compare-fixture --out work/comparison
```

Suggested 60-second walkthrough:

- 0–10s: say “This is a scientific laboratory. Gemini Argon is the investigator; this credential-free recording demonstrates an authored validation fixture.” Show the registry's source versions, missing uncertainties and missing raw data.
- 10–25s: run the demo. Open `experiments/exp-001/proposal.json` and `checks.json`: predictions preceded computation and the coarse integral failed an independent analytic check.
- 25–40s: show the critique in `state.json`, the linked refined experiment and passing numerical result. Show the synthetic label generator, seed and selection assumption.
- 40–50s: run replay; it recomputes three analyses and preserves the first failed check. Open the report's evidence and experiment links.
- 50–60s: show comparison metrics. Say “These numbers measure authored process coverage, not Gemini quality or cosmology truth. Live Argon requires event-authorized credentials. The evidence may remain inconclusive.”

## Live demonstration (target under three minutes)

Set `GEMINI_API_KEY` securely through the terminal/environment secret mechanism. Do not put it in command history, repository files or a recording. The key must have event access to `gemini-4-argon`, and networking must permit `generativelanguage.googleapis.com`.

```sh
python -m argon_lab live --out work/live --thinking-level high
```

The investigator receives the research question, registry and tools; it chooses its own analyses and conclusion. Each call resends Interactions configuration; a 150s arm budget bounds the investigation. If it stops before a valid report, show the explicit incomplete/error status. Do not present that run as successful science. In the development environment, credentials were absent and the Google API host was outside the configured package-manager network policy. Only the explicit no-key failure and SDK/mock contracts were verified.

A live process comparison is a separate longer activity:

```sh
python -m argon_lab compare-live --out work/live-comparison --thinking-level high
```

No live comparison, live model availability, one-million-token capacity test, event submission or video upload is claimed by this repository.
