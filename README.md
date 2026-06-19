# Casper

Deterministic security-analysis runtime for session state, evidence persistence, findings, rules, and reproducible workflow advancement.

Casper now validates findings through mode-specific profiles, structured evidence contracts, Gatekeeper advancement rules, and replayable reasoning decisions.

## Run

```bash
PYTHONPATH="$PWD" python -m casper status
```

## Reset workspace

```bash
PYTHONPATH="$PWD" python -m casper workspace reset
```

## Set target

```bash
PYTHONPATH="$PWD" python -m casper target set --name example.com --scope web
PYTHONPATH="$PWD" python -m casper target show
```

## Run target probe

```bash
PYTHONPATH="$PWD" python -m casper run target
```

## Add evidence manually

```bash
PYTHONPATH="$PWD" python -m casper evidence add \
  --source manual-check \
  --target example.com \
  --status 200 \
  --proof request \
  --proof response \
  --observation "homepage reachable"
```

## Findings

```bash
PYTHONPATH="$PWD" python -m casper finding create \
  --title "Admin Exposure" \
  --severity medium

PYTHONPATH="$PWD" python -m casper finding list
```

## Review a finding

```bash
PYTHONPATH="$PWD" python -m casper finding review \
  --finding-id <finding-id> \
  --validation-state false_positive \
  --confirmation-status rejected \
  --false-positive-reason "expected behavior"
```

## Report

```bash
PYTHONPATH="$PWD" python -m casper report
```

## Validate

```bash
PYTHONPATH="$PWD" python -m casper validate
```

## Test

```bash
PYTHONPATH="$PWD" pytest -q
```
