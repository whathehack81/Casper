from casper.core.runtime import CasperRuntime


def test_record_non_http_evidence_without_status(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()

    evidence = runtime.record_evidence(
        source="patch-summary",
        content={
            "target": "src/file.cpp",
            "evidence_type": "patch",
            "result": "confirmed",
            "observation": "patch changed validation behavior",
        },
    )

    assert evidence.content["evidence_type"] == "patch"
    assert evidence.content["result"] == "confirmed"
    assert "status" not in evidence.content
