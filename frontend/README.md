# Frontend – EduRadar

Nuxt 4 frontend for the EduRadar project.

---

## 🛠 Tech Stack

- Nuxt 4
- Vue 3
- TypeScript
- Tailwind CSS
- MapLibre GL
- pnpm

---

## 📦 Installation

```bash
pnpm install
```

or from the project root:

```bash
pnpm --dir frontend install
```

---

## 🚀 Development Server

```bash
pnpm dev
```

or:

```bash
pnpm --dir frontend dev
```

The app will be available at:

```
http://localhost:3000
```

---

## 🐳 Running with Docker

The frontend Dockerfile is multi-stage:

- `dev` target: Nuxt dev server with HMR
- `prod` target: Nitro output (`node /app/frontend/server/index.mjs`)

From the project root (development):

```bash
docker compose up frontend --watch
```

Production-like run:

```bash
docker compose -f compose.yaml -f compose.prod.yaml build frontend
docker compose -f compose.yaml -f compose.prod.yaml up -d frontend
```

## 🌍 Environment Variables

Public runtime variables should be defined using:

```env
NUXT_PUBLIC_*
```

Example configuration in [`.env.example`](frontend/.env.example).
