from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class AxisState:
    session_id: str
    started_at: str
    workspace: Path


class CasperAxis:
    def __init__(self, workspace: Path):
        self.workspace = workspace

        self.state = AxisState(
            session_id=datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
            started_at=datetime.utcnow().isoformat(),
            workspace=workspace,
        )

    def initialize(self) -> None:
        print(f"[+] Axis session: {self.state.session_id}")
        print(f"[+] Workspace: {self.workspace}")

    def validate(self) -> bool:
        required = [
            self.workspace / "state",
            self.workspace / "evidence",
            self.workspace / "logs",
        ]

        for path in required:
            if not path.exists():
                print(f"[-] Missing: {path}")
                return False

        print("[+] Axis validation passed")
        return True
