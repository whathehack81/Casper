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
from casper.reasoning.engine import ReasoningDecision, analyze_finding, get_profile
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
        self.validation_mode: str = "web"
        self.validation_profile: str = get_profile("web").name
        self.last_assessments: list[ReasoningDecision] = []

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
        can_advance = self.rules.can_advance()
        self.events.append(
            event_type="validation.evaluated",
            payload={
                "mode": self.validation_mode,
                "profile": self.validation_profile,
                "can_advance": can_advance,
                "findings": [
                    {
                        "finding_id": decision.finding_id,
                        "validation_state": decision.validation_state,
                        "confirmation_status": decision.confirmation_status,
                        "can_advance": decision.can_advance,
                    }
                    for decision in self.last_assessments
                ],
            },
        )
        return can_advance

    def configure_validation(self, mode: str) -> str:
        profile = get_profile(mode)
        self.validation_mode = profile.mode
        self.validation_profile = profile.name
        return profile.name

    def assess_findings(self, mode: str | None = None) -> list[ReasoningDecision]:
        profile = get_profile(mode or self.validation_mode)
        self.validation_mode = profile.mode
        self.validation_profile = profile.name

        evidence_by_id = {
            entry.evidence_id: entry
            for entry in self.evidence.all()
        }
        assessments = [
            analyze_finding(
                finding,
                [
                    evidence_by_id[evidence_id]
                    for evidence_id in finding.evidence_ids
                    if evidence_id in evidence_by_id
                ],
                profile.mode,
            )
            for finding in self.findings.all()
        ]
        self.last_assessments = assessments
        return list(self.last_assessments)

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
        finding = self.findings.create(
            title=title,
            severity=severity,
            target=target,
        )
        self.events.append(
            event_type="finding.created",
            payload={
                "finding_id": finding.finding_id,
                "title": finding.title,
                "severity": finding.severity,
                "target": finding.target,
            },
        )
        return finding


    def link_finding_evidence(
        self,
        evidence_id: str,
        title: str | None = None,
        finding_id: str | None = None,
    ) -> Finding:
        if not self.evidence.exists(evidence_id):
            raise ValueError(f"evidence not found: {evidence_id}")

        finding = self.findings.link_evidence(
            title=title,
            finding_id=finding_id,
            evidence_id=evidence_id,
        )
        self.events.append(
            event_type="finding.evidence_linked",
            payload={
                "finding_id": finding.finding_id,
                "evidence_id": evidence_id,
            },
        )
        return finding

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

        finding = self.findings.set_status(
            title=title,
            finding_id=finding_id,
            status=status,
        )
        self.events.append(
            event_type="finding.status_changed",
            payload={
                "finding_id": finding.finding_id,
                "status": finding.status,
            },
        )
        return finding

    def review_finding(
        self,
        *,
        title: str | None = None,
        finding_id: str | None = None,
        validation_state: str | None = None,
        confirmation_status: str | None = None,
        confidence: float | None = None,
        false_positive_reason: str | None = None,
    ) -> Finding:
        finding = self.findings.update_validation(
            title=title,
            finding_id=finding_id,
            validation_state=validation_state,
            confirmation_status=confirmation_status,
            confidence=confidence,
            false_positive_reason=false_positive_reason,
        )
        self.events.append(
            event_type="finding.reviewed",
            payload={
                "finding_id": finding.finding_id,
                "validation_state": finding.validation_state,
                "confirmation_status": finding.confirmation_status,
                "confidence": finding.confidence,
                "false_positive_reason": finding.false_positive_reason,
            },
        )
        return finding

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
