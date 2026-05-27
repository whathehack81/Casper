from casper.core.runtime import CasperRuntime
from casper.rules.builtin import successful_probe_rule


def test_probe_evidence_allows_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path)
    runtime.initialize()

    runtime.record_evidence(
        source="http-probe",
        content={
            "url": "https://example.com",
            "ok": True,
            "status": 200,
            "content_type": "text/html",
            "error": None,
        },
    )

    runtime.register_rule(successful_probe_rule(runtime.evidence))

    assert runtime.validate() is True
