from casper.core.runtime import CasperRuntime


def test_finding_create_assigns_stable_finding_id(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    finding = runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    assert finding.finding_id is not None
    assert len(finding.finding_id) == 16


def test_link_evidence_by_finding_id(tmp_path):
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

    finding = runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    linked = runtime.link_finding_evidence(
        finding_id=finding.finding_id,
        evidence_id=evidence.evidence_id,
    )

    assert linked.evidence_ids == [evidence.evidence_id]


def test_set_status_by_finding_id(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    finding = runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    updated = runtime.set_finding_status(
        finding_id=finding.finding_id,
        status="ready",
    )

    assert updated.status == "ready"
