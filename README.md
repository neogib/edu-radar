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

Before running the project, configure the following env files (copy from the provided examples and fill in your values):

- [`backend/.env.example`](backend/.env.example) — app credentials, including RSPO API credentials required for data fetching
- [`frontend/.env.example`](frontend/.env.example) — API URL (defaults to `http://localhost:8000`) and [Martin](https://martin.maplibre.org/) tile server URL
- [`backend/martin/.env.example`](backend/martin/.env.example) — PostgreSQL connection URL for Martin

---

## 🐳 Running the project with Docker

### Docker files used

- `compose.yaml` — shared base config (prod-safe defaults)
- `compose.override.yaml` — development overrides (auto-loaded by Docker Compose)
- `compose.prod.yaml` — explicit production overlay

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

### 4. Running the project in production mode

Build all production images:

```bash
docker compose -f compose.yaml -f compose.prod.yaml build
```

Start all services in background:

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

Stop production services:

```bash
docker compose -f compose.yaml -f compose.prod.yaml down
```

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
docker compose -f compose.yaml -f compose.prod.yaml build --no-cache
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

---

## ⚙️ Running the project natively (without Docker) for development

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
