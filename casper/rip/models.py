from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationAttempt:
    attempt: int
    evidence_id: str
    exit_code: int
    sha256: str
    stdout_path: str
    stderr_path: str
    passed: bool
    reasons: list[str]


@dataclass(frozen=True)
class ValidationCapsule:
    validation_id: str
    validator: str
    status: str
    finding_id: str | None
    title: str | None
    target: str | None
    repetitions: int
    required_passes: int
    passed_attempts: int
    failed_attempts: int
    expectations: dict[str, Any]
    attempts: list[dict[str, Any]]
    evidence_id: str
    capsule_path: str
    timestamp: str
