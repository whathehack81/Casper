from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    title: str
    finding_id: str | None = None
    severity: str = "informational"
    target: Optional[str] = None
    status: str = "new"
    notes: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)

    def add_evidence(self, kind: str, value: Any, note: Optional[str] = None) -> None:
        item = {"kind": kind, "value": value}
        if note:
            item["note"] = note
        self.evidence.append(item)

    def link_evidence(self, evidence_id: str) -> None:
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)
