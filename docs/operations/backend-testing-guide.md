# Backend Testing Guide

Last verified: 2026-03-02

## 1. Environment Setup

From repository root:

```bash
cp .env.example .env.local
```

Minimum for most backend tests:

```bash
GEMINI_API_KEY=your_actual_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dovvybuddy_test
ENABLE_ADK=true
ENABLE_AGENT_ROUTING=true
ADK_MODEL=gemini-2.5-flash-lite
```

## 2. Install Backend Dependencies

```bash
cd apps/api
../../.venv/bin/pip install -e .
```

## 3. Canonical Test Commands

Run from repository root:

```bash
export PYTHONPATH="$PWD/apps/api"
```

### Full backend suite

```bash
.venv/bin/python -m pytest apps/api/tests -q
```

### Unit only

```bash
.venv/bin/python -m pytest apps/api/tests/unit -q
```

### Integration only

```bash
.venv/bin/python -m pytest apps/api/tests/integration -q
```

### Coverage

```bash
.venv/bin/python -m pytest apps/api/tests --cov=app --cov-report=html
```

## 4. Important Notes

- `apps/api/pytest.ini` sets `--import-mode=importlib` by default.
- Service-level integration tests may skip when `GEMINI_API_KEY` is not set.
- `tests/integration/scripts/test_full_ingestion.py` now uses in-memory test doubles and does not require external DB/network access.
- Chat orchestration tests remain resilient when ADK routing fails; fallback route behavior is part of expected runtime behavior.

## 5. Useful Filters

```bash
# Integration marker
.venv/bin/python -m pytest -m integration apps/api/tests -q

# Skip slow tests
.venv/bin/python -m pytest -m "not slow" apps/api/tests -q

# Stop on first failure
.venv/bin/python -m pytest -x apps/api/tests -q
```

## 6. Troubleshooting

### Import/module errors

```bash
export PYTHONPATH="$PWD/apps/api"
cd apps/api && ../../.venv/bin/pip install -e .
```

### DB errors

```bash
pg_isready -h localhost -p 5432
echo "$DATABASE_URL"
```

### Missing Gemini key

If `GEMINI_API_KEY` is missing, some integration tests are skipped by design.
