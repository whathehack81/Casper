from pathlib import Path

from casper.tools.executor import persist_artifacts, run_command


def test_command_artifacts_are_persisted(tmp_path):
    result = run_command(["python", "-c", "print('artifact-ok')"])

    artifacts = persist_artifacts(result, tmp_path)

    stdout_path = Path(artifacts["stdout_path"])
    stderr_path = Path(artifacts["stderr_path"])

    assert stdout_path.exists()
    assert stderr_path.exists()
    assert stdout_path.read_text(encoding="utf-8").strip() == "artifact-ok"
    assert stderr_path.read_text(encoding="utf-8") == ""
