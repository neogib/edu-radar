# Frontend – EduMap Rankings

Nuxt 4 frontend for the EduMap Rankings project.

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

## 🌍 Environment Variables

Public runtime variables should be defined using:

```env
NUXT_PUBLIC_*
```

Example configuration in `frontend/.env`:

```env
NUXT_PUBLIC_API_BASE=/api
NUXT_PROXY_URL=http://localhost:8000
```
