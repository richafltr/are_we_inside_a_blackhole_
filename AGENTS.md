# Cloud task defaults

- Use GPT-6.1 Sol (`gpt-6.1-sol`) with High reasoning (`high`) for Codex Cloud tasks and follow-ups unless the user explicitly requests another setting.
- Set the model and reasoning effort explicitly when dispatching cloud work. In the browser, verify the cloud chat shows GPT-6.1 Sol High; do not rely on a composer that resets to Light.

# Project guidance

- Read README.md before implementation. Preserve its distinction between observations, model-dependent inferences, and speculative hypotheses.
- Cite primary sources for scientific values. Store units, uncertainties, source URLs, and paper versions alongside data.
- Label synthetic data and toy models clearly. Never claim these papers establish a black-hole universe or manufacture confidence scores for that claim.
- Keep setup reproducible, choose lightweight dependencies, document real commands, and run checks appropriate to implemented functionality.
- Do not commit credentials, local environment files, downloaded restricted material, or large raw datasets.
