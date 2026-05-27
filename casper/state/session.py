"""
Casper session state.

Tracks one deterministic runtime session.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json


@dataclass(frozen=True)
class SessionState:
    session_id: str
    started_at: str
    status: str


class SessionStore:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.state_dir = workspace / "state"

    def create(self) -> SessionState:
        timestamp = datetime.utcnow()

        session = SessionState(
            session_id=timestamp.strftime("%Y%m%d-%H%M%S"),
            started_at=timestamp.isoformat(),
            status="initialized",
        )

        self._store(session)

        return session

    def _store(self, session: SessionState) -> None:
        output = self.state_dir / "session.json"

        with output.open("w", encoding="utf-8") as handle:
            json.dump(
                asdict(session),
                handle,
                indent=4,
                sort_keys=True,
            )
