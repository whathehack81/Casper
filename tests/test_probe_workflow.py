from casper.core.runtime import CasperRuntime
from casper.rules.engine import Rule


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

    runtime.register_rule(
        Rule(
            name="successful probe evidence exists",
            check=lambda: any(
                entry.source == "http-probe"
                and entry.content.get("ok") is True
                for entry in runtime.evidence.all()
            ),
            pass_reason="successful probe evidence exists",
            fail_reason="missing successful probe evidence",
        )
    )

    assert runtime.validate() is True
