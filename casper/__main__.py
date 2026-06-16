from __future__ import annotations
import sys

import argparse
import json
from pathlib import Path

from casper.core.runtime import CasperRuntime
from casper.rules.builtin import successful_probe_rule
from casper.tools.executor import export_result, persist_artifacts, run_command
from casper.tools.http_probe import probe_url
from casper.runtime.manifest import build_manifest, write_manifest
from casper.events.store import EventStore
from casper.workers.worker import create_worker
from casper.replay.replay import replay_digest
from casper.projections.session_projection import rebuild_session


def build_runtime() -> CasperRuntime:
    return CasperRuntime(workspace=Path.cwd() / ".casper")


def print_json(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_status() -> None:
    runtime = build_runtime()
    session = runtime.initialize()
    print_json({
        "workspace": str(runtime.workspace),
        "session_id": session.session_id,
        "can_advance": runtime.validate(),
        "evidence_count": len(runtime.evidence.all()),
        "rule_count": len(runtime.rules.rules),
    })


def cmd_cmd(args: argparse.Namespace) -> None:
    command = args.argv
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("missing command")

    runtime = build_runtime()
    runtime.initialize()

    result = run_command(command)
    exported = export_result(result)
    artifacts = persist_artifacts(result, runtime.workspace)

    evidence_payload = {
        "command": exported["command"],
        "exit_code": exported["exit_code"],
        "timestamp": exported["timestamp"],
        "sha256": exported["sha256"],
        "stdout_path": artifacts["stdout_path"],
        "stderr_path": artifacts["stderr_path"],
        "stdout_bytes": len(result.stdout.encode()),
        "stderr_bytes": len(result.stderr.encode()),
    }

    evidence = runtime.record_evidence(
        source="command-exec",
        content=evidence_payload,
    )

    exported = evidence_payload
    exported["evidence_id"] = evidence.evidence_id

    print_json(exported)


def cmd_evidence_list() -> None:
    runtime = build_runtime()
    runtime.initialize()
    print_json(runtime.evidence.export())


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
    print_json({
        "evidence_id": evidence.evidence_id,
        "source": evidence.source,
        "content": evidence.content,
    })


def cmd_target_set(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    target = runtime.set_target(args.name, args.scope)
    print_json({"name": target.name, "scope": target.scope})


def cmd_target_show() -> None:
    runtime = build_runtime()
    runtime.initialize()
    target = runtime.load_target()
    print_json({"name": target.name, "scope": target.scope})


def cmd_run_probe(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    result = probe_url(args.url)
    evidence = runtime.record_evidence("http-probe", result)
    print_json({
        "evidence_id": evidence.evidence_id,
        "source": evidence.source,
        "content": evidence.content,
    })


def cmd_run_target() -> None:
    runtime = build_runtime()
    runtime.initialize()
    target = runtime.load_target()

    url = target.name
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    result = probe_url(url)
    evidence = runtime.record_evidence("http-probe", result)

    runtime.register_rule(successful_probe_rule(runtime.evidence))
    can_advance = runtime.validate()

    print_json({
        "target": {"name": target.name, "scope": target.scope},
        "probe": result,
        "evidence_id": evidence.evidence_id,
        "can_advance": can_advance,
    })


def cmd_validate() -> None:
    runtime = build_runtime()
    runtime.initialize()
    runtime.register_rule(successful_probe_rule(runtime.evidence))

    print_json({
        "can_advance": runtime.validate(),
        "rule_results": [
            {
                "name": result.name,
                "passed": result.passed,
                "reason": result.reason,
            }
            for result in runtime.rules.results
        ],
    })



def artifact_health(runtime: CasperRuntime) -> list[dict]:
    checks = []

    for entry in runtime.evidence.all():
        content = entry.content
        if entry.source != "command-exec":
            continue

        stdout_path = Path(content["stdout_path"])
        stderr_path = Path(content["stderr_path"])

        checks.append({
            "evidence_id": entry.evidence_id,
            "sha256": content["sha256"],
            "stdout_exists": stdout_path.exists(),
            "stderr_exists": stderr_path.exists(),
            "valid": stdout_path.exists() and stderr_path.exists(),
        })

    return checks

def cmd_report() -> None:
    runtime = build_runtime()
    session = runtime.initialize()

    try:
        target = runtime.load_target()
        target_payload = {"name": target.name, "scope": target.scope}
    except FileNotFoundError:
        target_payload = None

    runtime.register_rule(successful_probe_rule(runtime.evidence))
    can_advance = runtime.validate()

    print_json({
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
        "artifact_health": artifact_health(runtime),
    })


def cmd_finding_create(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    finding = runtime.create_finding(
        title=args.title,
        severity=args.severity,
        target=args.target,
    )
    print_json({
        "title": finding.title,
        "severity": finding.severity,
        "target": finding.target,
        "status": finding.status,
        "evidence_ids": finding.evidence_ids,
    })


def cmd_finding_list() -> None:
    runtime = build_runtime()
    runtime.initialize()
    print_json(runtime.findings.export())


def cmd_finding_link_evidence(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()
    finding = runtime.link_finding_evidence(args.title, args.evidence_id)
    print_json({
        "title": finding.title,
        "severity": finding.severity,
        "evidence_ids": finding.evidence_ids,
    })


def cmd_workspace_reset() -> None:
    workspace = Path.cwd() / ".casper"

    if not workspace.exists():
        print_json({"reset": False, "reason": "workspace not found"})
        return

    for path in sorted(workspace.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()

    workspace.rmdir()
    print_json({"reset": True, "workspace": str(workspace)})



def cmd_artifact_cat(args: argparse.Namespace) -> None:
    workspace = Path.cwd() / ".casper"
    path = workspace / "artifacts" / f"{args.sha256}.{args.stream}"

    if not path.exists():
        raise SystemExit(f"artifact not found: {path}")

    print(path.read_text(encoding="utf-8"), end="")


def cmd_artifact_verify(args: argparse.Namespace) -> None:
    workspace = Path.cwd() / ".casper"

    stdout_path = workspace / "artifacts" / f"{args.sha256}.stdout"
    stderr_path = workspace / "artifacts" / f"{args.sha256}.stderr"

    payload = {
        "sha256": args.sha256,
        "stdout_exists": stdout_path.exists(),
        "stderr_exists": stderr_path.exists(),
    }

    payload["valid"] = (
        payload["stdout_exists"]
        and payload["stderr_exists"]
    )

    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_tool_httpx(args: argparse.Namespace) -> None:
    runtime = build_runtime()
    runtime.initialize()

    argv = args.argv
    if argv and argv[0] == "--":
        argv = argv[1:]

    command = ["httpx", *argv]

    result = run_command(command)
    exported = export_result(result)
    artifacts = persist_artifacts(result, runtime.workspace)

    evidence_payload = {
        "tool": "httpx",
        "command": exported["command"],
        "exit_code": exported["exit_code"],
        "timestamp": exported["timestamp"],
        "sha256": exported["sha256"],
        "stdout_path": artifacts["stdout_path"],
        "stderr_path": artifacts["stderr_path"],
        "stdout_bytes": len(result.stdout.encode()),
        "stderr_bytes": len(result.stderr.encode()),
    }

    worker = create_worker(
        run_id=getattr(args, "run_id", "unknown"),
        lane="tool-httpx",
    )

    evidence_payload["run_id"] = worker.run_id
    evidence_payload["worker_id"] = worker.worker_id
    evidence_payload["lane"] = worker.lane

    evidence = runtime.record_evidence(
        source="tool-httpx",
        content=evidence_payload,
    )

    evidence_payload["evidence_id"] = evidence.evidence_id

    print_json(evidence_payload)



def cmd_replay_digest() -> None:
    store = EventStore(Path(".casper"))
    digest = replay_digest(store.all())

    print_json({
        "event_count": len(store.all()),
        "digest": digest,
    })



def cmd_replay_project() -> None:
    store = EventStore(Path(".casper"))

    projection = rebuild_session(store.all())

    print_json({
        "event_count": projection.event_count,
        "run_ids": projection.run_ids,
        "evidence_ids": projection.evidence_ids,
    })



def cmd_worker_create(args) -> None:
    worker = create_worker(
        run_id=args.run_id,
        lane=args.lane,
    )

    print_json({
        "worker_id": worker.worker_id,
        "run_id": worker.run_id,
        "lane": worker.lane,
    })



def cmd_worker_start(args) -> None:
    store = EventStore(Path(".casper"))

    worker = create_worker(
        run_id=args.run_id,
        lane=args.lane,
    )

    event = store.append(
        event_type="worker.started",
        payload={
            "worker_id": worker.worker_id,
            "run_id": worker.run_id,
            "lane": worker.lane,
        },
    )

    print_json({
        "event_type": event.event_type,
        "worker_id": worker.worker_id,
        "run_id": worker.run_id,
        "lane": worker.lane,
        "timestamp": event.timestamp,
    })

def main() -> None:

    manifest = build_manifest(sys.argv)
    write_manifest(Path(".casper") / "runs" / manifest.run_id / "manifest.json", manifest)


    parser = argparse.ArgumentParser(prog="casper")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")
    sub.add_parser("report")
    sub.add_parser("validate")

    replay = sub.add_parser("replay")
    worker = sub.add_parser("worker")
    worker_sub = worker.add_subparsers(dest="worker_command")

    worker_create = worker_sub.add_parser("create")
    worker_create.add_argument("--run-id", required=True)
    worker_create.add_argument("--lane", required=True)

    worker_start = worker_sub.add_parser("start")
    worker_start.add_argument("--run-id", required=True)
    worker_start.add_argument("--lane", required=True)
    replay_sub = replay.add_subparsers(dest="replay_command")
    replay_sub.add_parser("digest")
    replay_sub.add_parser("project")

    tool = sub.add_parser("tool")
    tool_sub = tool.add_subparsers(dest="tool_command")
    tool_httpx = tool_sub.add_parser("httpx")
    tool_httpx.add_argument("argv", nargs=argparse.REMAINDER)

    artifact = sub.add_parser("artifact")
    artifact_sub = artifact.add_subparsers(dest="artifact_command")
    artifact_cat = artifact_sub.add_parser("cat")
    artifact_verify = artifact_sub.add_parser("verify")
    artifact_verify.add_argument("--sha256", required=True)
    artifact_cat.add_argument("--sha256", required=True)
    artifact_cat.add_argument("--stream", choices=["stdout", "stderr"], required=True)

    cmd_parser = sub.add_parser("cmd")
    cmd_parser.add_argument("argv", nargs=argparse.REMAINDER)

    workspace = sub.add_parser("workspace")
    workspace_sub = workspace.add_subparsers(dest="workspace_command")
    workspace_sub.add_parser("reset")

    run = sub.add_parser("run")
    run_sub = run.add_subparsers(dest="run_command")
    probe = run_sub.add_parser("probe")
    probe.add_argument("--url", required=True)
    run_sub.add_parser("target")

    target = sub.add_parser("target")
    target_sub = target.add_subparsers(dest="target_command")
    target_set = target_sub.add_parser("set")
    target_set.add_argument("--name", required=True)
    target_set.add_argument("--scope", required=True)
    target_sub.add_parser("show")

    finding = sub.add_parser("finding")
    finding_sub = finding.add_subparsers(dest="finding_command")
    finding_create = finding_sub.add_parser("create")
    finding_create.add_argument("--title", required=True)
    finding_create.add_argument("--severity", required=True)
    finding_create.add_argument("--target")
    finding_sub.add_parser("list")
    finding_link = finding_sub.add_parser("link-evidence")
    finding_link.add_argument("--title", required=True)
    finding_link.add_argument("--evidence-id", required=True)

    evidence = sub.add_parser("evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_command")
    evidence_add = evidence_sub.add_parser("add")
    evidence_add.add_argument("--source", required=True)
    evidence_add.add_argument("--target", required=True)
    evidence_add.add_argument("--status", type=int, required=True)
    evidence_add.add_argument("--observation", required=True)
    evidence_sub.add_parser("list")

    args = parser.parse_args()
    if not hasattr(args, "run_id") or args.run_id is None:
        args.run_id = manifest.run_id

    if args.command in (None, "status"):
        cmd_status()
    elif args.command == "cmd":
        cmd_cmd(args)
    elif args.command == "report":
        cmd_report()
    elif args.command == "validate":
        cmd_validate()
    elif args.command == "replay" and args.replay_command == "digest":
        cmd_replay_digest()
    elif args.command == "replay" and args.replay_command == "project":
        cmd_replay_project()
    elif args.command == "worker" and args.worker_command == "create":
        cmd_worker_create(args)
    elif args.command == "worker" and args.worker_command == "start":
        cmd_worker_start(args)
    elif args.command == "tool" and args.tool_command == "httpx":
        cmd_tool_httpx(args)
    elif args.command == "artifact" and args.artifact_command == "cat":
        cmd_artifact_cat(args)
    elif args.command == "artifact" and args.artifact_command == "verify":
        cmd_artifact_verify(args)
    elif args.command == "workspace" and args.workspace_command == "reset":
        cmd_workspace_reset()
    elif args.command == "run" and args.run_command == "probe":
        cmd_run_probe(args)
    elif args.command == "run" and args.run_command == "target":
        cmd_run_target()
    elif args.command == "target" and args.target_command == "set":
        cmd_target_set(args)
    elif args.command == "target" and args.target_command == "show":
        cmd_target_show()
    elif args.command == "finding" and args.finding_command == "create":
        cmd_finding_create(args)
    elif args.command == "finding" and args.finding_command == "list":
        cmd_finding_list()
    elif args.command == "finding" and args.finding_command == "link-evidence":
        cmd_finding_link_evidence(args)
    elif args.command == "evidence" and args.evidence_command == "add":
        cmd_evidence_add(args)
    elif args.command == "evidence" and args.evidence_command == "list":
        cmd_evidence_list()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
