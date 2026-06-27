import subprocess
import sys


def test_python_module_dispatches_rip_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "casper", "rip", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "casper rip" in result.stdout
