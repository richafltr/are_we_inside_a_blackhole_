# Cloud task defaults

- Use GPT-6.1 Sol (`gpt-6.1-sol`) with High reasoning (`high`) for Codex Cloud tasks and follow-ups unless the user explicitly requests another setting.
- Set the model and reasoning effort explicitly when dispatching cloud work. In the browser, verify the cloud chat shows GPT-6.1 Sol High; do not rely on a composer that resets to Light.

# Project guidance

- Follow the Gemini 4 Argon SF Hackathon participant guide: https://cerebralvalley.ai/e/gemini-4-argon-sf/details. Target More Dimensions with a 3D generate/render/inspect/critique/repair loop. Do not build Streamlit, a dashboard-led application, basic RAG, or an education chatbot.
- The product uses Gemini 4 Argon (`gemini-4-argon`); the Codex development agent remains GPT-6.1 Sol High. These are separate roles. Verify official API documentation and event-specific access before implementing model calls; never silently substitute another model.
- Use a TypeScript/React/Three.js web stack with server-side credentials. Keep deterministic simulation and scene validation separate from model-generated content. Label replay/fixture mode clearly.
- Preserve event-work provenance and attribution. The repository must remain public for submission; disclose reused assets and prior work. Do not submit a hackathon entry or contact organizers without explicit user authorization.
- Read README.md before implementation. Preserve its distinction between observations, model-dependent inferences, and speculative hypotheses.
- Cite primary sources for scientific values. Store units, uncertainties, source URLs, and paper versions alongside data.
- Label synthetic data and toy models clearly. Never claim these papers establish a black-hole universe or manufacture confidence scores for that claim.
- Keep setup reproducible, choose lightweight dependencies, document real commands, and run checks appropriate to implemented functionality.
- Do not commit credentials, local environment files, downloaded restricted material, or large raw datasets.
