import json
import math
from pathlib import Path

import pytest

from argon_lab.execution import canonical, digest, execute, verify
from argon_lab.fixture import AGE_CODE, AGE_HYPOTHESES, compare_fixture, demo
from argon_lab.lab import Lab, replay
from argon_lab.worker import validate


def proposal(**changes):
    request = dict(question="Numerical adequacy?", hypotheses=AGE_HYPOTHESES,
                   evidence_ids=["naidu-momz14"], code=AGE_CODE,
                   inputs={"h0":67.4,"omega_m":.315,"z":14.44,"steps":8192}, seed=42, verifier="flat_age")
    return {**request, **changes}


def test_demo_recomputes_and_preserves_failed_check(tmp_path):
    result = demo(tmp_path / "demo")
    assert result["metrics"]["mode"] == "fixture"
    assert result["metrics"]["checks_passed"] == 6
    assert result["metrics"]["checks_total"] == 7
    assert [e["checks_passed"] for e in result["replay"]["recomputed_experiments"]] == [False,True,True]
    state = json.loads((tmp_path / "demo/state.json").read_text())
    assert state["experiments"]["exp-002"]["critique_id"] == "critique-001"
    trace = [json.loads(line) for line in (tmp_path / "demo/trace.jsonl").read_text().splitlines()]
    before = next(i for i,e in enumerate(trace) if e["event"] == "prediction_registered_before_execution")
    after = next(i for i,e in enumerate(trace) if e["event"] == "experiment_executed")
    assert before < after
    assert state["report"]["claims"][1]["evidence_ids"][0] == "synthetic-selection-control"


def test_tamper_detected(tmp_path):
    root = tmp_path / "demo"
    demo(root)
    (root / "experiments/exp-002/inputs.json").write_text('{}')
    with pytest.raises(ValueError,match="integrity"):
        replay(root)


def test_replay_recomputes_even_if_manifest_rehashed(tmp_path):
    root = tmp_path / "demo"
    demo(root)
    result_file = root / "experiments/exp-002/execution.json"
    data = json.loads(result_file.read_text())
    data["result"]["age_gyr"] = 99
    result_file.write_bytes(canonical(data))
    manifest = json.loads((root / "manifest.json").read_text())
    manifest["files"][str(result_file.relative_to(root))] = digest(result_file.read_bytes())
    (root / "manifest.json").write_bytes(canonical(manifest))
    with pytest.raises(ValueError,match="recomputation differs"):
        replay(root)


@pytest.mark.parametrize("code", ["import os", "result = open('/etc/passwd').read()", "result = inputs.__class__", "result = getattr(math, 'sqrt')(4)", "result = (lambda:1)()", "@sum\ndef f():\n return 1", "result = math.__dict__", "result = [x for x in range(3) if (x := 1)]"])
def test_restricted_language_blocks_host_access(code):
    with pytest.raises(ValueError):
        validate(code)


def test_resource_limits_and_nonfinite():
    assert execute("while True:\n pass", {}, 1)["status"] in {"error","timeout"}
    assert execute("result = {'x': 1e309}", {}, 1)["status"] == "error"
    assert execute("result = {'x': 'a'*1000000}", {}, 1)["status"] == "error"
    assert execute("result = {'x': [1]*100000000}", {}, 1)["status"] == "error"


def test_no_credentials_in_worker(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "must-never-appear")
    execution = execute("result = {'answer': math.sqrt(4)}", {}, 1)
    assert execution["result"] == {"answer":2.0}
    assert "must-never-appear" not in json.dumps(execution)
    with pytest.raises(ValueError):
        validate("result = {'key': os.environ['GEMINI_API_KEY']}")


