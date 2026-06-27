from __future__ import annotations

import argparse
from dataclasses import asdict
import json

from casper.tools.registry import list_tools, run_registered_tool


def print_json(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_list(_: argparse.Namespace) -> None:
    print_json(list_tools())


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
