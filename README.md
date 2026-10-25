# Are We Inside a Black Hole?

A hackathon scientific sandbox for exploring what James Webb Space Telescope observations tell us about early cosmic structure—and what it would take to test a black-hole-universe hypothesis.

## The idea

Build an interactive environment where people can inspect published observations, change model assumptions, and compare predictions with evidence. Start with unusually early galaxies, concentrated galaxy clusters, and reported galaxy-spin asymmetries. Keep the question open: what can ordinary galaxy-formation physics explain, and what observations could distinguish more speculative cosmologies?

**Scientific stance:** the cited findings motivate investigation; they do not demonstrate that we live inside a black hole or, by themselves, overturn ΛCDM. Tension with a galaxy-formation prediction is not automatically a failure of the underlying cosmological model. Black-hole cosmology remains a hypothesis to explore with explicit assumptions and testable predictions.

## Observations that motivate the project

| Case study | What the paper reports | What we want to explore |
| --- | --- | --- |
| XLSSC 122 | Strong lensing in a cluster at redshift 1.98, with an unusually concentrated dark-matter core. | How inferred mass profiles depend on lensing constraints and assumptions about structure growth. |
| MoM-z14 | A luminous galaxy at spectroscopic redshift 14.44, about 280 million years after the Big Bang under the adopted cosmology, with unusual nitrogen enrichment. | Early star formation, chemical enrichment, and the abundance of bright galaxies versus model expectations. |
| JADES galaxy rotation | A reported imbalance in apparent spiral rotation directions in a deep field. | Sample selection, classification, observer effects, and alternative explanations before cosmological interpretation. |

MoM-z14's abundance pattern should not be reduced to “an old, mature galaxy”: the paper also describes a young stellar population and rapidly rising star formation.

## Hackathon scope

- [ ] Build a reproducible scientific workspace with documented setup and checks.
- [ ] Add a small, cited observation catalog with units, uncertainties, paper versions, and provenance.
- [ ] Implement a baseline redshift–cosmic-age calculator with visible cosmological parameters.
- [ ] Create an interactive evidence explorer and a transparent toy-model playground.
- [ ] Compare baseline assumptions with clearly labeled alternatives; distinguish measured data, inferred quantities, and simulated examples.
- [ ] Document limitations and identify observations that could falsify each proposed explanation.

The first demo should let someone select an observation, inspect its source, vary an assumption, and understand how the comparison changes. It should never produce a fabricated probability that we live inside a black hole.

## Current status

Repository initialized with the research brief and sources. Application code, datasets, runtime dependencies, and automated tests have not been added yet. There is no runnable demo or verified build command at this stage.

```sh
git clone https://github.com/richafltr/are_we_inside_a_blackhole_.git
cd are_we_inside_a_blackhole_
```

## Starting sources

1. Finner et al., **JWST Discovery of Strong Lensing from a Galaxy Cluster at Cosmic Noon: Giant Arcs and a Highly Concentrated Core of XLSSC 122**. [Journal / DOI](https://iopscience.iop.org/article/10.3847/2041-8213/ae1d80) · [Author preprint](https://arxiv.org/abs/2508.08356).
2. Naidu et al., **A Cosmic Miracle: A Remarkably Luminous Galaxy at z = 14.44 Confirmed with JWST**, version 2 (28 January 2026). [Abstract](https://arxiv.org/abs/2505.11263v2) · [PDF](https://arxiv.org/pdf/2505.11263v2).
3. Shamir, **The distribution of galaxy rotation in JWST Advanced Deep Extragalactic Survey** (2025). [MNRAS article](https://academic.oup.com/mnras/article/538/1/76/8019798?login=false) · [Author preprint](https://arxiv.org/abs/2502.18781).

These are the starting papers supplied for the project, not an exhaustive review or a claim that each remains the latest result. Numerical work must preserve the source's definitions, uncertainties, and adopted cosmology. Link to research data and imagery with their attribution and reuse terms before redistributing them.
