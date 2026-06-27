import os
import subprocess
from pathlib import Path


def test_dev_launcher_dispatches_rip_help() -> None:
    repo = Path(__file__).resolve().parents[1]
    launcher = repo / "bin" / "casper"

    env = os.environ.copy()
    env["CASPER_ROOT"] = str(repo)

    result = subprocess.run(
        [str(launcher), "rip", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "casper rip" in result.stdout
