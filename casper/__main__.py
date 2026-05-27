from __future__ import annotations

import json
import sys
from pathlib import Path

from casper.core.runtime import CasperRuntime


def build_runtime() -> CasperRuntime:
    workspace = Path.cwd() / ".casper"
    return CasperRuntime(workspace=workspace)


def status() -> None:
    runtime = build_runtime()
    session = runtime.initialize()

    payload = {
        "workspace": str(runtime.workspace),
        "session_id": session.session_id,
        "can_advance": runtime.validate(),
        "evidence_count": len(runtime.evidence.all()),
        "rule_count": len(runtime.rules.rules),
    }

    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"

    if command == "status":
        status()
        return

    raise SystemExit(f"unknown command: {command}")


if __name__ == "__main__":
    main()
