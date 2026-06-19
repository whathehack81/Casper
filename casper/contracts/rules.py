from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AdvancementRules:
    required_evidence: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    require_confirmation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def evidence_kinds(
        self,
        finding: Any,
        evidence_items: List[Dict[str, Any]] | None = None,
    ) -> set[str]:
        evidence = evidence_items if evidence_items is not None else getattr(finding, "evidence", [])
        kinds: set[str] = set()

        for item in evidence:
            if not isinstance(item, dict):
                continue

            kind = item.get("kind")
            if isinstance(kind, str):
                kinds.add(kind)

        return kinds

    def missing_requirements(
        self,
        finding: Any,
        evidence_items: List[Dict[str, Any]] | None = None,
    ) -> List[str]:
        kinds = self.evidence_kinds(finding, evidence_items=evidence_items)
        return [
            required
            for required in self.required_evidence
            if required not in kinds
        ]

    def advancement_gaps(
        self,
        finding: Any,
        evidence_items: List[Dict[str, Any]] | None = None,
    ) -> List[str]:
        gaps = self.missing_requirements(finding, evidence_items=evidence_items)

        try:
            confidence = float(getattr(finding, "confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0

        if confidence < self.min_confidence:
            gaps.append(f"confidence>={self.min_confidence:.2f}")

        if self.require_confirmation:
            confirmation_status = getattr(finding, "confirmation_status", "unconfirmed")
            if confirmation_status != "confirmed":
                gaps.append("confirmation")

        return gaps

    def allows(
        self,
        finding: Any,
        evidence_items: List[Dict[str, Any]] | None = None,
    ) -> bool:
        return not self.advancement_gaps(finding, evidence_items=evidence_items)
