# Casper

> **A deterministic validation and evidence runtime for security research.**

Casper is built for the work that happens **after an interesting signal appears**: deciding whether it represents a real security boundary, preserving the evidence, stating attacker capability, reproducing the behavior, and advancing only findings that can withstand review.

It is intentionally **not a vulnerability scanner**. Discovery tools can generate candidates; Casper is the reasoning and validation layer that determines what those candidates actually mean.

## Why Casper exists

Security research often fails in the space between observation and proof:

- A suspicious response is treated as impact.
- A reliability problem is presented as a security vulnerability.
- Scanner severity is confused with validated severity.
- Evidence is scattered across terminals, notes, and browser captures.
- Findings advance before attacker capability or reproducibility is established.

Casper turns that process into a structured, replayable workflow.

## Validation model

A candidate finding should not advance because it looks severe. It advances when the evidence supports it.

Casper tracks and evaluates:

- **Target and scope context**
- **Attacker capability and prerequisites**
- **Requests, responses, observations, and supporting artifacts**
- **Validation state and confirmation status**
- **False-positive and expected-behavior reasons**
- **Finding lifecycle and advancement decisions**
- **Reproducible reports generated from preserved evidence**

Gatekeeper rules make advancement explicit instead of relying on memory or intuition.

## Design principles

- Authorization and scope first
- Evidence before severity
- Deterministic reproduction over speculation
- Product-specific impact over generic noise
- Minimal controlled validation
- Clear separation between discovery, validation, and impact proof
- False positives documented rather than forced into reports
- Decisions that can be replayed and reviewed later

## Core capabilities

- Session and workspace state
- Target profiles and scope modes
- Structured evidence contracts
- Finding creation and review
- Validation-state tracking
- Gatekeeper advancement rules
- Replayable reasoning decisions
- Deterministic report generation
- Standard-library Python runtime

## Project status

Casper is under active development. The current public runtime focuses on the validation foundation: state, evidence, findings, rules, CLI workflows, and reproducible decisions.

Future work continues toward deeper evidence correlation and tightly controlled impact validation while preserving Casper's central rule:

> **Do not claim more than the evidence proves.**

## Prerequisites

- Python 3.11 or later
- No external runtime dependencies; Casper uses the Python standard library

## Installation

```bash
git clone https://github.com/whathehack81/Casper.git
cd Casper
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

After installation:

```bash
casper status
```

## Quickstart

### 1. Check workspace status

```bash
casper status
```

### 2. Reset the workspace

```bash
casper workspace reset
```

### 3. Set an authorized target

```bash
casper target set --name example.com --scope web
casper target show
```

### 4. Run a target probe

```bash
casper run target
```

### 5. Add evidence

```bash
casper evidence add \
  --source manual-check \
  --target example.com \
  --status 200 \
  --proof request \
  --proof response \
  --observation "homepage reachable"
```

### 6. Create and review a finding

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

### 7. Validate and report

```bash
casper validate
casper report
```

## Running tests

```bash
pip install pytest
pytest -q
```

## About the maintainer

Casper is created and maintained by **Rob (`whathehack81`)**, an independent security researcher and engineer working hands-on with threat modeling, vulnerability validation, adversarial analysis, Linux environments, source review, networking, and evidence-driven disclosure workflows since 2011.

The project reflects a validation-first research philosophy: understand the boundary, reproduce the behavior, prove only the impact that is actually present, and park unsupported findings.

## License

MIT License. See [`LICENSE`](LICENSE).
