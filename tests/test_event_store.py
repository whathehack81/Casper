from casper.events.store import EventStore


def test_event_append(tmp_path):
    store = EventStore(tmp_path)

    event = store.append(
        event_type="tool.executed",
        payload={"tool": "httpx"},
    )

    assert event.event_type == "tool.executed"

    events = store.all()

    assert len(events) == 1
    assert events[0].payload["tool"] == "httpx"
