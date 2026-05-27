from casper.contracts.finding import Finding
from casper.evidence.registry import EvidenceRegistry


def test_finding_links_registry_evidence():
    registry = EvidenceRegistry()

    evidence = registry.add(
        source="scanner",
        content={"endpoint": "/admin"},
    )

    finding = Finding(
        title="Admin Exposure",
        severity="medium",
    )

    finding.metadata["evidence_ids"] = [evidence.evidence_id]

    assert (
        finding.metadata["evidence_ids"][0]
        == evidence.evidence_id
    )
