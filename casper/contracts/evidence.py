from __future__ import annotations

from typing import Any


VALID_EVIDENCE_TYPES = {
    "manual",
    "http",
    "command",
    "code",
    "patch",
    "metadata",
}

VALID_EVIDENCE_RESULTS = {
    "observed",
    "blocked",
    "confirmed",
    "failed",
}

HTTP_SOURCES = {"http-probe", "manual-check"}
COMMAND_SOURCES = {
    "command-exec",
    "tool-httpx",
    "tool-git-head",
    "tool-git-grep",
    "tool-git-merge-diff",
    "tool-git-changed-files",
}


def infer_evidence_type(source: str, content: dict[str, Any]) -> str:
    explicit = content.get("evidence_type")
    if explicit in VALID_EVIDENCE_TYPES:
        return explicit

    if source == "http-probe":
        return "http"

    if source == "manual-check":
        return "manual"

    if source in COMMAND_SOURCES:
        return "command"

    lowered = source.lower()
    if "patch" in lowered or "diff" in lowered:
        return "patch"
    if "grep" in lowered or "source" in lowered:
        return "code"
    if "repo" in lowered or "meta" in lowered:
        return "metadata"

    return "manual"


def infer_evidence_result(source: str, content: dict[str, Any]) -> str:
    explicit = content.get("result")
    if explicit in VALID_EVIDENCE_RESULTS:
        return explicit

    status = content.get("status")
    ok = content.get("ok")

    if source == "http-probe":
        if ok is True:
            return "confirmed"
        if isinstance(status, int) and 200 <= status < 400:
            return "confirmed"
        return "failed"

    if source == "manual-check" and isinstance(status, int):
        if 200 <= status < 400:
            return "observed"
        return "failed"

    return "observed"


def _normalize_status(raw_status: Any) -> int | None:
    if raw_status is None:
        return None

    try:
        return int(raw_status)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid evidence status: {raw_status}") from exc


def _normalize_command(raw_command: Any) -> list[str] | None:
    if raw_command is None:
        return None

    if not isinstance(raw_command, list) or not all(
        isinstance(item, str) and item
        for item in raw_command
    ):
        raise ValueError("evidence command must be a list of strings")

    return list(raw_command)


def _normalize_proof(raw_proof: Any) -> list[str]:
    if raw_proof is None:
        return []

    if not isinstance(raw_proof, list) or not all(
        isinstance(item, str) and item
        for item in raw_proof
    ):
        raise ValueError("evidence proof must be a list of strings")

    return list(dict.fromkeys(raw_proof))


def normalize_evidence_content(source: str, content: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(content, dict):
        raise ValueError("evidence content must be a dictionary")

    normalized = dict(content)
    normalized["evidence_type"] = infer_evidence_type(source, normalized)
    normalized["result"] = infer_evidence_result(source, normalized)

    status = _normalize_status(normalized.get("status"))
    if status is not None:
        normalized["status"] = status

    command = _normalize_command(normalized.get("command"))
    if command is not None:
        normalized["command"] = command

    proof = _normalize_proof(normalized.get("proof"))
    if proof:
        normalized["proof"] = proof

    metadata = normalized.get("metadata")
    if metadata is None:
        normalized["metadata"] = {}
    elif not isinstance(metadata, dict):
        raise ValueError("evidence metadata must be a dictionary")

    if source in HTTP_SOURCES:
        if source == "http-probe" and "url" not in normalized:
            raise ValueError("http-probe evidence requires url")
        if "status" not in normalized and "ok" not in normalized:
            raise ValueError(f"{source} evidence requires status or ok")

    if source in COMMAND_SOURCES:
        required = {"command", "exit_code", "sha256"}
        missing = sorted(field for field in required if field not in normalized)
        artifact_reference = (
            "sha256" in normalized
            and "stdout_path" in normalized
            and "stderr_path" in normalized
        )
        if missing and not artifact_reference:
            raise ValueError(
                "command evidence missing required fields: "
                + ", ".join(missing)
            )
        if "exit_code" in normalized:
            try:
                normalized["exit_code"] = int(normalized["exit_code"])
            except (TypeError, ValueError) as exc:
                raise ValueError("evidence exit_code must be an integer") from exc

    has_signal = any(
        normalized.get(field)
        for field in (
            "target",
            "url",
            "observation",
            "command",
            "sha256",
            "signal",
            "endpoint",
        )
    )
    if not has_signal:
        raise ValueError(
            "evidence content requires at least one of target, url, observation, command, sha256, signal, or endpoint"
        )

    return normalized
