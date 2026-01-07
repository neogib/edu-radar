# EduMap Ranking

## 🛠️ Tech stack:

- **Frontend:** Nuxt 4, Vue 3, TypeScript, Tailwind CSS
- **Backend:** FastAPI, PostgreSQL, SQLModel
- **Map:** MapLibre GL (via Vue MapLibre) + OpenFreeMap
- **Package Managers:** pnpm (Frontend), uv or pip (Backend)
- **Testing:** Vitest, Playwright, and Pytest
- **Containers:** Docker with Docker Compose Watch

## 🗄️ Database Configuration

### PostgreSQL Environment Variables

Set PostgreSQL credentials in `backend/src/.env`, format:

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

- **Windows/macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop).
- **Linux:** Install [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose plugin](https://docs.docker.com/compose/install/).

### 2. Clone the repository:

```bash
git clone https://github.com/neogib/edu-map-rankings.git
cd edu-map-rankings
```

### Running the project with docker (first time & development)

For the initial setup and the best development experience (automatic file sync and rebuilds), run:

```bash
docker compose up --build --watch
```

This will build the images, start all services, and watch files defined in `develop.watch`.

---

### Stopping the services

To stop **and remove** containers, networks, and related resources:

```bash
docker compose down
```

If you only want to stop containers without removing them:

```bash
docker compose stop
```

---

If you want to force a clean rebuild without cache:

```bash
docker compose build --no-cache
docker compose up
```

---

## ⚙️ Running the project natively (without Docker)

### 1. Clone the repository:

```bash
git clone https://github.com/neogib/edu-map-rankings.git
cd edu-map-rankings
```

### 2. Install dependencies:

### Install backend dependencies and activate the virtual environment:

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
fastapi dev backend/src/main.py
```

- for uv users

```bash
uv run --project backend fastapi dev backend/src/main.py
```

**Or directly with Uvicorn:**

- for pip users

```bash
uvicorn backend.src.main:app --reload
```

- for uv users

```bash
uv run --project backend uvicorn backend.src.main:app --reload
```

#### Run frontend:

```bash
pnpm --dir frontend dev
```

---
