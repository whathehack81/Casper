from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    timestamp: str
    source: str
    content: dict


class EvidenceRegistry:
    def __init__(self) -> None:
        self._entries: list[Evidence] = []

    def add(self, source: str, content: dict) -> Evidence:
        timestamp = datetime.now(UTC).isoformat()

        payload = {
            "timestamp": timestamp,
            "source": source,
            "content": content,
        }

        digest = sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        evidence = Evidence(
            evidence_id=digest,
            timestamp=timestamp,
            source=source,
            content=content,
        )

        self._entries.append(evidence)

        return evidence

    def all(self) -> list[Evidence]:
        return list(self._entries)

    def export(self) -> list[dict]:
        return [asdict(entry) for entry in self._entries]
