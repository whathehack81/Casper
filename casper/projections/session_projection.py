from __future__ import annotations

from dataclasses import dataclass, field

from casper.events.store import Event


@dataclass
class SessionProjection:
    evidence_ids: list[str] = field(default_factory=list)
    run_ids: list[str] = field(default_factory=list)
    event_count: int = 0


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

    return projection
