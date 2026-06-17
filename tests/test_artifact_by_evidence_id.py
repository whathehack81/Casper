import argparse

from casper.__main__ import resolve_artifact_sha
from casper.core.runtime import CasperRuntime


def test_resolve_artifact_sha_by_evidence_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()

    evidence = runtime.record_evidence(
        source="command-exec",
        content={
            "sha256": "abc123",
            "stdout_path": ".casper/artifacts/abc123.stdout",
            "stderr_path": ".casper/artifacts/abc123.stderr",
        },
    )

    args = argparse.Namespace(
        sha256=None,
        evidence_id=evidence.evidence_id,
    )

    assert resolve_artifact_sha(args) == "abc123"
