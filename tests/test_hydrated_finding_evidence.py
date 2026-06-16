from casper.core.runtime import CasperRuntime


def test_export_findings_hydrates_linked_evidence(tmp_path):
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

    runtime.link_finding_evidence(
        title="Missing authorization check",
        evidence_id=evidence.evidence_id,
    )

    findings = runtime.export_findings()

    assert len(findings) == 1
    assert findings[0]["evidence_ids"] == [evidence.evidence_id]
    assert findings[0]["evidence"][0]["evidence_id"] == evidence.evidence_id
    assert findings[0]["evidence"][0]["source"] == "manual-check"
    assert findings[0]["evidence"][0]["content"]["status"] == 200
