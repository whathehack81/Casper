from __future__ import annotations

import hashlib
import json
import platform
import socket
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class RunManifest:
    run_id: str
    timestamp: str
    hostname: str
    platform: str
    cwd: str
    argv: list[str]
    python_version: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_manifest(argv: list[str]) -> RunManifest:
    timestamp = datetime.now(timezone.utc).isoformat()

    seed = json.dumps({
        "argv": argv,
        "timestamp": timestamp,
        "hostname": socket.gethostname(),
    }, sort_keys=True).encode()

    run_id = hashlib.sha256(seed).hexdigest()[:16]

    return RunManifest(
        run_id=run_id,
        timestamp=timestamp,
        hostname=socket.gethostname(),
        platform=platform.platform(),
        cwd=str(Path.cwd()),
        argv=argv,
        python_version=platform.python_version(),
    )


def write_manifest(path: Path, manifest: RunManifest) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(manifest.to_dict(), indent=2),
        encoding="utf-8",
    )

    return path
