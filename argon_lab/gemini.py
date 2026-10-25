"""Real Interactions API adapter. SDK types checked against google-genai2.33.0.

No fallback model, no canned live conclusions. Credential-free tests inject an
explicit fake transport; the CLI's live path always constructs the real SDK.
"""
import json
import os
import time

from .lab import Lab, write_json

MODEL = "gemini-4-argon"
QUESTION = "Can the supplied evidence distinguish a black-hole-universe hypothesis from standard explanations? Investigate data sufficiency and perform a numerically checked toy/control analysis if useful."
SYSTEM = '''You are Gemini Argon, the scientist in a computational dry lab. Inspect evidence first. Papers are summaries, not measurement catalogs. Never invent observations, errors, likelihoods or black-hole-universe probabilities. Before experiments state at least2 competing hypotheses with explicit prediction, falsification and assumptions. Alternative cosmologies need quantitative distinct predictions. Inconclusive is valid. Use controls, inspect checks, critique then revise. Do not hardcode a conclusion.
The source language is constrained numerical Python: no imports, file/network/env access, attribute introspection, classes, exceptions, decorators or dynamic calls. math.{sqrt,asinh,sinh,log,exp,pi,comb,isclose,isfinite,fabs,sin,cos,erf} and rng.{random,uniform,randint} are provided, plus basic builtins abs,all,any,bool,dict,enumerate,float,int,len,list,max,min,range,round,sorted,sum,tuple,zip. inputs is the saved JSON object. Assign a JSON object to result. For loops, functions, comprehensions and arithmetic are allowed. Code24KB, input16KB, output64KB, CPU2s, wall3s, memory256MiB. No print needed.
Use flat_age verifier only with .1<=h0<=10000(km/s/Mpc), 1e-6<=omega_m<=1-1e-6 and 0<=z<=10000, result.age_gyr; reference is exact flat matter+Lambda without radiation. Use binomial_control only for synthetic labels, n1..512, selection_probability0..1 and inputs.seed matching seed; result.k and result.p_value exact two-sided .5 null. finite_only verifies JSON finiteness, not scientific adequacy. Evidence IDs and experiment IDs must exist. Critique links parent experiment to revision. End by submit_report with claims [{kind:source_summary|computed|limitation,text,evidence_ids,experiment_ids}], unresolved_questions list. Computed claims require successful checked experiments. Citation validation does not establish semantic correctness. Single-pass mode: return ONLY that report JSON, with no computed claims because no tools execute. All conclusions must retain limitations.'''

STRING = {"type":"string"}
ARRAY = {"type":"array","items":STRING}
HYPOTHESIS = {"type":"object","properties":{k:STRING for k in ("id","prediction","falsification","assumptions")},"required":["id","prediction","falsification","assumptions"]}
PROPOSAL = {"question":STRING,"hypotheses":{"type":"array","items":HYPOTHESIS},"evidence_ids":ARRAY,"code":STRING,"inputs":{"type":"object","additionalProperties":True},"seed":{"type":"integer"},"verifier":{"type":"string","enum":["finite_only","flat_age","binomial_control"]}}
CLAIM = {"type":"object","properties":{"kind":{"type":"string","enum":["source_summary","computed","limitation"]},"text":STRING,"evidence_ids":ARRAY,"experiment_ids":ARRAY},"required":["kind","text","evidence_ids","experiment_ids"]}
SPECS = [
    ("inspect_evidence","Inspect registry, missing data, versions, units and uncertainties.",{"evidence_id":STRING},[]),
    ("propose_experiment","Register predictions and executable analysis BEFORE running.",PROPOSAL,["question","hypotheses","evidence_ids","code","inputs","seed"]),
    ("run_experiment","Execute one previously registered immutable experiment.",{"experiment_id":STRING},["experiment_id"]),
    ("inspect_artifact","Inspect saved proposal, inputs, code, execution or checks.",{"experiment_id":STRING,"artifact":STRING},["experiment_id"]),
    ("record_critique","Critique executed result and specify next test.",{"experiment_id":STRING,"finding":STRING,"next_test":STRING},["experiment_id","finding","next_test"]),
    ("revise_experiment","Create an explicit critique-linked revision with predictions.",{**PROPOSAL,"parent_id":STRING,"critique_id":STRING},["parent_id","critique_id","question","hypotheses","evidence_ids","code","inputs","seed"]),
    ("submit_report","Export evidence-linked scientific claims and unresolved questions.",{"claims":{"type":"array","items":CLAIM},"unresolved_questions":ARRAY},["claims","unresolved_questions"]),
]
TOOLS = [{"type":"function","name":name,"description":description,"parameters":{"type":"object","properties":properties,"required":required}} for name,description,properties,required in SPECS]


