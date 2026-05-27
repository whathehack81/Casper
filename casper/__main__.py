from __future__ import annotations

import argparse
import json
from pathlib import Path

from casper.core.runtime import CasperRuntime


def build_runtime() -> CasperRuntime:
    return CasperRuntime(workspace=Path.cwd() / ".casper")


def cmd_status() -> None:
    runtime = build_runtime()
    session = runtime.initialize()

    print(json.dumps({
        "workspace": str(runtime.workspace),
        "session_id": session.session_id,
        "can_advance": runtime.validate(),
        "evidence_count": len(runtime.evidence.all()),
        "rule_count": len(runtime.rules.rules),
    }, indent=2, sort_keys=True))


def cmd_evidence_add(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    evidence = runtime.record_evidence(
        source=args.source,
        content={
            "target": args.target,
            "status": args.status,
            "observation": args.observation,
        },
    )

    print(json.dumps({
        "evidence_id": evidence.evidence_id,
        "source": evidence.source,
        "content": evidence.content,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(prog="casper")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")

    evidence = sub.add_parser("evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_command")

    evidence_add = evidence_sub.add_parser("add")
    evidence_add.add_argument("--source", required=True)
    evidence_add.add_argument("--target", required=True)
    evidence_add.add_argument("--status", type=int, required=True)
    evidence_add.add_argument("--observation", required=True)

    args = parser.parse_args()

    if args.command in (None, "status"):
        cmd_status()
    elif args.command == "evidence" and args.evidence_command == "add":
        cmd_evidence_add(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
