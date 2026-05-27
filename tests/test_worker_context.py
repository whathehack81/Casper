from casper.workers.worker import create_worker


def test_worker_identity_stable():
    a = create_worker(
        run_id="run123",
        lane="recon",
    )

    b = create_worker(
        run_id="run123",
        lane="recon",
    )

    c = create_worker(
        run_id="run123",
        lane="idor",
    )

    assert a.worker_id == b.worker_id
    assert a.worker_id != c.worker_id
