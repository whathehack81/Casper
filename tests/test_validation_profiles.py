from casper.__main__ import register_profile_rules
from casper.core.runtime import CasperRuntime
from casper.projections.session_projection import rebuild_session


def test_web_validation_profile_requires_confirmed_finding(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()
    runtime.set_target(
        name="example.com",
        scope="web",
        mode="web",
    )

    finding = runtime.create_finding(
        title="Reflected parameter exposure",
        severity="medium",
        target="example.com",
    )
    evidence = runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 200,
            "observation": "GET /search?q=test reflected input",
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

    profile = register_profile_rules(runtime, "web")

    assert profile == "web-live-strict"
    assert runtime.validate() is True
    assert runtime.last_assessments[0].validation_state == "confirmed"
    assert runtime.last_assessments[0].can_advance is True


def test_false_positive_review_blocks_profile_advancement(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()
    runtime.set_target(
        name="repo",
        scope="code",
        mode="code",
    )

    finding = runtime.create_finding(
        title="Debug flag exposure",
        severity="low",
        target="repo",
    )
    for source in ("repo-head", "source-grep", "patch-diff"):
        evidence = runtime.record_evidence(
            source=source,
            content={
                "target": "repo",
                "observation": "debug flag guarded in test-only code",
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
    runtime.review_finding(
        finding_id=finding.finding_id,
        false_positive_reason="test-only code path",
        validation_state="false_positive",
        confirmation_status="rejected",
        confidence=0.9,
    )

    register_profile_rules(runtime, "code")

    assert runtime.validate() is False
    assert runtime.last_assessments[0].validation_state == "false_positive"
    assert runtime.last_assessments[0].false_positive_reason == "test-only code path"


def test_session_projection_tracks_validation_outcomes(tmp_path):
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()
    finding = runtime.create_finding(
        title="Open redirect",
        severity="medium",
        target="example.com",
    )
    evidence = runtime.record_evidence(
        source="manual-check",
        content={
            "target": "example.com",
            "status": 302,
            "observation": "GET /next redirected to attacker-controlled host",
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

    register_profile_rules(runtime, "web")
    assert runtime.validate() is True

    projection = rebuild_session(runtime.events.all())

    assert projection.validation_modes == ["web"]
    assert projection.can_advance is True
    assert projection.advanceable_findings == [finding.finding_id]
