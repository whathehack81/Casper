from casper.contracts.finding import Finding
from casper.evidence.registry import EvidenceRegistry


def test_finding_links_registry_evidence():
    registry = EvidenceRegistry()
    evidence = registry.add("scanner", {"endpoint": "/admin"})

    finding = Finding(title="Admin Exposure", severity="medium")
    finding.link_evidence(evidence.evidence_id)

    assert finding.evidence_ids == [evidence.evidence_id]
