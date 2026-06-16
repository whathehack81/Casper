from __future__ import annotations

from casper.contracts.finding import Finding
from casper.contracts.rules import AdvancementRules


class Gatekeeper:
    def __init__(self, rules: AdvancementRules | None = None) -> None:
        self.rules = rules or AdvancementRules()

    def evaluate(self, finding: Finding) -> Finding:
        missing = self.rules.missing_requirements(finding)

        if missing:
            finding.status = "blocked"
            finding.notes.append("missing:" + ",".join(missing))
            return finding

        finding.status = "ready"
        finding.notes.append("advance:requirements_satisfied")
        return finding
