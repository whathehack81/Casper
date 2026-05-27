from casper.events.store import EventStore
from casper.replay.replay import replay_digest


def test_replay_digest_generation(tmp_path):
    store = EventStore(tmp_path)

    store.append(
        event_type="evidence.recorded",
        payload={
            "evidence_id": "abc123",
            "run_id": "run001",
        },
    )

    digest = replay_digest(store.all())

    assert len(digest) == 64
