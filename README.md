# Healthcare Appointment Manager

Production-quality MVP scaffold (Phase 0). Authentication, booking, LLM, email, and calendar are not implemented yet.

## Prerequisites

- Python 3.11+ (3.13 is supported)
- Node.js 20+
- Docker Desktop (PostgreSQL and Redis)

## Environment variables

Copy the backend example file and adjust if needed:

```bash
cp backend/.env.example backend/.env
```

| Variable | Purpose | Local default |
|---|---|---|
| `APP_NAME` | API title | Healthcare Appointment Manager |
| `APP_ENV` | Environment label | `development` |
| `DEBUG` | Verbose logging | `true` |
| `SECRET_KEY` | Reserved for later JWT | `change-me-in-production` |
| `API_V1_PREFIX` | API prefix | `/api/v1` |
| `CORS_ORIGINS` | Comma-separated origins | `http://localhost:5173` |
| `DATABASE_URL` | SQLAlchemy URL (psycopg3) | `postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `HOLD_TTL_SECONDS` | Slot hold TTL | `300` (5 minutes) |
| `EMAIL_BACKEND` | `console` or `sendgrid` | `console` |
| `SENDGRID_API_KEY` | Used when backend is SendGrid | empty |
| `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` | LLM provider (later) | empty |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REDIRECT_URI` | OAuth (later) | empty |

Never commit `backend/.env` or API keys.

## Start the project locally

From the repository root:

```bash
docker compose up -d
```

Backend:

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

There are no schema migrations yet (`alembic upgrade head` is a no-op until models exist). Alembic is configured and ready.

Frontend (second terminal):

```bash
cd frontend
npm install
npm run dev
```

- API: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health
- Docs: http://127.0.0.1:8000/docs
- UI: http://localhost:5173

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm test
npm run build
```

Health checks ping PostgreSQL (`SELECT 1`) and Redis (`PING`). Docker Compose must be running for those checks to return `ok`.

If port 5432 is already used by a local PostgreSQL instance, stop it or change the Compose host port before `docker compose up -d`.
