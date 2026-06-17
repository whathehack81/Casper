"""
Casper runtime controller.

Coordinates:
- session state
- rule evaluation
- evidence registration
- execution advancement
"""

from pathlib import Path
from typing import Any

from casper.contracts.finding import Finding
from casper.contracts.finding_store import FindingStore
from casper.evidence.registry import Evidence, EvidenceRegistry
from casper.events.store import EventStore
from casper.rules.engine import RuleEngine
from casper.state.session import SessionState, SessionStore
from casper.state.target import TargetState, TargetStore


class CasperRuntime:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.rules = RuleEngine()
        self.evidence = EvidenceRegistry(workspace)
        self.events = EventStore(workspace)
        self.sessions = SessionStore(workspace)
        self.findings = FindingStore(workspace)
        self.targets = TargetStore(workspace)

        self.session: SessionState | None = None

    def initialize(self) -> SessionState:
        try:
            self.session = self.sessions.load()
        except FileNotFoundError:
            self.session = self.sessions.create()

        try:
            self.evidence.load()
        except FileNotFoundError:
            pass

        try:
            self.findings.load()
        except FileNotFoundError:
            pass

        return self.session

    def register_rule(self, rule: Any) -> None:
        self.rules.register(rule)

    def validate(self) -> bool:
        return self.rules.can_advance()

    def record_evidence(
        self,
        source: str,
        content: dict,
    ) -> Evidence:
        evidence = self.evidence.add(source=source, content=content)

        self.events.append(
            event_type="evidence.recorded",
            payload={
                "evidence_id": evidence.evidence_id,
                "source": source,
                "run_id": content.get("run_id"),
                "worker_id": content.get("worker_id"),
                "lane": content.get("lane"),
            },
        )

        return evidence


    def create_finding(
        self,
        title: str,
        severity: str,
        target: str | None = None,
    ) -> Finding:
        return self.findings.create(
            title=title,
            severity=severity,
            target=target,
        )


    def link_finding_evidence(
        self,
        evidence_id: str,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding:
        if not self.evidence.exists(evidence_id):
            raise ValueError(f"evidence not found: {evidence_id}")

        return self.findings.link_evidence(
            title=title,
            finding_id=finding_id,
            evidence_id=evidence_id,
        )

    def set_finding_status(
        self,
        status: str,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding:
        allowed_statuses = {"new", "blocked", "ready", "submitted"}

        if status not in allowed_statuses:
            allowed = ", ".join(sorted(allowed_statuses))
            raise ValueError(f"invalid status: {status}; expected one of: {allowed}")

        return self.findings.set_status(
            title=title,
            finding_id=finding_id,
            status=status,
        )

    def export_findings(self) -> list[dict]:
        evidence_by_id = {
            entry.evidence_id: {
                "evidence_id": entry.evidence_id,
                "timestamp": entry.timestamp,
                "source": entry.source,
                "content": entry.content,
            }
            for entry in self.evidence.all()
        }

        hydrated = []

        for finding in self.findings.export():
            evidence_ids = finding.get("evidence_ids", [])
            finding["evidence"] = [
                evidence_by_id[evidence_id]
                for evidence_id in evidence_ids
                if evidence_id in evidence_by_id
            ]
            hydrated.append(finding)

        return hydrated


    def set_target(
        self,
        name: str,
        scope: str,
        mode: str = "web",
    ) -> TargetState:
        return self.targets.set(name=name, scope=scope, mode=mode)

    def load_target(self) -> TargetState:
        return self.targets.load()
