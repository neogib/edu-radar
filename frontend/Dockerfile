# Base image shared by all stages.
FROM node:22-alpine AS base
WORKDIR /app/frontend

# Use pnpm via corepack (version pinned by packageManager in package.json).
RUN corepack enable

# Install dependencies first for better layer caching.
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

# Development stage: runs Nuxt dev server with HMR.
FROM base AS dev
COPY . .
EXPOSE 3000
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0", "--port", "3000"]

# Build stage: compiles Nuxt output for production.
FROM base AS build
COPY . .
RUN pnpm run build

# Production stage: ship only compiled Nitro output.
FROM node:22-alpine AS prod
WORKDIR /app/frontend

# Nitro server reads PORT/HOST (or NITRO_PORT/NITRO_HOST).
ENV PORT=3000 \
    HOST=0.0.0.0

# Copy only runtime output from build stage.
COPY --from=build /app/frontend/.output/ ./

EXPOSE 3000
CMD ["node", "/app/frontend/server/index.mjs"]
