from casper.core.runtime import CasperRuntime


def test_create_finding_accepts_target(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    finding = runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    assert finding.title == "Missing authorization check"
    assert finding.severity == "medium"
    assert finding.target == "example.com"
    assert finding.status == "new"


def test_create_finding_persists_target(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    restored = CasperRuntime(tmp_path)
    restored.initialize()

    findings = restored.findings.all()

    assert len(findings) == 1
    assert findings[0].target == "example.com"
