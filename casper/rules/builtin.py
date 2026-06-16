from __future__ import annotations

from typing import Any

from casper.evidence.registry import EvidenceRegistry
from casper.rules.engine import Rule


HTTP_EVIDENCE_SOURCES = {"http-probe", "manual-check"}


def _status_is_successful(content: dict[str, Any]) -> bool:
    raw_status = content.get("status")

    if raw_status is None:
        return False

    try:
        status = int(raw_status)
    except (TypeError, ValueError):
        return False

    return 200 <= status < 400


def _is_successful_http_evidence(entry: Any) -> bool:
    source = getattr(entry, "source", None)
    content = getattr(entry, "content", None)

    if source not in HTTP_EVIDENCE_SOURCES:
        return False

    if not isinstance(content, dict):
        return False

    return content.get("ok") is True or _status_is_successful(content)


def successful_probe_rule(registry: EvidenceRegistry) -> Rule:
    return Rule(
        name="successful probe evidence exists",
        check=lambda: any(
            _is_successful_http_evidence(entry)
            for entry in registry.all()
        ),
        pass_reason="successful probe evidence exists",
        fail_reason="missing successful probe evidence",
    )
