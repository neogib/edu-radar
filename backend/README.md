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

From the project root:

```bash
docker compose up backend --watch
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
