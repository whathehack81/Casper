from __future__ import annotations

import sys
from collections.abc import Sequence

from casper.__main__ import main as legacy_main
from casper.rip_cli import main as rip_main
from casper.tools_cli import main as tools_main

TOOL_ALIAS_COMMANDS = {"doctor", "list", "profile", "profiles", "run"}


def should_dispatch_tool_alias(argv: Sequence[str]) -> bool:
    return len(argv) >= 2 and argv[0] == "tool" and argv[1] in TOOL_ALIAS_COMMANDS


def should_dispatch_rip(argv: Sequence[str]) -> bool:
    return len(argv) >= 1 and argv[0] == "rip"


def main() -> None:
    argv = sys.argv[1:]
    if should_dispatch_rip(argv):
        original_argv = sys.argv
        try:
            sys.argv = ["casper-rip", *argv[1:]]
            rip_main()
        finally:
            sys.argv = original_argv
        return

    if should_dispatch_tool_alias(argv):
        original_argv = sys.argv
        try:
            sys.argv = ["casper-tools", *argv[1:]]
            tools_main()
        finally:
            sys.argv = original_argv
        return

    legacy_main()


if __name__ == "__main__":
    main()
