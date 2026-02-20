# EduRadar

## 🛠️ Tech stack:

- **Frontend:** Nuxt 4, Vue 3, TypeScript, Tailwind CSS
- **Backend:** FastAPI, PostgreSQL, SQLModel
- **Map:** MapLibre GL (via Vue MapLibre) + OpenFreeMap
- **Martin** for map tile rendering
- **Package Managers:** pnpm (Frontend), uv (Backend)
- **Containers:** Docker with Docker Compose Watch

## 📦 Project structure

- [`frontend/README.md`](frontend/README.md) – frontend setup, Nuxt specifics
- [`backend/README.md`](backend/README.md) – backend setup, FastAPI & database details

## ⚙️ Configuration

### Environment variables

Create `backend/.env` (you can copy from [`backend/.env.example`](backend/.env.example)) and set credentials. RSPO credentials are needed for fetching data from their API.
Next setup `frontend/.env` with the API URL (if different from default `http://localhost:8000`) and running [Martin](https://martin.maplibre.org/) URL. Check Martin installation steps if you want to run it without docker. For **Martin** configure `backend/martin/.env` with PostgreSQL database URL. You can copy example .env files from [`frontend/.env.example`](frontend/.env.example) and [`backend/martin/.env.example`](backend/martin/.env.example).

---

## 🐳 Running the project with Docker

### 1. Prerequisites

- **Windows/macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop).
- **Linux:** Install [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose plugin](https://docs.docker.com/compose/install/).

### 2. Clone the repository:

```bash
git clone https://github.com/neogib/edu-radar.git
cd edu-radar
```

### 3. Running the project with docker (first time & development)

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

#### Install backend dependencies (uv):

```bash
uv sync --project backend
```

#### Install frontend dependencies (using pnpm):

```bash
pnpm --dir frontend install
```

### 3. Run the services:

#### Run backend:

```bash
uv run --project backend uvicorn app.main:app --reload
```

Or from `backend/`:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

#### Run frontend:

```bash
pnpm --dir frontend dev
```

---
