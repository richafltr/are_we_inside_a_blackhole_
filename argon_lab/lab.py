"""Durable tool contracts and an inspectable scientific investigation state."""
from copy import deepcopy
import json
from pathlib import Path
import platform
import subprocess
import time

from .execution import canonical, checked_verify, digest, execute
from .worker import check_finite, validate

DATA = Path(__file__).with_name("data") / "evidence.json"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical(data))
    temporary.replace(path)


def text_required(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 24000:
        raise ValueError(f"{name} must be nonempty text <=24000 characters")
    return value


class Lab:
    def __init__(self, root, mode="fixture", budget=None):
        self.root = Path(root).resolve()
        if self.root.exists() and any(self.root.iterdir()):
            raise ValueError("run directory must be empty (prevent accidental overwrite)")
        self.root.mkdir(parents=True, exist_ok=True)
        self.started = time.monotonic()
        self.budget = budget or {"max_experiments": 4, "max_tool_calls": 24, "wall_seconds": 150}
        self.registry = json.loads(DATA.read_text())
        self.evidence = {entry["id"]: entry for entry in self.registry["entries"]}
        self.state = {"schema_version": 1, "mode": mode, "question": None,
                      "budget": self.budget, "tool_calls": 0, "experiments": {},
                      "critiques": [], "report": None, "status": "in_progress"}
        write_json(self.root / "evidence.json", self.registry)
        for name in ("worker.py", "execution.py"):
            target = self.root / "runtime" / name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(Path(__file__).with_name(name).read_bytes())
        lock = Path(__file__).resolve().parent.parent / "requirements.lock"
        if lock.exists():
            (self.root / "runtime" / "requirements.lock").write_bytes(lock.read_bytes())
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unavailable"
        write_json(self.root / "environment.json", {"python": platform.python_version(), "platform": platform.platform(), "git_commit": commit, "model": "gemini-4-argon" if mode == "live" else None, "fixture_is_model_output": False})
        self.event("created", {"mode": mode, "budget": self.budget})

    def event(self, kind, data):
        with (self.root / "trace.jsonl").open("a") as stream:
            stream.write(json.dumps({"event": kind, "data": data}, sort_keys=True, allow_nan=False) + "\n")
        write_json(self.root / "state.json", self.state)

    def references(self, ids):
        if not isinstance(ids, list) or not ids or any(i not in self.evidence for i in ids):
            raise ValueError("evidence_ids must reference existing registry entries")

    def dispatch(self, name, request):
        if self.state["tool_calls"] >= self.budget["max_tool_calls"]:
            raise ValueError("tool-call budget exhausted")
        if time.monotonic() - self.started >= self.budget["wall_seconds"]:
            raise ValueError("investigation wall budget exhausted")
        self.state["tool_calls"] += 1
        self.event("tool_call", {"name": name, "request": request})
        try:
            handler = {"inspect_evidence": self.inspect_evidence, "propose_experiment": self.propose_experiment,
                       "run_experiment": self.run_experiment, "inspect_artifact": self.inspect_artifact,
                       "record_critique": self.record_critique, "revise_experiment": self.revise_experiment,
                       "submit_report": self.submit_report}[name]
            result = handler(**request)
        except (KeyError, TypeError, ValueError, SyntaxError, OverflowError) as error:
            self.event("tool_error", {"name": name, "error": str(error)})
            return {"error": str(error)}
        self.event("tool_result", {"name": name, "result": result})
        return result

    def inspect_evidence(self, evidence_id=None):
        return self.evidence[evidence_id] if evidence_id else self.registry

    def propose_experiment(self, question, hypotheses, evidence_ids, code, inputs, seed, verifier="finite_only", parent_id=None, critique_id=None):
        if len(self.state["experiments"]) >= self.budget["max_experiments"]:
            raise ValueError("experiment budget exhausted")
        text_required(question, "question")
        self.references(evidence_ids)
        if not isinstance(hypotheses, list) or len(hypotheses) < 2:
            raise ValueError("at least two competing hypotheses required")
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                raise ValueError("each hypothesis must be an object")
            for key in ("id", "prediction", "falsification", "assumptions"):
                text_required(hypothesis.get(key), key)
        if len({h["id"] for h in hypotheses}) != len(hypotheses):
            raise ValueError("hypothesis IDs must be distinct")
        validate(code)
        if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed < 2**32:
            raise ValueError("seed must be an integer in [0,2**32)")
        check_finite(inputs)
        if not isinstance(inputs, dict) or len(canonical(inputs)) > 16000:
            raise ValueError("inputs must be a JSON object <=16000 bytes")
        if verifier not in {"finite_only", "flat_age", "binomial_control"}:
            raise ValueError("unknown verifier")
        if verifier == "flat_age":
            if not all(isinstance(inputs.get(k), (int, float)) and not isinstance(inputs[k], bool) for k in ("h0", "omega_m", "z")):
                raise ValueError("flat_age requires numeric h0,omega_m,z")
            if not (.1 <= inputs["h0"] <= 10000 and 1e-6 <= inputs["omega_m"] <= 1-1e-6 and 0 <= inputs["z"] <= 10000):
                raise ValueError("invalid flat_age parameters")
        if verifier == "binomial_control":
            if not isinstance(inputs.get("n"), int) or not 1 <= inputs["n"] <= 512 or not 0 <= inputs.get("selection_probability", -1) <= 1 or inputs.get("seed") != seed:
                raise ValueError("binomial_control needs 1<=n<=512, probability [0,1], matching seed")
            if "synthetic-selection-control" not in evidence_ids:
                raise ValueError("binomial control must cite synthetic evidence")
        if parent_id:
            if parent_id not in self.state["experiments"] or self.state["experiments"][parent_id]["status"] == "proposed":
                raise ValueError("revision parent must have been executed")
            if not any(c["id"] == critique_id and c["experiment_id"] == parent_id for c in self.state["critiques"]):
                raise ValueError("revision requires an existing critique of its parent")
        elif critique_id:
            raise ValueError("critique_id requires parent_id")
        eid = f"exp-{len(self.state['experiments'])+1:03d}"
        proposal = {"id": eid, "question": question, "hypotheses": deepcopy(hypotheses), "evidence_ids": evidence_ids,
                    "seed": seed, "verifier": verifier, "parent_id": parent_id, "critique_id": critique_id,
                    "status": "proposed", "code_sha256": digest(code.encode()), "inputs_sha256": digest(canonical(inputs))}
        folder = self.root / "experiments" / eid
        folder.mkdir(parents=True)
        (folder / "experiment.py").write_text(code)
        write_json(folder / "inputs.json", inputs)
        write_json(folder / "proposal.json", proposal)
        self.state["experiments"][eid] = proposal
        self.state["question"] = self.state["question"] or question
        self.event("prediction_registered_before_execution", proposal)
        return proposal

    def run_experiment(self, experiment_id):
        proposal = self.state["experiments"][experiment_id]
        if proposal["status"] != "proposed":
            raise ValueError("experiment immutable after run; create a critique-linked revision")
        folder = self.root / "experiments" / experiment_id
        code = (folder / "experiment.py").read_text()
        inputs = json.loads((folder / "inputs.json").read_text())
        if digest(code.encode()) != proposal["code_sha256"] or digest(canonical(inputs)) != proposal["inputs_sha256"]:
            raise ValueError("proposal source/input hash changed")
        execution = execute(code, inputs, proposal["seed"])
        checks = checked_verify(execution["result"], inputs, proposal["verifier"])
        write_json(folder / "execution.json", execution)
        write_json(folder / "checks.json", checks)
        proposal["status"] = execution["status"]
        proposal["checks_passed"] = all(c["passed"] for c in checks)
        self.event("experiment_executed", {"experiment_id": experiment_id, "status": execution["status"], "checks": checks})
        return {"experiment_id": experiment_id, "execution": execution, "checks": checks}

    def inspect_artifact(self, experiment_id, artifact="execution.json"):
        if experiment_id not in self.state["experiments"] or artifact not in {"proposal.json", "inputs.json", "experiment.py", "execution.json", "checks.json"}:
            raise ValueError("unknown experiment/artifact")
        path = self.root / "experiments" / experiment_id / artifact
        if not path.exists():
            raise ValueError("artifact does not yet exist")
        return {"path": str(path.relative_to(self.root)), "content": path.read_text()}

    def record_critique(self, experiment_id, finding, next_test):
        proposal = self.state["experiments"][experiment_id]
        if proposal["status"] == "proposed":
            raise ValueError("run experiment before critiquing")
        text_required(finding, "finding")
        text_required(next_test, "next_test")
        critique = {"id": f"critique-{len(self.state['critiques'])+1:03d}", "experiment_id": experiment_id,
                    "finding": finding, "next_test": next_test}
        self.state["critiques"].append(critique)
        self.event("critique", critique)
        return critique

    def revise_experiment(self, parent_id, critique_id, question, hypotheses, evidence_ids, code, inputs, seed, verifier="finite_only"):
        return self.propose_experiment(question, hypotheses, evidence_ids, code, inputs, seed, verifier, parent_id, critique_id)

    def submit_report(self, claims, unresolved_questions):
        if not isinstance(claims, list) or not claims:
            raise ValueError("report needs claims")
        for claim in claims:
            if not isinstance(claim, dict):
                raise ValueError("each claim must be an object")
            text_required(claim.get("text"), "claim.text")
            self.references(claim.get("evidence_ids"))
            if claim.get("kind") not in {"source_summary", "computed", "limitation"}:
                raise ValueError("claim kind must be source_summary, computed or limitation")
            experiments = claim.get("experiment_ids", [])
            if not isinstance(experiments, list) or any(not isinstance(e, str) for e in experiments):
                raise ValueError("experiment_ids must be a list of IDs")
            if any(e not in self.state["experiments"] for e in experiments):
                raise ValueError("unknown claim experiment")
            if claim["kind"] == "computed" and (not experiments or any(self.state["experiments"][e]["status"] != "ok" or not self.state["experiments"][e].get("checks_passed") for e in experiments)):
                raise ValueError("computed claim requires successful independently checked experiments")
        if not isinstance(unresolved_questions, list) or not unresolved_questions:
            raise ValueError("record unresolved questions")
        for question in unresolved_questions:
            text_required(question, "unresolved question")
        self.state["report"] = {"claims": claims, "unresolved_questions": unresolved_questions}
        self.state["status"] = "reported"
        self.event("report_submitted", self.state["report"])
        self.render_report()
        return {"path": "report.md", "claims": len(claims)}

    def render_report(self):
        report = self.state["report"]
        lines = ["# Scientific dry-lab report", "", f"Mode: **{self.state['mode']}**.", "",
                 "Fixture mode is authored software validation, not a Gemini response or observational analysis. Live mode records unreviewed model-authored claims; citation validation does not establish their scientific truth.", "",
                 "No probability of a black-hole universe is computed by this laboratory.", ""]
        if report:
            for claim in report["claims"]:
                lines.append(f"- **{claim['kind']}**: {claim['text']}")
                for eid in claim["evidence_ids"]:
                    entry = self.evidence[eid]
                    lines.append(f"  - [{eid}](evidence.json): {entry['version']}; [primary source]({entry['sources'][0]}).")
                for eid in claim.get("experiment_ids", []):
                    lines.append(f"  - [{eid} result](experiments/{eid}/execution.json) · [code](experiments/{eid}/experiment.py) · [checks](experiments/{eid}/checks.json)")
            lines.extend(["", "## Unresolved questions", ""] + [f"- {q}" for q in report["unresolved_questions"]])
        else:
            lines.append("No completed scientific report. Inspect state.json and trace.jsonl for the stop/failure reason.")
        lines.extend(["", "Paper summaries are not measurement catalogs. Toy flat matter+Lambda ages omit radiation and do not reproduce the paper's adopted cosmology. Synthetic direction counts are not JADES measurements. A numerical tail probability is conditional on a toy null, never a cosmological posterior.", ""])
        (self.root / "report.md").write_text("\n".join(lines))

    def finalize(self, status=None):
        if status:
            self.state["status"] = status
        self.event("finalized", {"status": self.state["status"]})
        self.render_report()
        metrics = self.metrics()
        write_json(self.root / "metrics.json", metrics)
        files = {str(p.relative_to(self.root)): digest(p.read_bytes()) for p in self.root.rglob("*") if p.is_file() and p.name != "manifest.json"}
        write_json(self.root / "manifest.json", {"schema_version": 1, "files": files})
        return metrics

    def metrics(self):
        experiments = self.state["experiments"]
        checks = []
        for eid in experiments:
            path = self.root / "experiments" / eid / "checks.json"
            if path.exists():
                checks.extend(json.loads(path.read_text()))
        claims = (self.state["report"] or {}).get("claims", [])
        return {"mode": self.state["mode"], "is_model_benchmark": self.state["mode"] == "live" and any((self.root / "interactions").glob("*-response.json")),
                "budget": self.budget, "tool_calls": self.state["tool_calls"], "experiments": len(experiments),
                "executed_experiments": sum(e["status"] != "proposed" for e in experiments.values()),
                "checks_passed": sum(c["passed"] for c in checks), "checks_total": len(checks),
                "critiques": len(self.state["critiques"]), "revisions": sum(bool(e["parent_id"]) for e in experiments.values()),
                "claims_with_valid_registry_links": len(claims), "elapsed_seconds": time.monotonic() - self.started,
                "reproducibility": "measured separately by deterministic replay", "semantic_claim_accuracy": "not measured"}


def replay(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    for relative, expected in manifest["files"].items():
        path = root / relative
        if not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError(f"artifact integrity failure: {relative}")
    state = json.loads((root / "state.json").read_text())
    for name in ("worker.py", "execution.py"):
        if (root / "runtime" / name).read_bytes() != Path(__file__).with_name(name).read_bytes():
            raise ValueError("runtime differs from archived runtime; use matching checkout")
    results = []
    for eid, proposal in state["experiments"].items():
        if proposal["status"] == "proposed":
            continue
        if not eid.startswith("exp-") or not eid[4:].isdigit():
            raise ValueError("invalid experiment identifier")
        folder = root / "experiments" / eid
        code = (folder / "experiment.py").read_text()
        inputs = json.loads((folder / "inputs.json").read_text())
        if digest(code.encode()) != proposal["code_sha256"] or digest(canonical(inputs)) != proposal["inputs_sha256"]:
            raise ValueError("proposal integrity mismatch")
        original = json.loads((folder / "execution.json").read_text())
        rerun = execute(code, inputs, proposal["seed"])
        checks = checked_verify(rerun["result"], inputs, proposal["verifier"])
        if original["status"] != rerun["status"] or original["result"] != rerun["result"] or checks != json.loads((folder / "checks.json").read_text()):
            raise ValueError(f"recomputation differs: {eid}")
        results.append({"experiment_id": eid, "recomputed": True, "checks_passed": all(c["passed"] for c in checks)})
    return {"mode": state["mode"], "integrity_verified": True, "recomputed_experiments": results,
            "note": "Hash consistency and deterministic recomputation, not authenticity or scientific truth. Failed numerical checks remain failed."}
