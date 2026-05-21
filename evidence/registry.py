"""
Casper evidence registry.

All execution evidence must be registered,
tracked, reproducible, and timestamped.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    created_at: str
    category: str
    source: str
    data: dict


class EvidenceRegistry:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.evidence_dir = workspace / "evidence"

    def create(
        self,
        category: str,
        source: str,
        data: dict,
    ) -> Evidence:

        timestamp = datetime.utcnow()

        evidence = Evidence(
            evidence_id=timestamp.strftime("%Y%m%d-%H%M%S"),
            created_at=timestamp.isoformat(),
            category=category,
            source=source,
            data=data,
        )

        self._store(evidence)

        return evidence

    def _store(self, evidence: Evidence) -> None:
        output = (
            self.evidence_dir
            / f"{evidence.evidence_id}.json"
        )

        with output.open("w", encoding="utf-8") as handle:
            json.dump(
                asdict(evidence),
                handle,
                indent=4,
                sort_keys=True,
            )
