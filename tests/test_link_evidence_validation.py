import pytest

from casper.core.runtime import CasperRuntime


def test_link_finding_evidence_requires_existing_evidence_id(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    with pytest.raises(ValueError, match="evidence not found"):
        runtime.link_finding_evidence(
            title="Missing authorization check",
            evidence_id="does-not-exist",
        )


def test_link_finding_evidence_accepts_existing_evidence_id(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    evidence = runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 200,
            "observation": "manual authz evidence",
        },
    )

    runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    finding = runtime.link_finding_evidence(
        title="Missing authorization check",
        evidence_id=evidence.evidence_id,
    )

    assert finding.evidence_ids == [evidence.evidence_id]
