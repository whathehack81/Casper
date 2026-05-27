from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
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
