# Base builder image with uv and the same Python version as runtime.
# Keeping distro + Python aligned avoids virtualenv interpreter path issues.
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder-base

# Build under backend directory so the resulting .venv stays project-local.
WORKDIR /app/backend

# Compile bytecode during install for faster startup.
# Use copy link mode because cache mount and working dir are on different filesystems.
# Disable managed Python downloads; we use the image's system Python.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Development dependency stage: includes dev groups (linters/debug tools).
FROM builder-base AS builder-dev
ENV UV_NO_DEV=0

# Install only dependencies first (without project code) for cache efficiency.
# Bind-mount lockfile + project metadata to avoid baking them into this layer.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy source and install the project itself.
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Production dependency stage: excludes development dependency groups.
FROM builder-base AS builder-prod
ENV UV_NO_DEV=1

# Same bind-mount dependency install pattern, but with dev dependencies excluded.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Runtime image without uv tooling, only Python + app virtualenv.
FROM python:3.13-slim-trixie AS runtime-base
WORKDIR /app/backend

# Ensure virtualenv binaries are first and logs are unbuffered.
ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Development runtime: root user is fine for local iteration.
FROM runtime-base AS dev
COPY --from=builder-dev /app/backend /app/backend

# Use auto-reload for local development.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production runtime: run as non-root for better container security.
FROM runtime-base AS prod
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --create-home app

COPY --from=builder-prod --chown=app:app /app/backend /app/backend
USER app

# No reload in production; use multiple workers instead.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
