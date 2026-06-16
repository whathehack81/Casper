import pytest

from casper.core.runtime import CasperRuntime


def test_set_finding_status_updates_existing_finding(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    finding = runtime.set_finding_status(
        title="Missing authorization check",
        status="ready",
    )

    assert finding.status == "ready"
    assert runtime.findings.all()[0].status == "ready"


def test_set_finding_status_rejects_invalid_status(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.create_finding(
        title="Missing authorization check",
        severity="medium",
        target="example.com",
    )

    with pytest.raises(ValueError, match="invalid status"):
        runtime.set_finding_status(
            title="Missing authorization check",
            status="invalid",
        )


def test_set_finding_status_rejects_missing_finding(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    with pytest.raises(ValueError, match="finding not found"):
        runtime.set_finding_status(
            title="Missing authorization check",
            status="ready",
        )
