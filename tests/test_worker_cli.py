from casper.workers.worker import create_worker


def test_worker_cli_identity():
    worker = create_worker(
        run_id="run123",
        lane="recon",
    )

    assert worker.run_id == "run123"
    assert worker.lane == "recon"
    assert len(worker.worker_id) == 16
