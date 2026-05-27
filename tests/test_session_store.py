from casper.state.session import SessionStore


def test_session_store_create(tmp_path):
    store = SessionStore(tmp_path)

    session = store.create()

    assert session.status == "initialized"
    assert (tmp_path / "state" / "session.json").exists()
