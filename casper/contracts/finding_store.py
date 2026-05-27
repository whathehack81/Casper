from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from casper.contracts.finding import Finding


class FindingStore:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._findings: list[Finding] = []

    def create(
        self,
        title: str,
        severity: str,
    ) -> Finding:

        finding = Finding(
            title=title,
            severity=severity,
        )

        self._findings.append(finding)
        self._persist()

        return finding

    def all(self) -> list[Finding]:
        return list(self._findings)

    def export(self) -> list[dict]:
        return [asdict(finding) for finding in self._findings]

    def load(self) -> list[Finding]:
        path = self.workspace / "findings" / "index.json"

        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        self._findings = [Finding(**entry) for entry in data]

        return self.all()

    def _persist(self) -> None:
        findings_dir = self.workspace / "findings"
        findings_dir.mkdir(parents=True, exist_ok=True)

        output = findings_dir / "index.json"

        with output.open("w", encoding="utf-8") as handle:
            json.dump(
                self.export(),
                handle,
                indent=2,
                sort_keys=True,
            )

    def link_evidence(
        self,
        title: str,
        evidence_id: str,
    ) -> Finding:
        for finding in self._findings:
            if finding.title == title:
                finding.link_evidence(evidence_id)
                self._persist()
                return finding

        raise ValueError(f"finding not found: {title}")
