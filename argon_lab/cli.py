import argparse
import json
from pathlib import Path
import sys

from .fixture import compare_fixture, demo
from .gemini import QUESTION, run_live
from .lab import replay, write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description="Headless Argon scientific dry lab")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("demo", "compare-fixture", "replay", "live", "compare-live"):
        item = sub.add_parser(command)
        item.add_argument("--out" if command != "replay" else "--run", required=True, type=Path)
        if command in {"live","compare-live"}:
            item.add_argument("--thinking-level",choices=["low","medium","high"],default="high")
            item.add_argument("--question",default=QUESTION)
            if command == "live":
                item.add_argument("--single-pass",action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            result = demo(args.out)
        elif args.command == "compare-fixture":
            result = compare_fixture(args.out)
        elif args.command == "replay":
            result = replay(args.run)
        elif args.command == "live":
            result = run_live(args.out,single_pass=args.single_pass,thinking_level=args.thinking_level,question=args.question)
        else:
            args.out.mkdir(parents=True,exist_ok=False)
            single = run_live(args.out / "single-pass",single_pass=True,thinking_level=args.thinking_level,question=args.question)
            if single["status"] == "blocked_credentials":
                result = single
            else:
                iterative = run_live(args.out / "iterative",thinking_level=args.thinking_level,question=args.question)
                result = {"label":"LIVE PROCESS COMPARISON; NOT A COSMOLOGY TRUTH SCORE", "same_question_and_evidence":True,
                          "budget_policy":"Each arm has150s wall cap; single-pass1 interaction/no tools, iterative8 interactions/24 tools/4 experiments. Output cap4096 per request. Unequal compute explicitly recorded; inspect API usage per response.",
                          "single_pass":single,"iterative":iterative,"reproducibility":{arm:replay(args.out / arm) for arm in ("single-pass","iterative")},"quality_caveat":"Citation links and numerical checks do not measure semantic accuracy or establish causal improvement."}
                write_json(args.out / "comparison.json",result)
        print(json.dumps(result,indent=2,allow_nan=False))
        return 0 if result.get("status") in {None,"reported"} else 2
    except (ValueError, OSError, KeyError) as error:
        print(f"argon-lab: {error}",file=sys.stderr)
        return 2
