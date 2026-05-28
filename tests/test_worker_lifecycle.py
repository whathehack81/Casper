from casper.events.store import EventStore
from casper.workers.worker import create_worker


def test_worker_lifecycle_event_payload(tmp_path):
    store = EventStore(tmp_path)
    worker = create_worker(run_id="run123", lane="recon")

    event = store.append(
        event_type="worker.started",
        payload={
            "worker_id": worker.worker_id,
            "run_id": worker.run_id,
            "lane": worker.lane,
        },
    )

    assert event.event_type == "worker.started"
    assert event.payload["worker_id"] == worker.worker_id
