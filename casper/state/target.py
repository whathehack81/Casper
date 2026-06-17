from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


VALID_TARGET_MODES = {"web", "api", "code", "blockchain", "mobile"}


@dataclass(frozen=True)
class TargetState:
    name: str
    scope: str
    mode: str = "web"


class TargetStore:
    def __init__(self, workspace: Path):
        self.workspace = workspace

    def set(self, name: str, scope: str, mode: str = "web") -> TargetState:
        if mode not in VALID_TARGET_MODES:
            allowed = ", ".join(sorted(VALID_TARGET_MODES))
            raise ValueError(f"invalid target mode: {mode}; expected one of: {allowed}")

        target = TargetState(name=name, scope=scope, mode=mode)
        self._persist(target)
        return target

    def load(self) -> TargetState:
        path = self.workspace / "state" / "target.json"

        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if "mode" not in data:
            data["mode"] = "web"

        return TargetState(**data)

    def _persist(self, target: TargetState) -> None:
        state_dir = self.workspace / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        with (state_dir / "target.json").open("w", encoding="utf-8") as handle:
            json.dump(asdict(target), handle, indent=2, sort_keys=True)
