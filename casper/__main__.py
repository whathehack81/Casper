from __future__ import annotations

import argparse
import json
from pathlib import Path

from casper.core.runtime import CasperRuntime
from casper.tools.http_probe import probe_url
from casper.rules.builtin import successful_probe_rule


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



def cmd_evidence_list() -> None:
    runtime = build_runtime()
    runtime.initialize()

    print(json.dumps(
        runtime.evidence.export(),
        indent=2,
        sort_keys=True,
    ))


def cmd_finding_create(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    finding = runtime.create_finding(
        title=args.title,
        severity=args.severity,
    )

    print(json.dumps({
        "title": finding.title,
        "severity": finding.severity,
        "evidence_ids": finding.evidence_ids,
    }, indent=2, sort_keys=True))


def cmd_finding_list() -> None:
    runtime = build_runtime()
    runtime.initialize()

    print(json.dumps(
        runtime.findings.export(),
        indent=2,
        sort_keys=True,
    ))


def cmd_finding_link_evidence(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    finding = runtime.link_finding_evidence(
        title=args.title,
        evidence_id=args.evidence_id,
    )

    print(json.dumps({
        "title": finding.title,
        "severity": finding.severity,
        "evidence_ids": finding.evidence_ids,
    }, indent=2, sort_keys=True))


def cmd_report() -> None:
    runtime = build_runtime()
    session = runtime.initialize()

    try:
        target = runtime.load_target()
        target_payload = {
            "name": target.name,
            "scope": target.scope,
        }
    except FileNotFoundError:
        target_payload = None

    runtime.register_rule(successful_probe_rule(runtime.evidence))
    can_advance = runtime.validate()

    payload = {
        "session": {
            "session_id": session.session_id,
            "started_at": session.started_at,
            "status": session.status,
        },
        "target": target_payload,
        "can_advance": can_advance,
        "rule_results": [
            {
                "name": result.name,
                "passed": result.passed,
                "reason": result.reason,
            }
            for result in runtime.rules.results
        ],
        "evidence_count": len(runtime.evidence.all()),
        "findings_count": len(runtime.findings.all()),
        "findings": runtime.findings.export(),
    }

    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_target_set(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    target = runtime.set_target(
        name=args.name,
        scope=args.scope,
    )

    print(json.dumps({
        "name": target.name,
        "scope": target.scope,
    }, indent=2, sort_keys=True))


def cmd_target_show() -> None:
    runtime = build_runtime()
    runtime.initialize()

    target = runtime.load_target()

    print(json.dumps({
        "name": target.name,
        "scope": target.scope,
    }, indent=2, sort_keys=True))


def cmd_run_probe(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    result = probe_url(args.url)

    evidence = runtime.record_evidence(
        source="http-probe",
        content=result,
    )

    print(json.dumps({
        "evidence_id": evidence.evidence_id,
        "source": evidence.source,
        "content": evidence.content,
    }, indent=2, sort_keys=True))


def cmd_validate() -> None:
    runtime = build_runtime()
    runtime.initialize()
    runtime.register_rule(successful_probe_rule(runtime.evidence))

    print(json.dumps({
        "can_advance": runtime.validate(),
        "rule_results": [
            {
                "name": result.name,
                "passed": result.passed,
                "reason": result.reason,
            }
            for result in runtime.rules.results
        ],
    }, indent=2, sort_keys=True))

def main() -> None:
    parser = argparse.ArgumentParser(prog="casper")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")
    sub.add_parser("report")
    sub.add_parser("validate")

    run = sub.add_parser("run")
    run_sub = run.add_subparsers(dest="run_command")

    probe = run_sub.add_parser("probe")
    probe.add_argument("--url", required=True)

    target = sub.add_parser("target")
    target_sub = target.add_subparsers(dest="target_command")

    target_set = target_sub.add_parser("set")
    target_set.add_argument("--name", required=True)
    target_set.add_argument("--scope", required=True)

    target_sub.add_parser("show")

    finding = sub.add_parser("finding")
    finding_sub = finding.add_subparsers(dest="finding_command")

    finding_sub.add_parser("list")

    finding_link = finding_sub.add_parser("link-evidence")
    finding_link.add_argument("--title", required=True)
    finding_link.add_argument("--evidence-id", required=True)

    finding_create = finding_sub.add_parser("create")
    finding_create.add_argument("--title", required=True)
    finding_create.add_argument("--severity", required=True)

    evidence = sub.add_parser("evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_command")

    evidence_sub.add_parser("list")

    evidence_add = evidence_sub.add_parser("add")
    evidence_add.add_argument("--source", required=True)
    evidence_add.add_argument("--target", required=True)
    evidence_add.add_argument("--status", type=int, required=True)
    evidence_add.add_argument("--observation", required=True)

    args = parser.parse_args()

    if args.command in (None, "status"):
        cmd_status()
    elif args.command == "report":
        cmd_report()
    elif args.command == "validate":
        cmd_validate()
    elif args.command == "run" and args.run_command == "probe":
        cmd_run_probe(args)
    elif args.command == "target" and args.target_command == "set":
        cmd_target_set(args)
    elif args.command == "target" and args.target_command == "show":
        cmd_target_show()
    elif args.command == "evidence" and args.evidence_command == "add":
        cmd_evidence_add(args)
    elif args.command == "evidence" and args.evidence_command == "list":
        cmd_evidence_list()
    elif args.command == "finding" and args.finding_command == "create":
        cmd_finding_create(args)
    elif args.command == "finding" and args.finding_command == "list":
        cmd_finding_list()
    elif args.command == "finding" and args.finding_command == "link-evidence":
        cmd_finding_link_evidence(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
