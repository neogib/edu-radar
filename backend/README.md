# Backend – EduRadar

FastAPI backend for the EduRadar project.

---

## 🛠 Tech Stack

- FastAPI
- SQLModel
- PostgreSQL
- Pydantic v2
- uv

---

## ⚙️ Configuration

### Environment Variables

Copy the example env files and fill in your values:

```bash
cp backend/.env.example backend/.env
cp backend/martin/.env.example backend/martin/.env
```

These variables are used both for Docker and native execution.

---

## 🐳 Running with Docker

The backend Dockerfile is multi-stage:

- `dev` target: `uvicorn --reload`
- `prod` target: `uvicorn --workers 2` (no reload, non-root user)

From the project root (development):

```bash
docker compose up backend --watch
```

Production-like run (prod build target):

```bash
docker compose -f compose.yaml -f compose.prod.yaml build backend
docker compose -f compose.yaml -f compose.prod.yaml up -d backend
```

---

## ⚙️ Running Natively (Without Docker)

### Using uv + uvicorn

```bash
# from project root
uv sync --project backend
uv run --project backend uvicorn app.main:app --reload

# or change directory
cd backend/
uv sync
uv run uvicorn app.main:app --reload
```
