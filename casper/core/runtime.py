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

from casper.evidence.registry import Evidence, EvidenceRegistry
from casper.rules.engine import RuleEngine
from casper.state.session import SessionState, SessionStore


class CasperRuntime:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.rules = RuleEngine()
        self.evidence = EvidenceRegistry(workspace)
        self.sessions = SessionStore(workspace)

        self.session: SessionState | None = None

    def initialize(self) -> SessionState:
        try:
            self.session = self.sessions.load()
        except FileNotFoundError:
            self.session = self.sessions.create()

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
