from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Finding:
    title: str
    severity: str = "informational"
    target: Optional[str] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_evidence(self, kind: str, value: Any, note: Optional[str] = None) -> None:
        item = {"kind": kind, "value": value}
        if note:
            item["note"] = note
        self.evidence.append(item)
