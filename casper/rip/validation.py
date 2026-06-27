from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from casper.contracts.finding import Finding
from casper.core.runtime import CasperRuntime
from casper.rip.models import ValidationAttempt, ValidationCapsule
from casper.tools.executor import export_result, persist_artifacts, run_command


def _resolve_finding(runtime: CasperRuntime, *, title: str | None = None, finding_id: str | None = None) -> Finding | None:
    if bool(title) and bool(finding_id):
        raise ValueError("provide only one finding selector")
    for finding in runtime.findings.all():
        if finding_id is not None and finding.finding_id == finding_id:
            return finding
        if title is not None and finding.title == title:
            return finding
    if title is not None or finding_id is not None:
        raise ValueError("finding not found")
    return None


def _missing_markers(stream: str, markers: list[str], stream_name: str) -> list[str]:
    return [f"missing {stream_name} marker: {marker}" for marker in markers if marker not in stream]


def _assess(exit_code: int, stdout: str, stderr: str, expect_exit_code: int, expect_stdout: list[str], expect_stderr: list[str]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if exit_code != expect_exit_code:
        reasons.append(f"exit_code {exit_code} != expected {expect_exit_code}")
    reasons.extend(_missing_markers(stdout, expect_stdout, "stdout"))
    reasons.extend(_missing_markers(stderr, expect_stderr, "stderr"))
    return len(reasons) == 0, reasons


def _status(passed: int, required: int) -> str:
    if passed >= required:
        return "VERIFIED"
    if passed > 0:
        return "FLAKY"
    return "FAILED"


def _capsule_id(payload: dict[str, Any]) -> str:
    stable = {
        "finding_id": payload.get("finding_id"),
        "title": payload.get("title"),
        "target": payload.get("target"),
        "argv": payload.get("argv"),
        "expectations": payload.get("expectations"),
        "attempts": [item["evidence_id"] for item in payload.get("attempts", [])],
    }
    return sha256(json.dumps(stable, sort_keys=True).encode()).hexdigest()[:24]


def _write(workspace: Path, validation_id: str, payload: dict[str, Any]) -> Path:
    out_dir = workspace / "rip"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{validation_id}.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return out


def run_validation(
    runtime: CasperRuntime,
    *,
    argv: list[str],
    title: str | None = None,
    finding_id: str | None = None,
    target: str | None = None,
    validator: str = "rip",
    repetitions: int = 3,
    required_passes: int | None = None,
    expect_exit_code: int = 0,
    expect_stdout: list[str] | None = None,
    expect_stderr: list[str] | None = None,
    timeout: int = 60,
    run_id: str = "unknown",
) -> ValidationCapsule:
    if not argv:
        raise ValueError("argv is required")
    if repetitions < 1:
        raise ValueError("repetitions must be >= 1")
    required = repetitions if required_passes is None else required_passes
    if required < 1 or required > repetitions:
        raise ValueError("required_passes must be between 1 and repetitions")

    expect_stdout = list(expect_stdout or [])
    expect_stderr = list(expect_stderr or [])
    finding = _resolve_finding(runtime, title=title, finding_id=finding_id)
    resolved_target = target or (finding.target if finding is not None else None)
    attempts: list[ValidationAttempt] = []

    for index in range(1, repetitions + 1):
        result = run_command(argv, timeout=timeout)
        exported = export_result(result)
        artifacts = persist_artifacts(result, runtime.workspace)
        ok, reasons = _assess(result.exit_code, result.stdout, result.stderr, expect_exit_code, expect_stdout, expect_stderr)
        evidence_payload = {
            "tool": "rip",
            "command": exported["command"],
            "exit_code": exported["exit_code"],
            "timestamp": exported["timestamp"],
            "sha256": exported["sha256"],
            "stdout_path": artifacts["stdout_path"],
            "stderr_path": artifacts["stderr_path"],
            "stdout_bytes": len(result.stdout.encode()),
            "stderr_bytes": len(result.stderr.encode()),
            "run_id": run_id,
            "lane": "rip-validation",
            "attempt": index,
            "validator": validator,
            "target": resolved_target,
            "finding_id": finding.finding_id if finding is not None else finding_id,
            "signal": "rip-attempt-pass" if ok else "rip-attempt-fail",
            "result": "confirmed" if ok else "failed",
            "evidence_type": "command",
            "metadata": {"passed": ok, "reasons": reasons},
        }
        evidence = runtime.record_evidence(source="rip-attempt", content=evidence_payload)
        attempts.append(ValidationAttempt(index, evidence.evidence_id, exported["exit_code"], exported["sha256"], artifacts["stdout_path"], artifacts["stderr_path"], ok, reasons))

    passed_attempts = sum(1 for item in attempts if item.passed)
    failed_attempts = len(attempts) - passed_attempts
    status = _status(passed_attempts, required)
    timestamp = datetime.now(UTC).isoformat()
    provisional = {
        "validator": validator,
        "status": status,
        "finding_id": finding.finding_id if finding is not None else finding_id,
        "title": finding.title if finding is not None else title,
        "target": resolved_target,
        "argv": argv,
        "repetitions": repetitions,
        "required_passes": required,
        "passed_attempts": passed_attempts,
        "failed_attempts": failed_attempts,
        "expectations": {"exit_code": expect_exit_code, "stdout_contains": expect_stdout, "stderr_contains": expect_stderr},
        "attempts": [asdict(item) for item in attempts],
        "timestamp": timestamp,
    }
    validation_id = _capsule_id(provisional)
    capsule_path = _write(runtime.workspace, validation_id, {"validation_id": validation_id, **provisional})
    capsule_evidence = runtime.record_evidence(
        source="rip-validation",
        content={
            "target": resolved_target or provisional.get("title") or validation_id,
            "observation": f"RIP {status}: {passed_attempts}/{repetitions} attempts passed",
            "signal": status,
            "evidence_type": "metadata",
            "result": "confirmed" if status == "VERIFIED" else "failed",
            "proof": [item.evidence_id for item in attempts],
            "metadata": {"validation_id": validation_id, "capsule_path": str(capsule_path), "validator": validator},
        },
    )
    final = {"validation_id": validation_id, **provisional, "evidence_id": capsule_evidence.evidence_id, "capsule_path": str(capsule_path)}
    _write(runtime.workspace, validation_id, final)

    if finding is not None:
        runtime.link_finding_evidence(finding_id=finding.finding_id, evidence_id=capsule_evidence.evidence_id)
        runtime.review_finding(
            finding_id=finding.finding_id,
            validation_state="confirmed" if status == "VERIFIED" else "incomplete",
            confirmation_status="confirmed" if status == "VERIFIED" else "needs-proof",
            confidence=1.0 if status == "VERIFIED" else 0.0,
        )

    return ValidationCapsule(command=argv, **final)


def list_capsules(workspace: Path) -> list[dict[str, Any]]:
    out_dir = workspace / "rip"
    if not out_dir.exists():
        return []
    rows = []
    for path in sorted(out_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.append({
            "validation_id": data.get("validation_id"),
            "status": data.get("status"),
            "finding_id": data.get("finding_id"),
            "title": data.get("title"),
            "passed_attempts": data.get("passed_attempts"),
            "required_passes": data.get("required_passes"),
            "capsule_path": str(path),
        })
    return rows


def load_capsule(workspace: Path, validation_id: str) -> dict[str, Any]:
    path = workspace / "rip" / f"{validation_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"RIP capsule not found: {validation_id}")
    return json.loads(path.read_text(encoding="utf-8"))
