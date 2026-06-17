import argparse
import json

import pytest

from casper.__main__ import cmd_tool_httpx
from casper.tools.executor import CommandResult


def test_tool_httpx_propagates_wrapped_exit_code(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)

    def fake_run_command(command):
        return CommandResult(
            command=command,
            exit_code=7,
            stdout="",
            stderr="httpx failed",
            timestamp="2026-06-16T00:00:00+00:00",
            sha256="abc123",
        )

    monkeypatch.setattr("casper.__main__.run_command", fake_run_command)

    args = argparse.Namespace(argv=["--", "-bad-flag"], run_id="run123")

    with pytest.raises(SystemExit) as exc:
        cmd_tool_httpx(args)

    assert exc.value.code == 7

    payload = json.loads(capsys.readouterr().out)
    assert payload["tool"] == "httpx"
    assert payload["command"] == ["httpx", "-bad-flag"]
    assert payload["exit_code"] == 7
    assert payload["stderr_bytes"] == len("httpx failed".encode())
