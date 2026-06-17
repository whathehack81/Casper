from casper.core.runtime import CasperRuntime
from casper.rules.builtin import code_review_rule


def test_target_set_persists_mode(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()

    target = runtime.set_target(
        name="Electroneum Legacy Blockchain",
        scope="Bugcrowd code review",
        mode="code",
    )

    loaded = runtime.load_target()

    assert target.mode == "code"
    assert loaded.mode == "code"


def test_code_review_rule_passes_with_ready_finding_and_code_evidence(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()

    finding = runtime.create_finding(
        title="code issue",
        severity="medium",
        target="repo",
    )

    evidence = runtime.record_evidence(
        source="repo-head",
        content={
            "target": "repo",
            "status": 200,
            "observation": "repo_head=abc123",
        },
    )

    runtime.link_finding_evidence(
        finding_id=finding.finding_id,
        evidence_id=evidence.evidence_id,
    )

    for idx in range(2):
        extra = runtime.record_evidence(
            source=f"source-grep-{idx}",
            content={
                "target": "src",
                "status": 200,
                "observation": f"src/file.cpp:{idx}: validation code",
            },
        )
        runtime.link_finding_evidence(
            finding_id=finding.finding_id,
            evidence_id=extra.evidence_id,
        )

    runtime.set_finding_status(
        finding_id=finding.finding_id,
        status="ready",
    )

    runtime.register_rule(code_review_rule(runtime.evidence, runtime.findings))

    assert runtime.validate() is True
