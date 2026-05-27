from __future__ import annotations

from hashlib import sha256
import json

from casper.events.store import Event


def replay_digest(events: list[Event]) -> str:
    normalized = []

    for event in events:
        normalized.append(
            {
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "payload": event.payload,
            }
        )

    return sha256(
        json.dumps(
            normalized,
            sort_keys=True,
        ).encode()
    ).hexdigest()
