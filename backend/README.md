# Backend – EduMap Rankings

FastAPI backend for the EduMap Rankings project.

---

## 🛠 Tech Stack

- FastAPI
- SQLModel
- PostgreSQL
- Pydantic v2
- uv (recommended) or pip

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in:

```

backend/src/.env

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

### Using uv (recommended)

```bash
# from project root
uv sync --project backend
uv run --project backend fastapi dev backend/src/main.py

# or change directory
cd backend/
uv sync
uv run fastapi dev src/main.py
```

### Using pip

```bash
# from project root
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install backend/
fastapi dev backend/src/main.py

# or change directory
cd backend/
python3 -m venv .venv
source .venv/bin/activate
pip install .
fastapi dev src/main.py
```

## 📝 Notes

- Database tables are created on startup if they do not exist
- Sync SQLModel is used intentionally for simplicity
