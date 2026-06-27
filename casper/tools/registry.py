from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from casper.core.runtime import CasperRuntime
from casper.tools.executor import export_result, persist_artifacts, run_command


@dataclass(frozen=True)
class ToolSpec:
    name: str
    binary: str
    lane: str
    description: str
    default_timeout: int = 120


@dataclass(frozen=True)
class ToolRun:
    tool: str
    command: list[str]
    exit_code: int
    evidence_id: str
    sha256: str
    stdout_path: str
    stderr_path: str
    stdout_bytes: int
    stderr_bytes: int
    run_id: str
    lane: str


TOOL_REGISTRY: dict[str, ToolSpec] = {
    "httpx": ToolSpec("httpx", "httpx", "recon-http", "HTTP probing and technology/status capture"),
    "subfinder": ToolSpec("subfinder", "subfinder", "recon-dns", "Passive subdomain discovery"),
    "assetfinder": ToolSpec("assetfinder", "assetfinder", "recon-dns", "Passive asset discovery"),
    "dnsx": ToolSpec("dnsx", "dnsx", "recon-dns", "DNS resolution and enrichment"),
    "naabu": ToolSpec("naabu", "naabu", "recon-port", "Port discovery"),
    "katana": ToolSpec("katana", "katana", "recon-content", "Crawler and URL discovery"),
    "gau": ToolSpec("gau", "gau", "recon-content", "Archived URL discovery"),
    "waybackurls": ToolSpec("waybackurls", "waybackurls", "recon-content", "Wayback URL discovery"),
    "nuclei": ToolSpec("nuclei", "nuclei", "validation-template", "Template-based validation", 300),
    "ffuf": ToolSpec("ffuf", "ffuf", "recon-content", "Content discovery", 300),
    "curl": ToolSpec("curl", "curl", "http-manual", "Manual HTTP request capture"),
    "jq": ToolSpec("jq", "jq", "transform", "JSON filtering"),
    "rg": ToolSpec("rg", "rg", "code-search", "Ripgrep source and evidence search"),
    "grep": ToolSpec("grep", "grep", "code-search", "Grep source and evidence search"),
    "git": ToolSpec("git", "git", "code-git", "Git repository inspection"),
    "trivy": ToolSpec("trivy", "trivy", "code-sca", "Dependency/container/IaC scanning", 300),
    "gitleaks": ToolSpec("gitleaks", "gitleaks", "code-secret", "Secret scanning", 300),
    "semgrep": ToolSpec("semgrep", "semgrep", "code-sast", "Static analysis", 300),
    "pytest": ToolSpec("pytest", "pytest", "code-test", "Python test execution", 300),
    "go": ToolSpec("go", "go", "code-test", "Go build/test tooling", 300),
    "mvn": ToolSpec("mvn", "mvn", "code-test", "Maven build/test tooling", 300),
    "gradle": ToolSpec("gradle", "gradle", "code-test", "Gradle build/test tooling", 300),
    "python": ToolSpec("python", "python", "utility", "Python interpreter utility", 300),
    "python3": ToolSpec("python3", "python3", "utility", "Python 3 interpreter utility", 300),
}


def list_tools() -> list[dict[str, Any]]:
    return [asdict(spec) for spec in sorted(TOOL_REGISTRY.values(), key=lambda item: item.name)]


def get_tool(name: str) -> ToolSpec:
    try:
        return TOOL_REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(TOOL_REGISTRY))
        raise ValueError(f"unknown tool: {name}. known tools: {known}") from exc


def build_runtime(workspace: Path | None = None) -> CasperRuntime:
    runtime = CasperRuntime(workspace=workspace or Path.cwd() / ".casper")
    runtime.initialize()
    return runtime


def run_registered_tool(
    *,
    tool_name: str,
    argv: list[str],
    runtime: CasperRuntime | None = None,
    run_id: str = "manual",
    lane: str | None = None,
    target: str | None = None,
    timeout: int | None = None,
) -> ToolRun:
    spec = get_tool(tool_name)
    selected_runtime = runtime or build_runtime()
    command = [spec.binary, *argv]
    selected_lane = lane or spec.lane
    result = run_command(command, timeout=timeout or spec.default_timeout)
    exported = export_result(result)
    artifacts = persist_artifacts(result, selected_runtime.workspace)

    evidence_payload: dict[str, Any] = {
        "tool": spec.name,
        "binary": spec.binary,
        "description": spec.description,
        "command": exported["command"],
        "exit_code": exported["exit_code"],
        "timestamp": exported["timestamp"],
        "sha256": exported["sha256"],
        "stdout_path": artifacts["stdout_path"],
        "stderr_path": artifacts["stderr_path"],
        "stdout_bytes": len(result.stdout.encode()),
        "stderr_bytes": len(result.stderr.encode()),
        "run_id": run_id,
        "lane": selected_lane,
        "target": target,
        "evidence_type": "command",
        "result": "confirmed" if result.exit_code == 0 else "failed",
    }

    evidence = selected_runtime.record_evidence(source=f"tool-{spec.name}", content=evidence_payload)
    return ToolRun(
        tool=spec.name,
        command=list(exported["command"]),
        exit_code=int(exported["exit_code"]),
        evidence_id=evidence.evidence_id,
        sha256=str(exported["sha256"]),
        stdout_path=artifacts["stdout_path"],
        stderr_path=artifacts["stderr_path"],
        stdout_bytes=evidence_payload["stdout_bytes"],
        stderr_bytes=evidence_payload["stderr_bytes"],
        run_id=run_id,
        lane=selected_lane,
    )
