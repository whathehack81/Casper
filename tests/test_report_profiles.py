import json

from casper.__main__ import cmd_report
from casper.core.runtime import CasperRuntime


def test_report_uses_code_profile_without_name_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()
    runtime.set_target(
        name="Electroneum Legacy Blockchain",
        scope="Bugcrowd code review",
        mode="code",
    )

    finding = runtime.create_finding(
        title="code issue",
        severity="medium",
        target="repo",
    )

    for source in ("repo-head", "source-grep", "patch-diff"):
        evidence = runtime.record_evidence(
            source=source,
            content={
                "target": "repo",
                "evidence_type": "code",
                "result": "confirmed",
                "observation": "repo_head src/file.cpp patch diff",
            },
        )
        runtime.link_finding_evidence(
            finding_id=finding.finding_id,
            evidence_id=evidence.evidence_id,
        )

    runtime.set_finding_status(
        finding_id=finding.finding_id,
        status="ready",
    )

    cmd_report()

    payload = json.loads(capsys.readouterr().out)

    assert payload["target"]["mode"] == "code"
    assert payload["profile"] == "code-review-strict"
    assert payload["can_advance"] is True
    assert payload["findings"][0]["validation_state"] == "confirmed"
    assert payload["findings"][0]["can_advance"] is True
