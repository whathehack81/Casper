from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import hashlib
import json

from casper.contracts.finding import Finding


class FindingStore:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self._findings: list[Finding] = []

    def _build_finding_id(
        self,
        title: str,
        severity: str,
        target: str | None,
    ) -> str:
        seed = f"{title}\0{severity}\0{target or ''}"
        existing = {
            finding.finding_id
            for finding in self._findings
            if finding.finding_id is not None
        }

        candidate = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

        if candidate not in existing:
            return candidate

        counter = 2
        while True:
            candidate = hashlib.sha256(
                f"{seed}\0{counter}".encode("utf-8")
            ).hexdigest()[:16]

            if candidate not in existing:
                return candidate

            counter += 1

    def _find(
        self,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding | None:
        for finding in self._findings:
            if finding_id is not None and finding.finding_id == finding_id:
                return finding

            if title is not None and finding.title == title:
                return finding

        return None

    def create(
        self,
        title: str,
        severity: str,
        target: str | None = None,
    ) -> Finding:
        finding = Finding(
            title=title,
            finding_id=self._build_finding_id(
                title=title,
                severity=severity,
                target=target,
            ),
            severity=severity,
            target=target,
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

        changed = False

        for finding in self._findings:
            if finding.finding_id is None:
                finding.finding_id = self._build_finding_id(
                    title=finding.title,
                    severity=finding.severity,
                    target=finding.target,
                )
                changed = True

        if changed:
            self._persist()

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

    def set_status(
        self,
        status: str,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding:
        finding = self._find(title=title, finding_id=finding_id)

        if finding is None:
            raise ValueError("finding not found")

        finding.status = status
        self._persist()
        return finding

    def link_evidence(
        self,
        evidence_id: str,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding:
        finding = self._find(title=title, finding_id=finding_id)

        if finding is None:
            raise ValueError("finding not found")

        finding.link_evidence(evidence_id)
        self._persist()
        return finding
