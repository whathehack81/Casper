#!/usr/bin/env python3
"""
Casper controlled initialization entry point.
Creates the baseline axis workspace and package structure.
"""

from pathlib import Path
import sys


CASPER_ROOT = Path.cwd()
WORKSPACE = CASPER_ROOT / ".casper"

REQUIRED_DIRS = [
    WORKSPACE,
    WORKSPACE / "state",
    WORKSPACE / "evidence",
    WORKSPACE / "logs",
    CASPER_ROOT / "casper",
    CASPER_ROOT / "casper" / "core",
    CASPER_ROOT / "casper" / "rules",
    CASPER_ROOT / "casper" / "state",
    CASPER_ROOT / "casper" / "evidence",
    CASPER_ROOT / "casper" / "tools",
]

REQUIRED_FILES = [
    CASPER_ROOT / "casper" / "__init__.py",
    CASPER_ROOT / "casper" / "core" / "__init__.py",
    CASPER_ROOT / "casper" / "rules" / "__init__.py",
    CASPER_ROOT / "casper" / "state" / "__init__.py",
    CASPER_ROOT / "casper" / "evidence" / "__init__.py",
    CASPER_ROOT / "casper" / "tools" / "__init__.py",
]


def validate_environment() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ required")


def create_structure() -> None:
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

    for file_path in REQUIRED_FILES:
        file_path.touch(exist_ok=True)


def banner() -> None:
    print("=" * 50)
    print(" Casper Axis Bootstrap")
    print("=" * 50)


def bootstrap() -> None:
    banner()
    validate_environment()
    create_structure()

    print("[+] Workspace initialized")
    print(f"[+] Root: {CASPER_ROOT}")
    print(f"[+] State: {WORKSPACE / 'state'}")
    print(f"[+] Evidence: {WORKSPACE / 'evidence'}")
    print(f"[+] Logs: {WORKSPACE / 'logs'}")


def main() -> None:
    bootstrap()


if __name__ == "__main__":
    main()
