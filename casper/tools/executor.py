from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import json
import subprocess


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str
    timestamp: str
    sha256: str


def run_command(command: list[str], timeout: int = 60) -> CommandResult:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

    timestamp = datetime.now(UTC).isoformat()

    payload = {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timestamp": timestamp,
    }

    digest = sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        timestamp=timestamp,
        sha256=digest,
    )


def export_result(result: CommandResult) -> dict:
    return asdict(result)


def persist_artifacts(result: CommandResult, workspace: Path) -> dict:
    artifact_dir = workspace / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    stdout_path = artifact_dir / f"{result.sha256}.stdout"
    stderr_path = artifact_dir / f"{result.sha256}.stderr"

    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")

    return {
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
