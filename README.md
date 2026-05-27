# Casper

Deterministic security-analysis runtime for session state, evidence persistence, findings, rules, and reproducible workflow advancement.

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
  --observation "homepage reachable"
```

## Findings

```bash
PYTHONPATH="$PWD" python -m casper finding create \
  --title "Admin Exposure" \
  --severity medium

PYTHONPATH="$PWD" python -m casper finding list
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
