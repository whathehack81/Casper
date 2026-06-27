from __future__ import annotations

import sys

from casper.core.runtime import CasperRuntime
from casper.rip.validation import run_validation


def test_rip_validation_marks_finding_confirmed(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()
    finding = runtime.create_finding(
        title="deterministic proof",
        severity="high",
        target="local-test",
    )

    capsule = run_validation(
        runtime,
        finding_id=finding.finding_id,
        argv=[sys.executable, "-c", "print('RIP_OK')"],
        repetitions=2,
        expect_stdout=["RIP_OK"],
        run_id="test",
    )

    refreshed = runtime.findings.all()[0]
    assert capsule.status == "VERIFIED"
    assert capsule.passed_attempts == 2
    assert refreshed.validation_state == "confirmed"
    assert refreshed.confirmation_status == "confirmed"
    assert refreshed.confidence == 1.0
    assert (tmp_path / ".casper" / "rip" / f"{capsule.validation_id}.json").exists()
