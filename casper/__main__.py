from pathlib import Path

from casper.core.runtime import CasperRuntime


def main():
    workspace = Path.cwd() / ".casper"
    workspace.mkdir(exist_ok=True)

    runtime = CasperRuntime(workspace=workspace)
    print(f"Casper runtime initialized: {workspace}")


if __name__ == "__main__":
    main()
