# DovvyBuddy Python Backend (PR3.2a)

This folder contains a minimal FastAPI + SQLAlchemy scaffold used as the Python backend foundation for the project.

Quick start (assumes Python 3.11+ and poetry):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install "poetry>=1.5"
poetry install
cp .env.example .env
# Edit DATABASE_URL in .env
uvicorn app.main:app --reload --port 8000
```

APIs:
- `GET /health` — health check
- `POST /api/chat` — placeholder chat endpoint
- `GET/POST /api/sessions` — placeholder session endpoints
- `POST /api/leads` — placeholder lead endpoint
