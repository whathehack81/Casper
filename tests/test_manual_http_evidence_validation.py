from casper.core.runtime import CasperRuntime
from casper.rules.builtin import successful_probe_rule


def test_manual_successful_http_status_allows_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 200,
            "observation": "manual successful HTTP evidence",
        },
    )

    runtime.register_rule(successful_probe_rule(runtime.evidence))

    assert runtime.validate() is True


def test_manual_redirect_http_status_allows_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 302,
            "observation": "manual redirect HTTP evidence",
        },
    )

    runtime.register_rule(successful_probe_rule(runtime.evidence))

    assert runtime.validate() is True


def test_manual_failed_http_status_blocks_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 500,
            "observation": "manual failed HTTP evidence",
        },
    )

    runtime.register_rule(successful_probe_rule(runtime.evidence))

    assert runtime.validate() is False


def test_non_http_manual_evidence_blocks_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.record_evidence(
        source="notes",
        content={
            "status": 200,
            "observation": "not HTTP evidence",
        },
    )

    runtime.register_rule(successful_probe_rule(runtime.evidence))

    assert runtime.validate() is False
