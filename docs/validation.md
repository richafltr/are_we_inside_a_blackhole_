# Verified development checks

On 25 October 2026, a fresh Linux/Python 3.12 virtual environment installed `requirements.lock` with `pip install --require-hashes -r requirements.lock`. `pip check` reported no broken requirements. The documented demo, replay and fixture comparison commands executed successfully. The final test suite passed 29 tests, including real installed SDK type validation, fake transport continuations, numerical references, failed-check preservation, malformed tool inputs, missing credentials, wall/CPU/memory/output limits, restricted language contracts, artifact tampering and actual recomputation.

The authored demo completed in approximately 0.13 seconds in the fresh environment, excluding setup. It registered 3 experiments, 2 critiques and 1 revision;6 of 7 structural/numerical checks passed. The failed coarse age integration check is intentional and preserved. Replay recomputed all 3 experiments and reproduced the failed and passed checks. Timing varies by machine and is not a model-performance result.

The synthetic directional control generated 145 of 256 labels at seed 1729 with chosen Bernoulli probability 0.65. Its two-sided unbiased-null p-value is approximately 0.03895, above the preregistered 0.01 threshold. The result must not be reported as crossing that threshold, and no seed was changed to manufacture a desired rejection.

The no-key live command exited 2 with saved `blocked_credentials` state and no attempted model call. No live Gemini call, live comparison, event-model entitlement, Google API network access, three-minute live completion or million-token investigation was tested. CI configuration was added but remote CI success must be inspected on the proposed branch/PR; it is not claimed by these local checks.
