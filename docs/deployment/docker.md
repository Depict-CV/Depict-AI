# Docker Setup

Depict AI ships with a `docker-compose.yml` that starts both the backend and frontend services with a single command.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin)
- A `.env` file (or environment variables) for Clerk keys and any other secrets

---

## Services

### `backend`

| Property | Value |
|----------|-------|
| Dockerfile | `Dockerfile.backend` |
| Base image | `python:3.12-slim` |
| Exposed port | `8000` |
| Entry command | `fastapi dev endpoints.py --host 0.0.0.0 --port 8000` |

The backend mounts the entire repository into `/app`, so code changes are reflected without rebuilding the image during development.

### `frontend`

| Property | Value |
|----------|-------|
| Dockerfile | `Dockerfile.frontend` |
| Base image | `node:20-alpine` |
| Exposed port | `3000` |
| Entry command | `npm run dev -- --host 0.0.0.0 --port 3000` |

The frontend mounts `src/frontend` into the container for hot-module reloading. `node_modules` is excluded from the mount via an anonymous volume to avoid conflicts between host and container installs.

---

## `docker-compose.yml`

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      FRONTEND_URL: "http://localhost:3000"
    volumes:
      - ./:/app

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: "http://localhost:8000"
    depends_on:
      - backend
    volumes:
      - ./src/frontend:/app/src/frontend
      - /app/src/frontend/node_modules
```

---

## Starting the Stack

```bash
docker compose up --build
```

| URL | Service |
|-----|---------|
| `http://localhost:3000` | Frontend (Nuxt) |
| `http://localhost:8000` | Backend API (FastAPI) |
| `http://localhost:8000/docs` | Interactive API docs (Swagger UI) |

---

## Environment Variables

Pass secrets via an `.env` file at the project root or via the `environment` key in `docker-compose.yml`.

| Variable | Service | Description |
|----------|---------|-------------|
| `VITE_CLERK_PUBLISHABLE_KEY` | frontend | Clerk publishable key |
| `VITE_API_BASE_URL` | frontend | Backend API base URL |
| `FRONTEND_URL` | backend | Allowed CORS origin |
| `SENTRY_DSN` | backend | Sentry error tracking DSN |

---

## Stopping the Stack

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```

---

## Rebuilding After Dependency Changes

After modifying `pyproject.toml` or `package.json`, force a rebuild:

```bash
docker compose up --build --force-recreate
```
