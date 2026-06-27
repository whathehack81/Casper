from __future__ import annotations

from casper.cli import should_dispatch_tool_alias


def test_tool_alias_dispatches_registered_tool_commands() -> None:
    assert should_dispatch_tool_alias(["tool", "doctor"])
    assert should_dispatch_tool_alias(["tool", "doctor", "--profile", "secrets"])
    assert should_dispatch_tool_alias(["tool", "list"])
    assert should_dispatch_tool_alias(["tool", "profiles"])
    assert should_dispatch_tool_alias(["tool", "profile", "recon"])
    assert should_dispatch_tool_alias(["tool", "run", "trufflehog", "--", "--help"])


def test_tool_alias_leaves_legacy_tool_commands_alone() -> None:
    assert not should_dispatch_tool_alias(["tool", "httpx"])
    assert not should_dispatch_tool_alias(["tool", "git-head"])
    assert not should_dispatch_tool_alias(["status"])
    assert not should_dispatch_tool_alias([])