def test_prediction_contract_and_budget(tmp_path):
    lab = Lab(tmp_path / "lab",budget={"max_experiments":1,"max_tool_calls":5,"wall_seconds":150})
    assert "error" in lab.dispatch("propose_experiment",proposal(hypotheses=[]))
    assert "error" in lab.dispatch("propose_experiment",proposal(hypotheses=[None,None]))
    assert "error" in lab.dispatch("propose_experiment",proposal(evidence_ids=["invented"]))
    good = lab.dispatch("propose_experiment",proposal())
    assert good["id"] == "exp-001"
    assert "error" in lab.dispatch("propose_experiment",proposal())
    with pytest.raises(ValueError,match="budget"):
        lab.dispatch("inspect_evidence",{})


def test_immutable_execution_and_critique_gate(tmp_path):
    lab = Lab(tmp_path / "lab")
    first = lab.propose_experiment(**proposal())
    with pytest.raises(ValueError,match="executed"):
        lab.revise_experiment(parent_id=first["id"],critique_id="fake",**proposal())
    lab.run_experiment(first["id"])
    with pytest.raises(ValueError,match="immutable"):
        lab.run_experiment(first["id"])
    with pytest.raises(ValueError,match="critique"):
        lab.revise_experiment(parent_id=first["id"],critique_id="fake",**proposal())


@pytest.mark.parametrize("inputs", [
    {"h0":67.4,"omega_m":.315,"z":1e300},
    {"h0":float('nan'),"omega_m":.315,"z":14.44},
    {"h0":0,"omega_m":.315,"z":14.44},
    {"h0":67.4,"omega_m":1,"z":14.44},
])
def test_verifier_domains_rejected_before_execution(tmp_path,inputs):
    lab = Lab(tmp_path / "lab")
    with pytest.raises(ValueError):
        lab.propose_experiment(**proposal(inputs=inputs))


def test_verifier_direct_bounds_and_finiteness():
    with pytest.raises(ValueError):
        verify({"k":1,"p_value":1},{"n":10**12,"selection_probability":.5,"seed":1},"binomial_control")
    assert verify({"x":float('nan')},{},"finite_only") == [{"name":"finite_json","passed":False}]
    assert not verify({"age_gyr":99},{"h0":67.4,"omega_m":.315,"z":14.44},"flat_age")[-1]["passed"]


def test_report_references_and_failed_computed_claim(tmp_path):
    lab = Lab(tmp_path / "lab")
    first = lab.propose_experiment(**proposal(inputs={"h0":67.4,"omega_m":.315,"z":14.44,"steps":8}))
    lab.run_experiment(first["id"])
    for claims in ([None],[{"text":"bad","kind":"computed","evidence_ids":["naidu-momz14"],"experiment_ids":[first["id"]]}],[{"text":"bad","kind":"limitation","evidence_ids":["invented"],"experiment_ids":[]}]):
        with pytest.raises(ValueError):
            lab.submit_report(claims=claims,unresolved_questions=["what data?"])


def test_comparison_is_not_model_benchmark(tmp_path):
    comparison = compare_fixture(tmp_path / "comparison")
    assert "NOT GEMINI" in comparison["label"]
    assert comparison["single_pass"]["executed_experiments"] == 0
    assert comparison["iterative"]["executed_experiments"] == 3
    assert comparison["iterative"]["semantic_claim_accuracy"] == "not measured"


def test_verifier_contract_error_replays_as_failed_check(tmp_path):
    lab = Lab(tmp_path / "lab")
    first = lab.propose_experiment(**proposal(code="result = {'age_gyr': 10**400}"))
    result = lab.run_experiment(first["id"])
    assert result["checks"][-1]["passed"] is False
    lab.finalize()
    assert replay(tmp_path / "lab")["recomputed_experiments"][0]["checks_passed"] is False


def test_malformed_analysis_is_recoverable_tool_error(tmp_path):
    lab = Lab(tmp_path / "lab")
    assert "error" in lab.dispatch("propose_experiment",proposal(code="result = ("))
    assert lab.dispatch("propose_experiment",proposal())["id"] == "exp-001"
