"""Trusted constrained-Python worker; invoked in a credential-free child process.

This is a small numerical language implemented with Python AST validation, not a
sandbox for arbitrary Python or native extensions. Keep the whitelist narrow.
"""
import ast
import json
import math
import random
import sys

SAFE = {name: value for name, value in {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "float": float, "int": int, "len": len,
    "list": list, "max": max, "min": min, "range": range, "round": round,
    "sorted": sorted, "sum": sum, "tuple": tuple, "zip": zip,
}.items()}
MATH = {"sqrt", "asinh", "sinh", "log", "exp", "pi", "comb", "isclose", "isfinite", "fabs", "sin", "cos", "erf"}
ALLOWED = {
    ast.Module, ast.Assign, ast.AugAssign, ast.Expr, ast.Name, ast.Load,
    ast.Store, ast.Constant, ast.List, ast.Tuple, ast.Dict, ast.Subscript,
    ast.Slice, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.If,
    ast.IfExp, ast.For, ast.While, ast.Break, ast.Continue, ast.Pass,
    ast.Call, ast.keyword, ast.Attribute, ast.ListComp, ast.DictComp,
    ast.GeneratorExp, ast.comprehension, ast.FunctionDef, ast.arguments,
    ast.arg, ast.Return, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
    ast.Mod, ast.Pow, ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn,
}


def validate(code):
    if not isinstance(code, str) or len(code.encode()) > 24_000:
        raise ValueError("source must be text <=24000 bytes")
    tree = ast.parse(code)
    functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for node in ast.walk(tree):
        if type(node) not in ALLOWED:
            raise ValueError(f"unsupported syntax: {type(node).__name__}")
        for field in ("id", "name", "arg"):
            name = getattr(node, field, None)
            if isinstance(name, str) and name.startswith("_"):
                raise ValueError("private identifiers forbidden")
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            raise ValueError("decorators forbidden")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (str, int, float, bool, type(None))):
            raise ValueError("unsupported constant")
        if isinstance(node, ast.Attribute):
            if not isinstance(node.value, ast.Name) or not (
                (node.value.id == "math" and node.attr in MATH)
                or (node.value.id == "rng" and node.attr in {"random", "uniform", "randint"})
            ):
                raise ValueError("only documented math/rng attributes permitted")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id not in SAFE and node.func.id not in functions:
                    raise ValueError(f"call not permitted: {node.func.id}")
            elif not isinstance(node.func, ast.Attribute):
                raise ValueError("dynamic calls forbidden")
    return tree


def check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite result")
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ValueError("result keys must be strings")
        for item in value.values():
            check_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            check_finite(item)
    elif not isinstance(value, (str, int, float, bool, type(None))):
        raise ValueError("result must contain JSON values")


def evaluate(code, inputs, seed):
    tree = validate(code)
    namespace = {"__builtins__": SAFE, "math": math, "rng": random.Random(seed), "inputs": inputs}
    exec(compile(tree, "experiment.py", "exec"), namespace, namespace)
    result = namespace.get("result")
    if not isinstance(result, dict):
        raise ValueError("analysis must assign a JSON object to result")
    check_finite(result)
    encoded = json.dumps(result, sort_keys=True, allow_nan=False)
    if len(encoded.encode()) > 64_000:
        raise ValueError("result exceeds 64000 bytes")
    return encoded


if __name__ == "__main__":
    request = json.loads(sys.stdin.read(64_001))
    print(evaluate(request["code"], request["inputs"], request["seed"]))
