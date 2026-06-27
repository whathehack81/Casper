from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from casper import rip_cli


def invoke_rip(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["casper-rip", *argv])
    rip_cli.main()


def read_json_output(
    capsys: pytest.CaptureFixture[str],
) -> dict[str, Any] | list[dict[str, Any]]:
    captured = capsys.readouterr()
    return json.loads(captured.out)


def test_rip_cli_capsule_lifecycle(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    invoke_rip(
        monkeypatch,
        [
            "run",
            "--target",
            "local-cli-test",
            "--repetitions",
            "1",
            "--expect-stdout",
            "CASPER_RIP_OK",
            "--",
            sys.executable,
            "-c",
            "print('CASPER_RIP_OK')",
        ],
    )
    capsule = read_json_output(capsys)

    assert isinstance(capsule, dict)
    assert capsule["status"] == "VERIFIED"
    assert capsule["target"] == "local-cli-test"
    assert capsule["passed_attempts"] == 1
    assert capsule["required_passes"] == 1

    validation_id = capsule["validation_id"]
    capsule_path = tmp_path / ".casper" / "rip" / f"{validation_id}.json"
    assert capsule_path.exists()

    invoke_rip(monkeypatch, ["list"])
    rows = read_json_output(capsys)
    assert isinstance(rows, list)
    matching_rows = [row for row in rows if row["validation_id"] == validation_id]
    assert matching_rows == [
        {
            "capsule_path": str(capsule_path),
            "finding_id": None,
            "passed_attempts": 1,
            "required_passes": 1,
            "status": "VERIFIED",
            "title": None,
            "validation_id": validation_id,
        }
    ]

    invoke_rip(monkeypatch, ["show", validation_id])
    loaded = read_json_output(capsys)
    assert isinstance(loaded, dict)
    assert loaded["validation_id"] == validation_id
    assert loaded["status"] == "VERIFIED"
    assert loaded["target"] == "local-cli-test"
