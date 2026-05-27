from casper.events.store import EventStore
from casper.projections.session_projection import rebuild_session


def test_projection_rebuild(tmp_path):
    store = EventStore(tmp_path)

    store.append(
        event_type="evidence.recorded",
        payload={
            "evidence_id": "abc123",
            "run_id": "run001",
        },
    )

    projection = rebuild_session(store.all())

    assert projection.event_count == 1
    assert projection.run_ids == ["run001"]
