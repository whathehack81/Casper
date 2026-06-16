from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AdvancementRules:
    required_evidence: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evidence_kinds(self, finding: Any) -> set[str]:
        evidence = getattr(finding, "evidence", [])
        kinds: set[str] = set()

        for item in evidence:
            if not isinstance(item, dict):
                continue

            kind = item.get("kind")
            if isinstance(kind, str):
                kinds.add(kind)

        return kinds

    def missing_requirements(self, finding: Any) -> List[str]:
        kinds = self.evidence_kinds(finding)
        return [
            required
            for required in self.required_evidence
            if required not in kinds
        ]

    def allows(self, finding: Any) -> bool:
        return not self.missing_requirements(finding)
