from __future__ import annotations

from typing import Any

from casper.evidence.registry import EvidenceRegistry
from casper.rules.engine import Rule


HTTP_EVIDENCE_SOURCES = {"http-probe", "manual-check"}
CODE_REVIEW_SOURCE_HINTS = {
    "repo",
    "source",
    "grep",
    "patch",
    "diff",
    "metadata",
    "command",
}


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


def _is_code_review_evidence(entry: Any) -> bool:
    source = str(getattr(entry, "source", "")).lower()
    content = getattr(entry, "content", {})

    if any(hint in source for hint in CODE_REVIEW_SOURCE_HINTS):
        return True

    if isinstance(content, dict):
        command = " ".join(str(part) for part in content.get("command", []))
        target = str(content.get("target", ""))
        observation = str(content.get("observation", ""))
        haystack = f"{command} {target} {observation}".lower()

        return any(
            token in haystack
            for token in (
                "git ",
                "grep",
                "diff",
                "patch",
                "src/",
                ".cpp",
                ".py",
                "repo_head",
                "commit",
            )
        )

    return False


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


def code_review_rule(registry: EvidenceRegistry, findings: Any) -> Rule:
    def check() -> bool:
        ready_findings = [
            finding
            for finding in findings.all()
            if finding.status == "ready" and len(finding.evidence_ids) >= 3
        ]

        if not ready_findings:
            return False

        return any(_is_code_review_evidence(entry) for entry in registry.all())

    return Rule(
        name="code review evidence profile satisfied",
        check=check,
        pass_reason="ready finding has linked code-review evidence",
        fail_reason="missing ready finding with linked code-review evidence",
    )
