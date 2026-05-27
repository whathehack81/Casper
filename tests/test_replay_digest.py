from casper.events.store import Event
from casper.replay.replay import replay_digest


def test_replay_digest_stable():
    events = [
        Event(
            timestamp="2026-01-01T00:00:00+00:00",
            event_type="evidence.recorded",
            payload={
                "evidence_id": "abc123",
            },
        ),
    ]

    a = replay_digest(events)
    b = replay_digest(events)

    assert a == b


def test_replay_digest_changes():
    events_a = [
        Event(
            timestamp="2026-01-01T00:00:00+00:00",
            event_type="evidence.recorded",
            payload={
                "evidence_id": "abc123",
            },
        ),
    ]

    events_b = [
        Event(
            timestamp="2026-01-01T00:00:01+00:00",
            event_type="evidence.recorded",
            payload={
                "evidence_id": "abc123",
            },
        ),
    ]

    assert replay_digest(events_a) != replay_digest(events_b)
