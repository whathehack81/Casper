from __future__ import annotations

from casper.evidence.registry import EvidenceRegistry
from casper.rules.engine import Rule


def successful_probe_rule(registry: EvidenceRegistry) -> Rule:
    return Rule(
        name="successful probe evidence exists",
        check=lambda: any(
            entry.source == "http-probe"
            and entry.content.get("ok") is True
            for entry in registry.all()
        ),
        pass_reason="successful probe evidence exists",
        fail_reason="missing successful probe evidence",
    )
