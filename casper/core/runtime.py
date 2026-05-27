"""
Casper runtime controller.

Coordinates:
- session state
- rule evaluation
- evidence registration
- execution advancement
"""

from pathlib import Path

from casper.rules.engine import RuleEngine
from casper.evidence.registry import EvidenceRegistry
from casper.state.session import SessionStore


class CasperRuntime:
    def __init__(self, workspace: Path):
        self.workspace = workspace

        self.rules = RuleEngine()
        self.evidence = EvidenceRegistry(workspace)
        self.sessions = SessionStore(workspace)

        self.session = None

    def initialize(self) -> None:
        self.session = self.sessions.create()

        print(f"[+] Runtime session: {self.session.session_id}")

    def register_rule(self, rule) -> None:
        self.rules.register(rule)

    def validate(self) -> bool:
        results = self.rules.evaluate()

        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {result.name} :: {result.reason}")

        return self.rules.can_advance()

    def record_evidence(
        self,
        category: str,
        source: str,
        data: dict,
    ) -> None:

        evidence = self.evidence.create(
            category=category,
            source=source,
            data=data,
        )

        print(f"[+] Evidence registered: {evidence.evidence_id}")
