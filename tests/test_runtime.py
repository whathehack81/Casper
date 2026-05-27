from casper.core.runtime import CasperRuntime


def test_runtime_initializes_session(tmp_path):
    runtime = CasperRuntime(tmp_path)

    session = runtime.initialize()

    assert session.status == "initialized"
    assert runtime.session == session
    assert (tmp_path / "state" / "session.json").exists()


def test_runtime_records_evidence(tmp_path):
    runtime = CasperRuntime(tmp_path)

    evidence = runtime.record_evidence(
        source="unit-test",
        content={"signal": "runtime"},
    )

    assert evidence.source == "unit-test"
    assert evidence.content["signal"] == "runtime"
    assert len(runtime.evidence.all()) == 1


def test_runtime_reuses_existing_session(tmp_path):
    first = CasperRuntime(tmp_path)
    created = first.initialize()

    second = CasperRuntime(tmp_path)
    loaded = second.initialize()

    assert loaded == created
