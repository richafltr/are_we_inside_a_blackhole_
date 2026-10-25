# Are We Inside a Black Hole?

A 3D scientific experiment environment where Gemini 4 Argon builds, renders, critiques, and revises cosmology scenes grounded in James Webb Space Telescope observations.

## The idea

Give a researcher or scientific creator a way to turn a cited observation and an explicit set of assumptions into an inspectable 3D experiment. The core interaction is a loop: describe a goal, generate a constrained scene, render it, let Gemini inspect the rendered result alongside numerical checks, then apply and replay a revision.

Start with a synthetic gravitational-lensing experiment inspired by XLSSC 122. Show how changing a lens model changes rendered arcs, preserve the before/after scene and verification results, and keep the source paper attached to the relevant constraints. Later experiments can explore early galaxy formation and reported galaxy-spin asymmetries. A rendered scene is an illustration of the selected model, not a reconstruction of the observed universe or new evidence for that model.

**Scientific stance:** the cited findings motivate investigation; they do not demonstrate that we live inside a black hole or, by themselves, overturn ΛCDM. Tension with a galaxy-formation prediction is not automatically a failure of the underlying cosmological model. Black-hole cosmology remains a hypothesis to explore with explicit assumptions and testable predictions.

## Observations that motivate the project

| Case study | What the paper reports | What we want to explore |
| --- | --- | --- |
| XLSSC 122 | Strong lensing in a cluster at redshift 1.98, with an unusually concentrated dark-matter core. | How inferred mass profiles depend on lensing constraints and assumptions about structure growth. |
| MoM-z14 | A luminous galaxy at spectroscopic redshift 14.44, about 280 million years after the Big Bang under the adopted cosmology, with unusual nitrogen enrichment. | Early star formation, chemical enrichment, and the abundance of bright galaxies versus model expectations. |
| JADES galaxy rotation | A reported imbalance in apparent spiral rotation directions in a deep field. | Sample selection, classification, observer effects, and alternative explanations before cosmological interpretation. |

MoM-z14's abundance pattern should not be reduced to “an old, mature galaxy”: the paper also describes a young stellar population and rapidly rising star formation.

## Hackathon target

Target **More Dimensions** at the [Gemini 4 Argon SF Hackathon](https://cerebralvalley.ai/e/gemini-4-argon-sf/details): generated 3D environments with a render–inspect–critique–repair loop. Use Gemini 4 Argon (`gemini-4-argon`) in the product; Codex is the development agent.

The participant guide requires a public repository and clearly identified work created during the event. It excludes Streamlit applications, basic RAG, and dashboard-led projects. Submission is due **25 October 2026 at 5:00 PM Pacific**, with an accessible demo and a one-minute video. Teams have 1–4 members.

## First working demo

- [ ] Set up a TypeScript web application with a React/Three.js 3D viewport and a small server-side Gemini adapter.
- [ ] Define a validated scene schema: source citations, units, assumptions, synthetic objects, camera, constraints, and reproducible seed.
- [ ] Implement one deterministic lensing toy model and a manipulable 3D scene; document its physical approximations.
- [ ] Connect a real Gemini generation call, capture rendered frames, and send those frames plus numerical checks back for critique and a constrained revision.
- [ ] Show one real failure, one repair, and a replayable before/after comparison in the world itself.
- [ ] Test numerical invariants and scene validation; measure constraint violations before and after repair, loop latency, and rendering performance.
- [ ] Record original contributions, asset provenance, setup commands, and a one-minute demo script.

The first demo should accept a live change to the experimental goal and complete a visible verification loop. A fixture replay can support development, but must be labeled and cannot stand in for the live Gemini integration. Scientific hypotheses require evidence beyond visual plausibility; the system must never manufacture a probability that we live inside a black hole.

## Implementation direction

Use Node.js, TypeScript, Vite/React, Three.js, and browser-based verification. Keep Gemini credentials on the server in environment variables. Verify the event's builder guide for API access and model availability rather than inventing SDK signatures or silently substituting a model. The initial scaffold should work without a key for local deterministic experiments; live generation must clearly report missing credentials.

The [event builder guide](https://docs.google.com/document/d/1kN0n6hPNNTIHMVqf5-hDACrZuIg4KFrWiYpla4WQW8w/edit) specifies the Interactions API and `@google/genai` version 2.3.0 or later. Its Argon examples use `thinking_level`; verify the current TypeScript types before implementing requests. Keep scene generation and revision bounded so a live demonstration can finish promptly.

## Current status

Repository initialized with the research brief, hackathon scope, and sources. Application code, datasets, runtime dependencies, and automated tests have not been added yet. There is no runnable demo or verified build command at this stage.

```sh
git clone https://github.com/richafltr/are_we_inside_a_blackhole_.git
cd are_we_inside_a_blackhole_
```

## Starting sources

1. Finner et al., **JWST Discovery of Strong Lensing from a Galaxy Cluster at Cosmic Noon: Giant Arcs and a Highly Concentrated Core of XLSSC 122**. [Journal / DOI](https://iopscience.iop.org/article/10.3847/2041-8213/ae1d80) · [Author preprint](https://arxiv.org/abs/2508.08356).
2. Naidu et al., **A Cosmic Miracle: A Remarkably Luminous Galaxy at z = 14.44 Confirmed with JWST**, version 2 (28 January 2026). [Abstract](https://arxiv.org/abs/2505.11263v2) · [PDF](https://arxiv.org/pdf/2505.11263v2).
3. Shamir, **The distribution of galaxy rotation in JWST Advanced Deep Extragalactic Survey** (2025). [MNRAS article](https://academic.oup.com/mnras/article/538/1/76/8019798?login=false) · [Author preprint](https://arxiv.org/abs/2502.18781).

These are the starting papers supplied for the project, not an exhaustive review or a claim that each remains the latest result. Numerical work must preserve the source's definitions, uncertainties, and adopted cosmology. Link to research data and imagery with their attribution and reuse terms before redistributing them.
