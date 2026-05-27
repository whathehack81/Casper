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


def test_runtime_records_persistent_evidence(tmp_path):
    runtime = CasperRuntime(tmp_path)

    runtime.record_evidence(
        source="runtime",
        content={"signal": "persistent"},
    )

    assert (tmp_path / "evidence" / "index.json").exists()


def test_runtime_loads_existing_evidence(tmp_path):
    first = CasperRuntime(tmp_path)
    first.record_evidence(
        source="runtime",
        content={"signal": "resume"},
    )

    second = CasperRuntime(tmp_path)
    second.initialize()

    assert len(second.evidence.all()) == 1
