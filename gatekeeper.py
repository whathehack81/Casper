from __future__ import annotations

from casper.contracts.finding import Finding
from casper.contracts.rules import AdvancementRules


class Gatekeeper:
    def __init__(self, rules: AdvancementRules | None = None) -> None:
        self.rules = rules or AdvancementRules()

    def evaluate(
        self,
        finding: Finding,
        evidence_items: list[dict] | None = None,
    ) -> Finding:
        missing = self.rules.advancement_gaps(
            finding,
            evidence_items=evidence_items,
        )
        finding.missing_evidence = list(missing)

        if finding.false_positive_reason:
            finding.status = "blocked"
            finding.validation_state = "false_positive"
            finding.confirmation_status = "rejected"
            finding.notes.append(f"false_positive:{finding.false_positive_reason}")
            return finding

        if missing:
            finding.status = "blocked"
            if all(
                not item.startswith("confidence>=") and item != "confirmation"
                for item in missing
            ):
                finding.notes.append("missing:" + ",".join(missing))
            else:
                finding.notes.append("blocked:" + ",".join(missing))
            return finding

        finding.status = "ready"
        finding.notes.append("advance:requirements_satisfied")
        return finding
