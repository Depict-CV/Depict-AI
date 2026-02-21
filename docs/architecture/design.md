# System Design

Depict AI is a web-based image annotation and dataset management platform for computer vision teams. It follows a **client-server architecture** with a clear separation between the frontend, backend API, ML inference layer, and object storage.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│          Nuxt 3 SPA  (Vue 3 + Tailwind CSS)             │
│   Authentication: Clerk  │  API calls: useApi composable│
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/JSON
                      ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend  (Python 3.12)            │
│  ┌───────────┐  ┌──────────┐  ┌───────────────────────┐ │
│  │  REST API │  │  Auth    │  │  ML Inference Router  │ │
│  │  Routers  │  │ (Clerk   │  │  (HuggingFace models) │ │
│  │           │  │  JWT)    │  │                       │ │
│  └─────┬─────┘  └──────────┘  └───────────────────────┘ │
│        │                                                 │
│  ┌─────▼──────────────────────────────────────────────┐  │
│  │          SQLite / PostgreSQL  (SQLModel ORM)       │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  MinIO Object Storage                   │
│          (S3-compatible – images & assets)              │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### Frontend (Nuxt 3)

- **Framework:** Nuxt 3 with Vue 3 Composition API
- **Styling:** Tailwind CSS
- **Auth:** Clerk (JWT-based)
- **Canvas:** Konva.js (annotation editor)
- **HTTP:** Nuxt `$fetch` wrapped in `useApi` composable
- **Routing:** File-based (Nuxt pages/)

### Backend (FastAPI)

- **Framework:** FastAPI (Python 3.12)
- **ORM:** SQLModel (Pydantic + SQLAlchemy)
- **Auth:** Clerk JWT verification via `deps.py`
- **Object Storage:** MinIO client (`minio_sync.py`)
- **ML:** HuggingFace Transformers / custom models (`ml/`)
- **Error Monitoring:** Sentry SDK

### Database

- **Development:** SQLite (auto-created on first run)
- **Production:** PostgreSQL (recommended)
- Schema managed by SQLModel (auto `CREATE TABLE` on startup)

### Object Storage — MinIO

MinIO stores all raw images and data files.  
Per-project credentials are stored in the `MinIOConfig` database table.  
The backend proxies pre-signed URLs to the frontend so credentials are never exposed.

### ML Inference Layer

Located in `src/ml/`. Provides:
- HuggingFace model wrappers (`hugging_face_models.py`)
- Inference endpoint exposed through the FastAPI `ml` router

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Nuxt 3 SPA | SSR not needed; simpler deployment for a tool application |
| SQLModel ORM | Single Pydantic model serves both API schema and DB table |
| Clerk for auth | Managed OAuth + JWT; avoids building auth from scratch |
| MinIO for storage | S3-compatible; self-hostable; per-project isolation |
| File-based routing | Reduces boilerplate; aligns with Nuxt conventions |
| Sentry integration | Production error observability with minimal setup |
