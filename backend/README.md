# Backend – EduMap Rankings

FastAPI backend for the EduMap Rankings project.

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

Create a `.env` file in:

```
backend/.env
```

```ini
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_SERVER=
POSTGRES_PORT=5432
POSTGRES_DB=
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
