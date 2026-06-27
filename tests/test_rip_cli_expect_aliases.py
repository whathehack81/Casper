import subprocess
import sys


def test_rip_cli_stdout_contains_alias(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "casper",
            "rip",
            "run",
            "--validator",
            "smoke",
            "--stdout-contains",
            "alias-ok",
            "--",
            sys.executable,
            "-c",
            "print('alias-ok')",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"status": "VERIFIED"' in result.stdout
    assert '"stdout_contains": [' in result.stdout
    assert '"alias-ok"' in result.stdout


def test_rip_cli_stderr_contains_alias(tmp_path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "casper",
            "rip",
            "run",
            "--validator",
            "smoke",
            "--stderr-contains",
            "err-alias-ok",
            "--",
            sys.executable,
            "-c",
            "import sys; print('err-alias-ok', file=sys.stderr)",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert '"status": "VERIFIED"' in result.stdout
    assert '"stderr_contains": [' in result.stdout
    assert '"err-alias-ok"' in result.stdout
