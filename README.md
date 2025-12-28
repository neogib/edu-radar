# EduMap Ranking

## 🛠️ Tech stack:

- Vue 3
- TypeScript
- FastAPI
- Vitest, Playwright, and Pytest

## 🗄️ Database Configuration

### PostgreSQL Environment Variables

Set PostgreSQL credentials in `backend/app/core/.env`, format:

```ini
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_DB=
```

---

## 🐳 Running the project with Docker

### 1. Prerequisites

- Install Docker Desktop before proceeding: [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Clone the repository:

```bash
git clone https://github.com/KubaBrambor/FujiTech-students_app.git
cd FujiTech-students_app
```

### 3. Running the entire project with Docker

To build and run both frontend and backend services, use:

```bash
docker compose up --build
```

If you want to force a clean rebuild without cache, use:

```bash
docker compose build --no-cache
docker compose up
```

To stop the containers, run:

```bash
docker compose down
```

To remove images and volumes after stopping, run:

```bash
docker compose down --rmi all --volumes
```

### Running a single service with Docker

#### Running only the backend:

```bash
docker compose up --build backend
```

To restart only the backend container:

```bash
docker compose restart backend
```

#### Running only the frontend:

```bash
docker compose up --build frontend
```

To restart only the frontend container:

```bash
docker compose restart frontend
```

---

## ⚙️ Running the project natively (without Docker)

### 1. Clone the repository:

```bash
git clone https://github.com/KubaBrambor/FujiTech-students_app.git
cd FujiTech-students_app
```

### 2. Install dependencies:

#### Install backend dependencies and activate the virtual environment:

For pip users:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate   # On Windows: backend\.venv\Scripts\activate
pip install backend/
```

For uv users:

```bash
uv sync --project backend
```

#### Install frontend dependencies (using pnpm):

```bash
pnpm --dir frontend install
```

### 3. Run the services:

#### Run backend:

**You can run the backend using FastAPI:**

- for pip users

```bash
fastapi dev backend/main.py
```

- for uv users

```bash
uv run --project backend fastapi dev backend/main.py
```

**Or directly with Uvicorn:**

- for pip users

```bash
uvicorn backend.main:app --reload
```

- for uv users

```bash
uv run --project backend uvicorn backend.main:app --reload
```

#### Run frontend:

```bash
pnpm --dir frontend dev
```

---
