"""Bounded constrained numerical execution, independent numerical verification."""
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

from .worker import check_finite, validate

LIMITS = {"wall_seconds": 3.0, "cpu_seconds": 2, "memory_bytes": 256 * 1024**2,
          "file_bytes": 128_000, "result_bytes": 64_000, "source_bytes": 24_000}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, indent=2, allow_nan=False).encode() + b"\n"


def restrict():
    resource.setrlimit(resource.RLIMIT_CPU, (LIMITS["cpu_seconds"], LIMITS["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_AS, (LIMITS["memory_bytes"], LIMITS["memory_bytes"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS["file_bytes"], LIMITS["file_bytes"]))
    resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def execute(code, inputs, seed):
    validate(code)
    request = canonical({"code": code, "inputs": inputs, "seed": seed})
    if len(request) > 64_000:
        raise ValueError("execution input exceeds 64000 bytes")
    start = time.monotonic()
    # Source cannot import, access files/environment, call arbitrary objects or
    # introspect. Child receives no inherited secrets, network tools or cwd data.
    with tempfile.TemporaryDirectory(prefix="argon-experiment-") as tmp:
        with open(Path(tmp) / "stdout", "w+b") as stdout, open(Path(tmp) / "stderr", "w+b") as stderr:
            child = subprocess.Popen(
                [sys.executable, "-I", str(Path(__file__).with_name("worker.py").resolve())],
                stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, cwd=tmp,
                env={"LANG": "C.UTF-8", "PYTHONHASHSEED": "0"},
                start_new_session=True, preexec_fn=restrict,
            )
            timed_out = False
            try:
                child.communicate(request, timeout=LIMITS["wall_seconds"])
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                child.communicate()
            stdout.seek(0)
            stderr.seek(0)
            out = stdout.read(LIMITS["result_bytes"] + 1)
            err = stderr.read(16_000).decode(errors="replace")
        status = "timeout" if timed_out else ("ok" if child.returncode == 0 else "error")
        if len(out) > LIMITS["result_bytes"]:
            status = "output_limit"
        result = None
        if status == "ok":
            try:
                result = json.loads(out)
            except (ValueError, UnicodeError):
                status = "invalid_output"
    return {"status": status, "result": result, "stderr": err, "returncode": child.returncode,
            "elapsed_seconds": time.monotonic() - start, "limits": LIMITS}


def verify(result, inputs, verifier):
    """Independent trusted references, not a pass flag written by the agent."""
    try:
        check_finite(result)
        finite = isinstance(result, dict)
    except (ValueError, RecursionError):
        finite = False
    checks = [{"name": "finite_json", "passed": finite}]
    if not finite:
        return checks
    check_finite(inputs)
    if verifier == "flat_age":
        h0, om, z = inputs["h0"], inputs["omega_m"], inputs["z"]
        if not (.1 <= h0 <= 10000 and 1e-6 <= om <= 1-1e-6 and 0 <= z <= 10000):
            raise ValueError("flat_age requires .1<=h0<=10000, 1e-6<=omega_m<=1-1e-6, 0<=z<=10000")
        # Exact flat matter+Lambda age, no radiation. 1 Mpc=3.0856775814913673e19 km;
        # Julian year=31557600 s. This is a toy reference, not the paper cosmology.
        hubble_gyr = 3.0856775814913673e19 / h0 / 31557600 / 1e9
        exact = hubble_gyr * 2 / (3 * math.sqrt(1-om)) * math.asinh(math.sqrt((1-om)/om) / (1+z)**1.5)
        actual = result.get("age_gyr")
        passed = isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isclose(actual, exact, rel_tol=1e-5, abs_tol=1e-8)
        checks.append({"name": "analytic_flat_age", "passed": passed, "reference_gyr": exact,
                       "actual_gyr": actual, "relative_tolerance": 1e-5})
    elif verifier == "binomial_control":
        n, p = inputs["n"], inputs["selection_probability"]
        if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 512 or not isinstance(p, (int,float)) or not 0 <= p <= 1:
            raise ValueError("binomial verifier requires n1..512 and probability0..1")
        import random
        rng = random.Random(inputs["seed"])
        k = sum(rng.random() < p for _ in range(n))
        # Independent recurrence for binomial tails avoids sharing experiment comb code.
        pmf = 2.0**(-n)
        tail = 0.0
        for j in range(n+1):
            if j <= min(k, n-k):
                tail += pmf
            pmf *= (n-j)/(j+1) if j < n else 1
        expected = min(1.0, 2*tail)
        checks.extend([
            {"name": "seeded_count", "passed": result.get("k") == k, "reference": k},
            {"name": "exact_two_sided_binomial", "passed": isinstance(result.get("p_value"), (int, float)) and math.isclose(result["p_value"], expected, rel_tol=1e-10, abs_tol=1e-14), "reference": expected},
        ])
    elif verifier != "finite_only":
        raise ValueError("unknown verifier")
    return checks


def checked_verify(result, inputs, verifier):
    """Persist verifier contract failures identically in original runs and replay."""
    try:
        return verify(result, inputs, verifier)
    except (ValueError, TypeError, KeyError, OverflowError, ArithmeticError) as error:
        return [{"name":"verifier_contract", "passed":False, "error":str(error)}]
