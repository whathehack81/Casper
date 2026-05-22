from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AdvancementRules:
    required_evidence: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def allows(self, finding: Any) -> bool:
        if not self.required_evidence:
            return True

        evidence = getattr(finding, "evidence", [])
        kinds = {item.get("kind") for item in evidence if isinstance(item, dict)}
        return all(kind in kinds for kind in self.required_evidence)
