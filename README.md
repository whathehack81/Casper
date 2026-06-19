# Casper

Deterministic security-analysis runtime for session state, evidence persistence, findings, rules, and reproducible workflow advancement.

Casper validates findings through mode-specific profiles, structured evidence contracts, Gatekeeper advancement rules, and replayable reasoning decisions.

## Prerequisites

- Python 3.11 or later
- No external runtime dependencies — Casper uses only the Python standard library

## Installation

Clone the repository and install the package in editable mode:

```bash
git clone https://github.com/whathehack81/Casper.git
cd Casper
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
```

After installation the `casper` command is available on your `PATH`:

```bash
casper status
```

## Quickstart

### 1 — Check workspace status

```bash
casper status
```

### 2 — Reset workspace

```bash
casper workspace reset
```

### 3 — Set a target

```bash
casper target set --name example.com --scope web
casper target show
```

### 4 — Run a target probe

```bash
casper run target
```

### 5 — Add evidence manually

```bash
casper evidence add \
  --source manual-check \
  --target example.com \
  --status 200 \
  --proof request \
  --proof response \
  --observation "homepage reachable"
```

### 6 — Create and review a finding

```bash
casper finding create \
  --title "Admin Exposure" \
  --severity medium

casper finding list

casper finding review \
  --finding-id <finding-id> \
  --validation-state false_positive \
  --confirmation-status rejected \
  --false-positive-reason "expected behavior"
```

### 7 — Validate and report

```bash
casper validate
casper report
```

## Running tests

```bash
pip install pytest
pytest -q
```

## Troubleshooting

**`casper: command not found`**
Ensure your virtual environment is activated (`source .venv/bin/activate`) and that you installed the project with `pip install -e .`.

**`ModuleNotFoundError: No module named 'casper'`**
Run `pip install -e .` from the repository root so the package is installed in your active environment.

**Tests fail with import errors**
Make sure you have installed the project (`pip install -e .`) before running `pytest`.

**Python version mismatch**
Casper requires Python 3.11 or later. Check your version with `python --version` and switch to a supported release if needed.

