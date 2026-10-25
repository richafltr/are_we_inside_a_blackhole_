import json
from types import SimpleNamespace

from google import genai
from google.genai import interactions

from argon_lab.cli import main
from argon_lab.gemini import MODEL, SYSTEM, TOOLS, run_live


class FakeInteractions:
    """Synthetic transport contract ONLY, never evidence of live model behavior."""
    def __init__(self,responses):
        self.responses = iter(responses)
        self.requests = []

    def create(self,**request):
        interactions.CreateModelInteraction.model_validate({k:v for k,v in request.items() if k != "timeout"})
        self.requests.append(request)
        return next(self.responses)


def claim():
    return {"claims":[{"kind":"limitation","text":"Synthetic transport report: missing calibrated data.","evidence_ids":["shamir-jades"],"experiment_ids":[]}],"unresolved_questions":["What is the selection function?"]}


def test_sdk_contract_real_types_no_network():
    client = genai.Client(api_key="synthetic-not-a-live-key",http_options={"retry_options":{"attempts":1}})
    assert callable(client.interactions.create)
    validated = interactions.CreateModelInteraction.model_validate({"model":MODEL,"input":"test","generation_config":{"thinking_level":"high","max_output_tokens":4096},"tools":TOOLS,"system_instruction":SYSTEM})
    assert validated.model == MODEL
    result = interactions.FunctionResultStep.model_validate({"type":"function_result","call_id":"a","name":"inspect_evidence","result":"{}"})
    assert result.call_id == "a"


def test_tool_continuation_resends_system_tools_generation(tmp_path):
    transport = FakeInteractions([
        {"id":"first","status":"requires_action","steps":[{"type":"function_call","id":"call-1","name":"inspect_evidence","arguments":{}}],"usage":{"total_tokens":50}},
        {"id":"second","status":"requires_action","steps":[{"type":"function_call","id":"call-2","name":"submit_report","arguments":claim()}],"usage":{"total_tokens":70}},
    ])
    result = run_live(tmp_path / "transport",client=SimpleNamespace(interactions=transport))
    assert result["status"] == "reported"
    assert len(transport.requests) == 2
    first,second = transport.requests
    assert first["tools"] == second["tools"] == TOOLS
    assert first["system_instruction"] == second["system_instruction"] == SYSTEM
    assert first["generation_config"] == second["generation_config"] == {"thinking_level":"high","max_output_tokens":4096}
    assert second["previous_interaction_id"] == "first"
    assert second["input"][0]["call_id"] == "call-1"
    assert second["input"][0]["type"] == "function_result"
    assert all(request["model"] == MODEL for request in transport.requests)


def test_single_pass_has_no_tools_and_records_report(tmp_path):
    transport=FakeInteractions([{"id":"a","status":"completed","steps":[],"output_text":json.dumps(claim())}])
    result=run_live(tmp_path / "baseline",single_pass=True,client=SimpleNamespace(interactions=transport))
    assert result["status"] == "reported"
    assert transport.requests[0]["tools"] == []
    assert result["metrics"]["executed_experiments"] == 0


def test_bad_status_or_text_never_claims_success(tmp_path):
    transport=FakeInteractions([{"id":"a","status":"incomplete","steps":[],"output_text":"unverified"}])
    result=run_live(tmp_path / "incomplete",client=SimpleNamespace(interactions=transport))
    assert result["status"] == "api_incomplete"
    transport=FakeInteractions([{"id":"a","status":"completed","steps":[],"output_text":"unstructured"}])
    result=run_live(tmp_path / "text",client=SimpleNamespace(interactions=transport))
    assert result["status"] == "incomplete_no_valid_report"


def test_missing_key_explicit_and_saves_failure(monkeypatch,tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY",raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY",raising=False)
    assert main(["live","--out",str(tmp_path / "blocked")]) == 2
    state=json.loads((tmp_path / "blocked/state.json").read_text())
    assert state["status"] == "blocked_credentials"
    assert not (tmp_path / "blocked/interactions").exists()
