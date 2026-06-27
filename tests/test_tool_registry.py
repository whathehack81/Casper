from __future__ import annotations

from casper.core.runtime import CasperRuntime
from casper.tools.registry import (
    doctor_tools,
    get_profile,
    get_tool,
    list_profiles,
    list_tools,
    run_registered_tool,
)


def test_registered_tools_include_core_recon_tools() -> None:
    names = {item["name"] for item in list_tools()}
    assert {
        "httpx",
        "subfinder",
        "nuclei",
        "curl",
        "git",
        "python",
        "gitleaks",
        "trufflehog",
    }.issubset(names)
    assert get_tool("httpx").lane == "recon-http"
    assert get_tool("trufflehog").lane == "code-secret"


def test_tool_profiles_group_lanes() -> None:
    profiles = list_profiles()
    assert "recon" in profiles
    assert "secrets" in profiles
    assert "trufflehog" in profiles["secrets"]
    assert any(item["name"] == "trufflehog" for item in get_profile("secrets"))


def test_doctor_reports_installed_and_missing_tools() -> None:
    result = doctor_tools(profile="secrets")
    assert result["profile"] == "secrets"
    assert "installed" in result
    assert "missing" in result
    assert {item["name"] for item in result["tools"]} == {"gitleaks", "trufflehog"}


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

    artifact = tmp_path / ".casper" / "artifacts" / f"{result.sha256}.stdout"
    assert "CASPER_TOOL_OK" in artifact.read_text(encoding="utf-8")
