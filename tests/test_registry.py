from casper.evidence.registry import EvidenceRegistry


def test_registry_add():
    registry = EvidenceRegistry()

    evidence = registry.add(
        source="unit-test",
        content={"signal": "test"},
    )

    assert evidence.source == "unit-test"
    assert evidence.content["signal"] == "test"

    exported = registry.export()

    assert len(exported) == 1
    assert exported[0]["evidence_id"]
