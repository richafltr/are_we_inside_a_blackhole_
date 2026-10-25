"""Authored deterministic contract scenario. These are NOT recorded model turns."""
from .lab import Lab, replay, write_json

QUESTION = "Can a checked age calculation and a synthetic selection control supply discriminating cosmological evidence?"

AGE_CODE = '''n = inputs["steps"]
a = 1 / (1 + inputs["z"])
h = a / n
integral = sum(((j + 0.5)*h)**0.5 / math.sqrt(inputs["omega_m"] + (1-inputs["omega_m"])*((j+0.5)*h)**3) for j in range(n)) * h
hubble_gyr = 3.0856775814913673e19 / inputs["h0"] / 31557600 / 1e9
result = {"age_gyr": integral * hubble_gyr, "steps": n}
'''
CONTROL_CODE = '''n = inputs["n"]
k = sum(rng.random() < inputs["selection_probability"] for j in range(n))
pvalue = min(1.0, 2 * sum(math.comb(n, j) * 0.5**n for j in range(min(k, n-k)+1)))
result = {"n": n, "k": k, "p_value": pvalue, "generating_probability": inputs["selection_probability"]}
'''
AGE_HYPOTHESES = [
    {"id": "converged-baseline", "prediction": "For H0=67.4 km/s/Mpc, Omega_m=.315, z=14.44, numerical age agrees with the exact flat matter+Lambda expression within relative1e-5.", "falsification": "Relative error greater than1e-5 falsifies numerical adequacy at the proposed resolution.", "assumptions": "Flat matter+Lambda FLRW toy; no radiation, cosmological parameters chosen for demonstration, not a fit."},
    {"id": "discretization-error", "prediction": "A very coarse midpoint rule disagrees with the analytic reference; increasing resolution decreases numerical error.", "falsification": "If refinement does not reduce disagreement, discretization alone is insufficient.", "assumptions": "Same integrand and parameters; only quadrature resolution varies. Neither hypothesis is a black-hole cosmology."},
]
CONTROL_HYPOTHESES = [
    {"id": "unbiased-labels", "prediction": "Independent equally likely labels have Binomial(n,.5) counts; a two-sided p<.01 rejects this toy null at the specified rule.", "falsification": "Reject toy unbiased null if exact two-sided p<.01, with no cosmological inference.", "assumptions": "Independent labels, fixed n=256 and threshold .01 specified before sampling."},
    {"id": "selection-confounder", "prediction": "Injected probability .65 produces a direction excess without any cosmological mechanism.", "falsification": "A count inconsistent with the generating probability warrants checking generator and sampling; one sample cannot identify the cause of real survey asymmetry.", "assumptions": "Synthetic Bernoulli labels; bias deliberately injected. Not fitted to JADES data."},
]


def call(lab, name, **request):
    result = lab.dispatch(name, request)
    if "error" in result:
        raise ValueError(result["error"])
    return result


def demo(root):
    lab = Lab(root, mode="fixture")
    call(lab, "inspect_evidence")
    proposal = dict(question=QUESTION,
                    hypotheses=AGE_HYPOTHESES, evidence_ids=["naidu-momz14"], code=AGE_CODE,
                    inputs={"h0":67.4,"omega_m":.315,"z":14.44,"steps":8}, seed=42, verifier="flat_age")
    first = call(lab, "propose_experiment", **proposal)
    call(lab, "run_experiment", experiment_id=first["id"])
    call(lab, "inspect_artifact", experiment_id=first["id"], artifact="checks.json")
    critique = call(lab, "record_critique", experiment_id=first["id"],
                    finding="The independent analytic check fails at 8 midpoint bins. An integration error is not a cosmological anomaly.",
                    next_test="Increase to8192 bins, retain parameters, compare against independent analytic reference.")
    proposal["inputs"] = {**proposal["inputs"], "steps":8192}
    revised = call(lab, "revise_experiment", parent_id=first["id"], critique_id=critique["id"], **proposal)
    age = call(lab, "run_experiment", experiment_id=revised["id"])
    control = call(lab, "propose_experiment", question="Can selection alone produce apparent directional excess in a synthetic control?", hypotheses=CONTROL_HYPOTHESES,
                   evidence_ids=["shamir-jades","synthetic-selection-control"], code=CONTROL_CODE,
                   inputs={"n":256,"selection_probability":.65,"seed":1729}, seed=1729, verifier="binomial_control")
    selection = call(lab, "run_experiment", experiment_id=control["id"])
    call(lab, "record_critique", experiment_id=control["id"], finding="A small toy-null p-value cannot distinguish classifier/selection effects from cosmological causes. No JADES object catalog is available.",
         next_test="Obtain independent fields, calibrated classifications, selection function and explicit alternative model predictions before observational model selection.")
    call(lab, "submit_report", claims=[
        {"kind":"computed", "text": f"The revised toy flat matter+Lambda calculation gives age {age['execution']['result']['age_gyr']:.6f} Gyr at z14.44 and passes its analytic numerical check. This does not reproduce the paper cosmology or compare cosmologies.", "evidence_ids":["naidu-momz14"],"experiment_ids":[revised["id"]]},
        {"kind":"computed", "text": f"Synthetic control generated {selection['execution']['result']['k']} of256 labels in one direction with injected selection probability .65. The conditional unbiased-null two-sided p-value is {selection['execution']['result']['p_value']:.6g}; it concerns the toy process only. The preregistered .01 rejection threshold is not crossed in this seeded realization.","evidence_ids":["synthetic-selection-control","shamir-jades"],"experiment_ids":[control["id"]]},
        {"kind":"limitation", "text":"The three supplied paper summaries lack the object-level data, selection functions and quantitative alternative predictions needed for cosmological model comparison. This authored fixture tests the laboratory and supplies no black-hole-universe likelihood.","evidence_ids":["finner-xlssc122","naidu-momz14","shamir-jades"],"experiment_ids":[]},
    ], unresolved_questions=["Which quantitative black-hole cosmology makes a prediction distinct from a specified standard model?", "Can primary catalogs and uncertainties be imported with valid reuse terms?", "Would calibrated selection controls explain directional imbalance in independent fields?"])
    metrics = lab.finalize()
    return {"metrics":metrics,"replay":replay(root)}


def compare_fixture(root):
    from pathlib import Path
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    baseline = Lab(root / "single-pass", mode="fixture", budget={"max_experiments":0,"max_tool_calls":0,"wall_seconds":150})
    baseline.submit_report(claims=[{"kind":"limitation","text":"Authored single-pass fixture: source summaries alone do not supply quantitative alternative predictions or raw data for cosmological model selection.","evidence_ids":["finner-xlssc122","naidu-momz14","shamir-jades"],"experiment_ids":[]}],unresolved_questions=["What quantitative predictions and calibrated primary data distinguish the hypotheses?"])
    baseline.state["question"] = QUESTION
    b = baseline.finalize()
    iterative = demo(root / "iterative")
    result = {"label":"AUTHORED SOFTWARE FIXTURE; NOT GEMINI PERFORMANCE", "same_question_and_evidence":True,
              "budget_policy":"Task budgets differ intentionally: single response/no tools versus iterative4 experiments/24 tools/150s. No claim of equal compute or model superiority.",
              "single_pass":b,"iterative":iterative["metrics"], "replay":iterative["replay"],
              "reproducibility":{"single_pass":replay(root / "single-pass"),"iterative":iterative["replay"]},
              "interpretation":"Counts demonstrate instrumented process coverage only; no model output, model-quality measurement or cosmology truth score."}
    write_json(root / "comparison.json", result)
    return result
