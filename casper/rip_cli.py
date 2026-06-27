from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from casper.core.runtime import CasperRuntime
from casper.rip.validation import list_capsules, load_capsule, run_validation


def build_runtime() -> CasperRuntime:
    return CasperRuntime(workspace=Path.cwd() / ".casper")


def print_json(payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _argv(args: argparse.Namespace) -> list[str]:
    argv = list(args.argv or [])
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        raise SystemExit("error: validation command is required after --")
    return argv


def cmd_run(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    try:
        capsule = run_validation(
            runtime,
            argv=_argv(args),
            title=args.title,
            finding_id=args.finding_id,
            target=args.target,
            validator=args.validator,
            repetitions=args.repetitions,
            required_passes=args.required_passes,
            expect_exit_code=args.expect_exit_code,
            expect_stdout=list(args.expect_stdout or []),
            expect_stderr=list(args.expect_stderr or []),
            timeout=args.timeout,
            run_id=args.run_id,
        )
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from None

    print_json(asdict(capsule))
    if capsule.status != "VERIFIED" and not args.allow_fail:
        raise SystemExit(1)


def cmd_list(_: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    print_json(list_capsules(runtime.workspace))


def cmd_show(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    try:
        print_json(load_capsule(runtime.workspace, args.validation_id))
    except FileNotFoundError as exc:
        raise SystemExit(f"error: {exc}") from None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="casper rip")
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run")
    run_parser.add_argument("--title")
    run_parser.add_argument("--finding-id")
    run_parser.add_argument("--target")
    run_parser.add_argument("--validator", default="rip")
    run_parser.add_argument("--repetitions", type=int, default=3)
    run_parser.add_argument("--required-passes", type=int)
    run_parser.add_argument("--expect-exit-code", type=int, default=0)
    run_parser.add_argument("--expect-stdout", "--stdout-contains", dest="expect_stdout", action="append")
    run_parser.add_argument("--expect-stderr", "--stderr-contains", dest="expect_stderr", action="append")
    run_parser.add_argument("--timeout", type=int, default=60)
    run_parser.add_argument("--run-id", default="manual")
    run_parser.add_argument("--allow-fail", action="store_true")
    run_parser.add_argument("argv", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=cmd_run)

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(func=cmd_list)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("validation_id")
    show_parser.set_defaults(func=cmd_show)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
