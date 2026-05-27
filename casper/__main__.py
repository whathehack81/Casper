from pathlib import Path

from casper.core.runtime import CasperRuntime


def main() -> None:
    workspace = Path.cwd() / ".casper"

    runtime = CasperRuntime(workspace=workspace)
    session = runtime.initialize()

    print("Casper runtime initialized")
    print(f"Workspace: {workspace}")
    print(f"Session: {session.session_id}")
    print(f"Can advance: {runtime.validate()}")


if __name__ == "__main__":
    main()
