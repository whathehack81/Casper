# Contributing

Thank you for your interest in contributing to Casper.

## Getting started

1. Fork the repository and clone it locally.
2. Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest ruff mypy
```

3. Create a branch for your changes:

```bash
git checkout -b your-feature-name
```

## Running checks

Before submitting a pull request, ensure the following all pass locally:

```bash
ruff check .
mypy casper gatekeeper.py
pytest -q
```

## Pull request guidelines

- Keep changes focused and minimal.
- Include tests for new behavior where practical.
- Update `CHANGELOG.md` under `[Unreleased]` with a brief description of your change.
- Ensure CI passes before requesting a review.

## Reporting bugs

Open an issue with a clear description, steps to reproduce, and the Python version you are using.
