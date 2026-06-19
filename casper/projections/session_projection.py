from __future__ import annotations

from dataclasses import dataclass, field

from casper.events.store import Event


@dataclass
class SessionProjection:
    evidence_ids: list[str] = field(default_factory=list)
    run_ids: list[str] = field(default_factory=list)
    event_count: int = 0
    validation_modes: list[str] = field(default_factory=list)
    advanceable_findings: list[str] = field(default_factory=list)
    can_advance: bool = False


def rebuild_session(events: list[Event]) -> SessionProjection:
    projection = SessionProjection()

    for event in events:
        projection.event_count += 1

        if event.event_type == "evidence.recorded":
            evidence_id = event.payload.get("evidence_id")
            run_id = event.payload.get("run_id")

            if evidence_id:
                projection.evidence_ids.append(evidence_id)

            if run_id and run_id not in projection.run_ids:
                projection.run_ids.append(run_id)

        if event.event_type == "validation.evaluated":
            mode = event.payload.get("mode")
            if mode and mode not in projection.validation_modes:
                projection.validation_modes.append(mode)

            if event.payload.get("can_advance") is True:
                projection.can_advance = True

            for finding in event.payload.get("findings", []):
                if not isinstance(finding, dict):
                    continue
                if finding.get("can_advance") is not True:
                    continue
                finding_id = finding.get("finding_id")
                if finding_id and finding_id not in projection.advanceable_findings:
                    projection.advanceable_findings.append(finding_id)
    return projection
