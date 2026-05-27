from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class WorkerContext:
    worker_id: str
    run_id: str
    lane: str


def create_worker(
    run_id: str,
    lane: str,
) -> WorkerContext:
    seed = json.dumps(
        {
            "run_id": run_id,
            "lane": lane,
        },
        sort_keys=True,
    ).encode()

    worker_id = sha256(seed).hexdigest()[:16]

    return WorkerContext(
        worker_id=worker_id,
        run_id=run_id,
        lane=lane,
    )
