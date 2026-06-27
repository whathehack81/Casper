from __future__ import annotations

import sys

from casper.core.runtime import CasperRuntime
from casper.tools.registry import get_tool, list_tools, run_registered_tool


def test_registered_tools_include_core_recon_tools() -> None:
    names = {item["name"] for item in list_tools()}
    assert {"httpx", "subfinder", "nuclei", "curl", "git", "python"}.issubset(names)
    assert get_tool("httpx").lane == "recon-http"


def test_registered_tool_records_evidence(tmp_path) -> None:
    runtime = CasperRuntime(tmp_path / ".casper")
    runtime.initialize()

    result = run_registered_tool(
        tool_name="python",
        argv=["-c", "print('CASPER_TOOL_OK')"],
        runtime=runtime,
        run_id="test-run",
        target="local",
    )

    assert result.exit_code == 0
    assert result.tool == "python"
    assert result.run_id == "test-run"
    assert result.lane == "utility"
    assert result.evidence_id

    evidence = runtime.evidence.all()[0]
    assert evidence.source == "tool-python"
    assert evidence.content["tool"] == "python"
    assert evidence.content["target"] == "local"
    assert evidence.content["result"] == "confirmed"

    stdout = (tmp_path / ".casper" / "artifacts" / f"{result.sha256}.stdout").read_text(encoding="utf-8")
    assert "CASPER_TOOL_OK" in stdout
