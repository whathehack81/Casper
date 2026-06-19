from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
import json

from casper.contracts.evidence import normalize_evidence_content


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    timestamp: str
    source: str
    content: dict


class EvidenceRegistry:
    def __init__(self, workspace: Path | None = None) -> None:
        self.workspace = workspace
        self._entries: list[Evidence] = []

    def add(self, source: str, content: dict) -> Evidence:
        timestamp = datetime.now(UTC).isoformat()
        normalized_content = normalize_evidence_content(source, content)

        payload = {
            "timestamp": timestamp,
            "source": source,
            "content": normalized_content,
        }

        digest = sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        content = dict(normalized_content)
        content["evidence_id"] = digest

        evidence = Evidence(
            evidence_id=digest,
            timestamp=timestamp,
            source=source,
            content=content,
        )

        self._entries.append(evidence)
        self._persist()

        return evidence

    def all(self) -> list[Evidence]:
        return list(self._entries)

    def exists(self, evidence_id: str) -> bool:
        return any(
            entry.evidence_id == evidence_id
            for entry in self._entries
        )

    def export(self) -> list[dict]:
        return [asdict(entry) for entry in self._entries]

    def _persist(self) -> None:
        if self.workspace is None:
            return

        evidence_dir = self.workspace / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        output = evidence_dir / "index.json"
        with output.open("w", encoding="utf-8") as handle:
            json.dump(self.export(), handle, indent=4, sort_keys=True)

    def load(self) -> list[Evidence]:
        if self.workspace is None:
            return []

        input_path = self.workspace / "evidence" / "index.json"

        with input_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        self._entries = [Evidence(**entry) for entry in data]
        return self.all()
