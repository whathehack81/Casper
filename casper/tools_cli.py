from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from typing import Any

from casper.tools.registry import (
    doctor_tools,
    get_profile,
    list_profiles,
    list_tools,
    run_registered_tool,
)


def print_json(payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_list(_: argparse.Namespace) -> None:
    print_json(list_tools())


def cmd_doctor(args: argparse.Namespace) -> None:
    try:
        print_json(doctor_tools(profile=args.profile))
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from None


def cmd_profiles(_: argparse.Namespace) -> None:
    print(json.dumps(list_profiles(), indent=2, sort_keys=True))


def cmd_profile(args: argparse.Namespace) -> None:
    try:
        print_json(get_profile(args.name))
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from None


def cmd_run(args: argparse.Namespace) -> None:
    argv = list(args.argv or [])
    if argv and argv[0] == "--":
        argv = argv[1:]

    try:
        result = run_registered_tool(
            tool_name=args.tool,
            argv=argv,
            run_id=args.run_id,
            lane=args.lane,
            target=args.target,
            timeout=args.timeout,
        )
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from None

    print_json(asdict(result))
    if result.exit_code != 0 and not args.allow_fail:
        raise SystemExit(result.exit_code)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="casper-tools")
    sub = parser.add_subparsers(dest="command")

    list_parser = sub.add_parser("list")
    list_parser.set_defaults(func=cmd_list)

    doctor_parser = sub.add_parser("doctor")
    doctor_parser.add_argument("--profile")
    doctor_parser.set_defaults(func=cmd_doctor)

    profiles_parser = sub.add_parser("profiles")
    profiles_parser.set_defaults(func=cmd_profiles)

    profile_parser = sub.add_parser("profile")
    profile_parser.add_argument("name")
    profile_parser.set_defaults(func=cmd_profile)

    run_parser = sub.add_parser("run")
    run_parser.add_argument("tool")
    run_parser.add_argument("--run-id", default="manual")
    run_parser.add_argument("--lane")
    run_parser.add_argument("--target")
    run_parser.add_argument("--timeout", type=int)
    run_parser.add_argument("--allow-fail", action="store_true")
    run_parser.add_argument("argv", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=cmd_run)

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
