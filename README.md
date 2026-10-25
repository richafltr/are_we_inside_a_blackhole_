# Are We Inside a Black Hole?

A reproducible computational dry lab in which Gemini 4 Argon investigates whether available cosmological evidence can distinguish a black-hole-universe hypothesis from standard explanations.

## What we are building

**The product is the laboratory. Gemini Argon is the scientist operating inside it.** Give the agent a research question, cited evidence, computational tools, and an experiment workspace. It should formulate competing hypotheses, derive testable predictions, write and run analyses, inspect failures, revise its reasoning, and produce a reproducible scientific argument. “The evidence cannot distinguish these hypotheses” is a valid result.

This is an agent research environment, with a headless runner and inspectable experiment artifacts as the first interface. Visualizations and simulations are instruments the investigator can create when needed.

## Scientific starting point

- **XLSSC 122:** strong lensing and an unusually concentrated dark-matter core at redshift 1.98 motivate investigation of early structure growth.
- **MoM-z14:** a luminous galaxy at spectroscopic redshift 14.44, about 280 million years after the Big Bang under the paper's cosmology, motivates investigation of early star formation and enrichment. Unusual nitrogen enrichment does not by itself make it an old, mature galaxy.
- **JADES galaxy rotation:** a reported directional imbalance motivates investigation of selection, classification, observer effects, and possible cosmological interpretations.

These findings do not establish that we live inside a black hole. Tension with a galaxy-formation prediction is not automatically a failure of ΛCDM. Alternative cosmologies must supply quantitative, distinguishable predictions before the lab can compare them. A suggestive analogy or a universe-size/Schwarzschild-radius coincidence is not a model-selection result.

## The investigation loop

1. Inspect evidence, source versions, uncertainties, units, selection effects, and missing data.
2. State competing hypotheses, assumptions, predictions, and a falsification criterion before running an experiment.
3. Write an executable analysis; run it inside the isolated workspace with a bounded compute budget.
4. Inspect numerical checks, errors, artifacts, and whether the result actually discriminates between hypotheses.
5. Challenge the result with controls, sensitivity checks, or an alternative explanation; revise and rerun.
6. Export an evidence-linked report, experiment code, inputs, seeds, logs, and unresolved questions.

The lab must distinguish measured data, paper-derived estimates, synthetic controls, and theoretical assumptions. If only a paper summary is available, the agent must identify the missing data instead of fabricating observations or likelihoods. It must not produce a made-up probability that we live inside a black hole.

## Hackathon scope

Target **Million Token Engineering** at the [Gemini 4 Argon SF Hackathon](https://cerebralvalley.ai/e/gemini-4-argon-sf/details): an agent maintains and verifies a scientific investigation across evidence, code, experiments, and revisions. The public repo must identify work created during the event. The guide excludes Streamlit applications, basic RAG, and dashboard-led projects. Submission is due **25 October 2026 at 5:00 PM Pacific**; prepare a live demonstration and one-minute video.

- [x] Build a Python scientific workspace and a headless Gemini research runner with explicit experiment tools.
- [x] Add an evidence manifest with primary-source links, paper versions, units, uncertainty fields, and data availability/rights status.
- [x] Implement tools to inspect evidence, create experiments, execute bounded analyses, inspect artifacts, and record revisions.
- [x] Provide one reproducible initial investigation and synthetic control to validate the lab; do not pre-script the agent's scientific conclusion.
- [x] Implement real Gemini Argon Interactions calls and persistent traces; SDK/mock contracts verified, live access untested.
- [x] Instrument a single-pass response baseline with a tool-assisted investigation under recorded budgets; measure reproducibility, citation traceability, checks passed, and time. These metrics assess research process, not the truth of an unverified cosmology.
- [x] Test tool contracts, numerical checks, execution limits, provenance, and end-to-end artifact replay.
- [x] Document actual setup commands, contribution provenance, limitations, and the short live demo.

Use Gemini 4 Argon (`gemini-4-argon`) as the investigator; Codex GPT-6.1 Sol High is the development agent. The [event builder guide](https://docs.google.com/document/d/1kN0n6hPNNTIHMVqf5-hDACrZuIg4KFrWiYpla4WQW8w/edit) specifies the Interactions API and `google-genai` or `@google/genai` version 2.3.0 or later. Verify current official SDK types and event access before implementation. Keep credentials in environment variables. Missing credentials must be explicit; fixture replay must never masquerade as a live investigation.

## Current status

A runnable Python headless lab, evidence registry, bounded numerical tools, Gemini Interactions adapter and deterministic artifact replay are implemented. The authored fixture exercises a failed numerical check, critique, revision and synthetic selection control. It is **not a Gemini transcript or a cosmological result**. No live Gemini investigation or model-performance result is claimed; credentials were not supplied.

See [laboratory contracts and limitations](docs/architecture.md), [one-minute demonstration](docs/demo.md) and [contribution provenance](CONTRIBUTIONS.md), and [verified checks](docs/validation.md).

```sh
git clone --branch codex/argon-dry-lab https://github.com/richafltr/are_we_inside_a_blackhole_.git
cd are_we_inside_a_blackhole_
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock
python -m pytest -q
python -m argon_lab demo --out work/demo
python -m argon_lab replay --run work/demo
python -m argon_lab compare-fixture --out work/comparison
```

Verified on Linux/Python 3.12. Offline demo/replay use only the standard library; install the hash-pinned lock for the supported SDK/test environment. Outputs are saved under `work/` and are ignored by Git. Use a fresh output directory on each run.

For a live investigation, securely set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) with access to the event model and permit outbound `generativelanguage.googleapis.com`, then run:

```sh
python -m argon_lab live --out work/live --thinking-level high
python -m argon_lab compare-live --out work/live-comparison --thinking-level high
```

The first live command has a 150s budget; the two-arm comparison can take five minutes. Without a key, the CLI exits 2, saves `blocked_credentials`, and explicitly says no live call was attempted. The development cloud had neither a key nor Google API network access. API behavior, event access and live demo completion remain unverified. The adapter uses only `gemini-4-argon` and never substitutes another model.

A run preserves code, JSON inputs, seeds, resource limits, logs/results, independent checks, evidence/source links, critique/revision state, raw interaction contracts (live only), a report and artifact hashes. Replay recomputes analyses rather than just reading saved results. Process metrics assess reproducibility and traceability; fixture comparisons measure authored software coverage, not Gemini quality. An intentionally failed coarse integration check remains visible in the trace.

## Starting sources

1. Finner et al., **JWST Discovery of Strong Lensing from a Galaxy Cluster at Cosmic Noon: Giant Arcs and a Highly Concentrated Core of XLSSC 122**. [Journal / DOI](https://iopscience.iop.org/article/10.3847/2041-8213/ae1d80) · [Author preprint](https://arxiv.org/abs/2508.08356).
2. Naidu et al., **A Cosmic Miracle: A Remarkably Luminous Galaxy at z = 14.44 Confirmed with JWST**, version 2 (28 January 2026). [Abstract](https://arxiv.org/abs/2505.11263v2) · [PDF](https://arxiv.org/pdf/2505.11263v2).
3. Shamir, **The distribution of galaxy rotation in JWST Advanced Deep Extragalactic Survey** (2025). [MNRAS article](https://academic.oup.com/mnras/article/538/1/76/8019798?login=false) · [Author preprint](https://arxiv.org/abs/2502.18781).

These are the starting papers supplied for the project, not an exhaustive review or a claim that each remains the latest result. Numerical work must preserve the source's definitions, uncertainties, and adopted cosmology. Link to research data and imagery with their attribution and reuse terms before redistributing them.
