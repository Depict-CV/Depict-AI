# Production Deployment

This guide covers the recommended steps to deploy Depict AI in a production environment.

---

## Architecture Overview

A typical production deployment consists of:

```
Internet
   │
   ▼
Reverse Proxy (Nginx / Caddy / Traefik)
   ├── / ──────────► Frontend (Nuxt SSR or static)  :3000
   └── /api ────────► Backend (FastAPI via Gunicorn)  :8000
                             │
                        PostgreSQL  :5432
                             │
                        MinIO        :9000
```

---

## 1. Environment Variables

Create a `.env` file (never commit it to version control):

```env
# Backend
DATABASE_URL=postgresql://user:password@db:5432/depictai
SENTRY_DSN=https://your_sentry_dsn
FRONTEND_URL=https://app.yourdomain.com

# Frontend
VITE_CLERK_PUBLISHABLE_KEY=pk_live_...
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 2. Database

Switch from SQLite to **PostgreSQL** for production:

```python
# config.py
DATABASE_URL = os.environ["DATABASE_URL"]
```

Use a managed database (e.g., AWS RDS, Supabase, Railway) or a containerized PostgreSQL instance.

### Migrations

SQLModel auto-creates tables on startup. For schema migrations after the initial deployment, use **Alembic**:

```bash
alembic init alembic
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

## 3. Backend — Gunicorn + Uvicorn

Replace the `fastapi dev` command used in development with a production ASGI server:

```bash
gunicorn src.backend.endpoints:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  --bind 0.0.0.0:8000
```

Install the extra dependencies:

```bash
pip install gunicorn uvicorn[standard]
```

### Dockerfile.backend (production override)

```dockerfile
CMD ["gunicorn", "src.backend.endpoints:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "--bind", "0.0.0.0:8000"]
```

---

## 4. Frontend — Static Build

Build the Nuxt app for static hosting:

```bash
cd src/frontend
npm run build    # outputs to .output/
npm run preview  # test the production build locally
```

Serve `.output/public/` via a CDN (Netlify, Vercel, Cloudflare Pages) or Nginx.

---

## 5. CORS Configuration

In `src/backend/endpoints.py`, restrict CORS to your actual frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. MinIO

For production, use a dedicated MinIO instance or an S3-compatible cloud service (AWS S3, Cloudflare R2, Backblaze B2).

**Security checklist:**
- Enable TLS (`use_ssl: true` in `MinIOConfig`)
- Rotate access keys regularly
- Encrypt `secret_key` values at rest (currently stored in plaintext — see `tables.py` TODO)

---

## 7. Sentry

Set `SENTRY_DSN` in your environment to enable error reporting. Sentry is already initialized in `endpoints.py`:

```python
sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=True)
```

See the [Sentry Tutorial](../sentry.md) for full setup instructions.

---

## 8. Docker Compose (Production)

Create a `docker-compose.prod.yml` that overrides the development defaults:

```yaml
services:
  backend:
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SENTRY_DSN: ${SENTRY_DSN}
      FRONTEND_URL: ${FRONTEND_URL}
    command: >
      gunicorn src.backend.endpoints:app
      -k uvicorn.workers.UvicornWorker
      -w 4 --bind 0.0.0.0:8000

  frontend:
    environment:
      VITE_CLERK_PUBLISHABLE_KEY: ${VITE_CLERK_PUBLISHABLE_KEY}
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}
    command: node .output/server/index.mjs
```

Run with:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Security Checklist

- [ ] Replace `allow_origins=["*"]` with specific domain(s)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Encrypt MinIO `secret_key` values at rest
- [ ] Set strong, unique secrets for all environment variables
- [ ] Enable HTTPS on the reverse proxy
- [ ] Set up Sentry for error monitoring
- [ ] Configure automated database backups
