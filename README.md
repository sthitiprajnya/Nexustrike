# Autonomous Self-Evolving Pentesting AI Platform (Scaffold)

This repository now includes an executable scaffold that maps to the PRD:

- FastAPI backend (`backend/api/main.py`)
- Thread management (`backend/thread_manager.py`)
- Tool orchestration stubs (`tools/`)
- Evolution and evaluation modules (`evolution/`, `evaluation/`)
- Cross-engagement memory (`memory/compressed_learning.py`)
- Execution orchestrator (`execution/autonomous_executor.py`)
- Reporting pipeline (`reporting/`)
- Deployment helper (`scripts/deploy_autonomous_pentest.sh`)

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

## Test

```bash
pytest -q
```


### Notes

- `zstandard` is optional at runtime; if not installed, memory compression automatically falls back to `zlib`.


### Python compatibility

- Requirements are set as compatible ranges (not old hard pins) to prefer prebuilt wheels on Python 3.13 and avoid local Rust/C builds during install.
