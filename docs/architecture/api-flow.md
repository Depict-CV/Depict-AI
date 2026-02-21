# API Flow

This document describes how requests flow between the Nuxt 3 frontend and the FastAPI backend.

---

## Authentication Flow

```
Browser                    Clerk (SaaS)              FastAPI Backend
   │                           │                           │
   │──── sign in ─────────────►│                           │
   │◄─── Clerk session + JWT ──│                           │
   │                                                       │
   │──── API request + Bearer <JWT> ──────────────────────►│
   │                                              verify JWT│
   │                                           (deps.py)   │
   │                                              look up   │
   │                                              user in DB│
   │◄─── JSON response ────────────────────────────────────│
```

1. The user authenticates via Clerk (OAuth or email/password).
2. Clerk issues a signed JWT for the session.
3. On every API call, `useApi.ts` calls `$clerk.session.getToken()` to get a fresh token.
4. The token is sent as `Authorization: Bearer <token>`.
5. `deps.py` on the backend verifies the token against Clerk's JWKS endpoint and resolves the `User` database record.

---

## REST API Routers

The FastAPI application (`endpoints.py`) mounts the following routers:

| Router | Prefix | Description |
|--------|--------|-------------|
| `users` | `/users` | User registration and profile |
| `projects` | `/projects` | CRUD for projects |
| `data` | `/data` | Image/video upload and listing |
| `annotations` | `/annotations` | Annotation CRUD and status transitions |
| `ml` | `/ml` | AI inference jobs |
| `images` | `/images` | Image serving and pre-signed URLs |
| `minio_sync` | `/minio` | MinIO bucket synchronization |
| `notifications` | `/notifications` | User notifications |
| `test_auth` | `/test-auth` | Auth debugging endpoint (dev only) |

Interactive API documentation is available at `http://localhost:8000/docs` when the backend is running.

---

## Common Request Patterns

### Listing Images with Filters

```
GET /data?project_id=3&status=to+review&skip=0&limit=20
Authorization: Bearer <token>
```

Response: paginated list of `Data` objects with annotation status.

---

### Creating an Annotation

```
POST /annotations
Authorization: Bearer <token>
Content-Type: application/json

{
  "data_id": 42,
  "status": "human annotation",
  "x1": 100, "y1": 150, "x2": 300, "y2": 400
}
```

---

### Running AI Inference

```
POST /ml/inference
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 3,
  "model": "yolos-tiny",
  "image_ids": [42, 43, 44]
}
```

The backend runs inference and stores results as `Annotation` rows with `status = "ml annotation"`.

---

### MinIO Sync

```
POST /minio/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "project_id": 3
}
```

The backend connects to the configured MinIO bucket, lists objects, and imports any new images into the `Data` table.

---

## CORS Policy

In development, all origins are allowed:

```python
allow_origins=["*"]
```

In production, restrict this to your frontend domain:

```python
allow_origins=["https://app.yourdomain.com"]
```

See [Deployment → Production](../deployment/production.md) for secure configuration guidance.

---

## Error Handling

| HTTP Status | Meaning |
|-------------|---------|
| `401 Unauthorized` | Missing or invalid JWT |
| `403 Forbidden` | Authenticated but insufficient permissions |
| `404 Not Found` | Resource does not exist |
| `422 Unprocessable Entity` | Request body validation error (Pydantic) |
| `500 Internal Server Error` | Unexpected server error (reported to Sentry) |
