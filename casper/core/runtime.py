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
from casper.rules.engine import RuleEngine
from casper.state.session import SessionState, SessionStore
from casper.state.target import TargetState, TargetStore


class CasperRuntime:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.rules = RuleEngine()
        self.evidence = EvidenceRegistry(workspace)
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
        return self.evidence.add(source=source, content=content)


    def create_finding(
        self,
        title: str,
        severity: str,
    ) -> Finding:
        return self.findings.create(title=title, severity=severity)


    def link_finding_evidence(
        self,
        title: str,
        evidence_id: str,
    ) -> Finding:
        return self.findings.link_evidence(
            title=title,
            evidence_id=evidence_id,
        )


    def set_target(
        self,
        name: str,
        scope: str,
    ) -> TargetState:
        return self.targets.set(name=name, scope=scope)

    def load_target(self) -> TargetState:
        return self.targets.load()
