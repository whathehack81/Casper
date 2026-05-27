from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
import json


@dataclass(frozen=True)
class Event:
    timestamp: str
    event_type: str
    payload: dict


class EventStore:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.events_dir = workspace / "events"
        self.events_dir.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        event_type: str,
        payload: dict,
    ) -> Event:
        event = Event(
            timestamp=datetime.now(UTC).isoformat(),
            event_type=event_type,
            payload=dict(payload),
        )

        filename = (
            f"{event.timestamp.replace(':', '-')}"
            f"_{event.event_type}.json"
        )

        output = self.events_dir / filename

        output.write_text(
            json.dumps(asdict(event), indent=2, sort_keys=True),
            encoding="utf-8",
        )

        return event

    def all(self) -> list[Event]:
        events = []

        for path in sorted(self.events_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            events.append(Event(**data))

        return events
