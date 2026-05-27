from casper.events.store import Event
from casper.projections.session_projection import rebuild_session


def test_rebuild_session():
    events = [
        Event(
            timestamp="2026-01-01T00:00:00+00:00",
            event_type="evidence.recorded",
            payload={
                "evidence_id": "abc123",
                "run_id": "run001",
            },
        ),
        Event(
            timestamp="2026-01-01T00:01:00+00:00",
            event_type="evidence.recorded",
            payload={
                "evidence_id": "def456",
                "run_id": "run001",
            },
        ),
    ]

    projection = rebuild_session(events)

    assert projection.event_count == 2
    assert len(projection.evidence_ids) == 2
    assert projection.run_ids == ["run001"]