def plain(value):
    if value is None or isinstance(value,(dict,list,str,int,float,bool)):
        return value
    return value.model_dump(mode="json",exclude_none=True)


def run_live(root, *, single_pass=False, thinking_level="high", question=QUESTION, client=None, max_interactions=8, wall_seconds=150, max_output_tokens=4096):
    if thinking_level not in {"low","medium","high"}:
        raise ValueError("thinking level must be low, medium or high")
    if not 1 <= max_interactions <= 12 or not 1 <= wall_seconds <= 150 or not 256 <= max_output_tokens <= 8192:
        raise ValueError("live budgets exceed supported bounds")
    lab = Lab(root, mode="live", budget={"max_experiments":4,"max_tool_calls":24 if not single_pass else 0,"wall_seconds":wall_seconds})
    lab.state["question"] = question
    lab.event("research_question", {"question": question, "single_pass": single_pass})
    api_budget = {"max_interactions":1 if single_pass else max_interactions,"max_output_tokens_per_interaction":max_output_tokens,"thinking_level":thinking_level,"wall_seconds":wall_seconds,"token_usage":"reported by API, not estimated"}
    write_json(lab.root / "api-budget.json", api_budget)
    if client is None:
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            lab.event("blocked", {"reason":"Missing GEMINI_API_KEY (or GOOGLE_API_KEY); no live call attempted."})
            lab.finalize("blocked_credentials")
            return {"status":"blocked_credentials","message":"Missing GEMINI_API_KEY (or GOOGLE_API_KEY); no live Gemini call attempted."}
        from google import genai
        client = genai.Client(api_key=key, http_options={"retry_options":{"attempts":1}})
    request_input = question + "\nEvidence registry:\n" + json.dumps(lab.registry)
    previous = None
    responses = []
    try:
        for turn in range(api_budget["max_interactions"]):
            remaining = wall_seconds - (time.monotonic()-lab.started)
            if remaining <= 0:
                lab.finalize("wall_budget_exhausted")
                return {"status":"wall_budget_exhausted"}
            request = {"model":MODEL,"input":request_input,"system_instruction":SYSTEM,
                       "generation_config":{"thinking_level":thinking_level,"max_output_tokens":max_output_tokens},
                       "tools":[] if single_pass else TOOLS,"store":True,"timeout":remaining}
            if previous:
                request["previous_interaction_id"] = previous
            write_json(lab.root / "interactions" / f"{turn+1:03d}-request.json", {k:v for k,v in request.items() if k != "timeout"})
            response = plain(client.interactions.create(**request))
            snapshot = {k:response.get(k) for k in ("id","status","steps","output_text","usage")}
            responses.append(snapshot)
            write_json(lab.root / "interactions" / f"{turn+1:03d}-response.json", snapshot)
            lab.event("interaction_received", {"id":snapshot["id"],"status":snapshot["status"],"usage":snapshot["usage"]})
            if snapshot["status"] not in {"completed","requires_action"}:
                lab.finalize("api_" + str(snapshot["status"]))
                return {"status":lab.state["status"]}
            if single_pass:
                report = json.loads(snapshot["output_text"] or "")
                lab.submit_report(**report)
                break
            calls = [s for s in (snapshot["steps"] or []) if s.get("type") == "function_call"]
            if not calls:
                (lab.root / "final-model-text.txt").write_text(snapshot["output_text"] or "")
                break
            results = []
            for call in calls:
                result = lab.dispatch(call["name"], call["arguments"])
                results.append({"type":"function_result","call_id":call["id"],"name":call["name"],"result":json.dumps(result,allow_nan=False),"is_error":"error" in result})
            if lab.state["report"]:
                break
            previous = snapshot["id"]
            if not previous:
                raise ValueError("API response missing interaction id")
            request_input = results
        status = "reported" if lab.state["report"] else "incomplete_no_valid_report"
        metrics = lab.finalize(status)
        return {"status":status,"metrics":metrics,"interactions":len(responses)}
    except Exception as error:
        # Avoid serializing SDK exception text/URLs that might contain credentials.
        lab.event("live_error", {"type":type(error).__name__,"message":"Live invocation or response contract failed; no fallback model used."})
        lab.finalize("live_error")
        return {"status":"live_error","error_type":type(error).__name__,"message":"See saved request/response contracts; no fallback model or live-success claim."}
