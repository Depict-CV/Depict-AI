# API Reference

Complete REST API reference for Depict AI backend.

!!! tip "Interactive Documentation"
    For interactive API testing, visit http://localhost:8000/docs when the backend is running.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Get Token

**Endpoint:** `POST /token`

OAuth2 token endpoint for authentication.

**Request:**
```http
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## Authentication Endpoints

### Sign Up

**Endpoint:** `POST /signup`

Create a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "hashed_password": "secure_password",
  "permission": "edit"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "permission": "edit"
}
```

### Login

**Endpoint:** `POST /login`

Login with email and password.

**Request Body:**
```json
{
  "username": "john@example.com",
  "hashed_password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "johndoe"
}
```

### Get Current User

**Endpoint:** `GET /me`

Get authenticated user's information.

**Headers:** Requires authentication

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "permission": "edit"
}
```

---

## OAuth2 Endpoints

### Google Login

**Endpoint:** `GET /auth/google/login`

Initiates Google OAuth2 flow.

**Response:** Redirects to Google login page

### Google Callback

**Endpoint:** `GET /auth/google/callback`

Google OAuth2 callback (handled automatically).

### Microsoft Login

**Endpoint:** `GET /auth/microsoft/login`

Initiates Microsoft OAuth2 flow.

### GitHub Login

**Endpoint:** `GET /auth/github/login`

Initiates GitHub OAuth2 flow.

---

## Project Endpoints

### List My Projects

**Endpoint:** `GET /projects/my-projects`

Get all projects for the authenticated user.

**Headers:** Requires authentication

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Dataset",
    "description": "Image classification dataset",
    "owner_id": 1,
    "created_at": "2025-12-01T10:00:00",
    "members": 3,
    "images": 150,
    "role": "admin"
  }
]
```

### Create Project

**Endpoint:** `POST /projects/`

Create a new project.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Optional description"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "New Project",
  "description": "Optional description",
  "owner_id": 1,
  "created_at": "2025-12-02T15:30:00"
}
```

### Join Project

**Endpoint:** `POST /projects/join/{project_code}`

Join an existing project by code or name.

**Headers:** Requires authentication

**Parameters:**
- `project_code` (path) - Project name or invite code

**Response:**
```json
{
  "message": "Successfully joined project",
  "project_id": 3
}
```

### Get Project

**Endpoint:** `GET /projects/{project_id}`

Get project details.

**Headers:** Requires authentication

**Parameters:**
- `project_id` (path) - Project ID

**Response:**
```json
{
  "id": 1,
  "name": "My Dataset",
  "description": "Image classification dataset",
  "owner_id": 1,
  "users": [
    {"id": 1, "username": "johndoe", "role": "admin"},
    {"id": 2, "username": "janedoe", "role": "editor"}
  ]
}
```

### Update Project

**Endpoint:** `PUT /projects/{project_id}`

Update project information.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### Delete Project

**Endpoint:** `DELETE /projects/{project_id}`

Delete a project (owner only).

**Headers:** Requires authentication

---

## Data (Image) Endpoints

### Upload Image

**Endpoint:** `POST /data/`

Upload a new image to a project.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "type": "image",
  "location": "s3://bucket/image.jpg",
  "project_id": 1
}
```

**Response:**
```json
{
  "id": 100,
  "type": "image",
  "location": "s3://bucket/image.jpg",
  "author_id": 1,
  "project_id": 1,
  "creation_date": "2025-12-02T16:00:00"
}
```

### Batch Upload

**Endpoint:** `POST /data/batch`

Upload multiple images at once.

**Headers:** Requires authentication

**Request Body:**
```json
[
  {
    "type": "image",
    "location": "s3://bucket/img1.jpg",
    "project_id": 1
  },
  {
    "type": "image",
    "location": "s3://bucket/img2.jpg",
    "project_id": 1
  }
]
```

### Get Unlabeled Images

**Endpoint:** `GET /data/non-labeled?project_id={project_id}`

Get images without annotations.

**Headers:** Requires authentication

**Query Parameters:**
- `project_id` - Project ID

**Response:**
```json
[
  {
    "id": 105,
    "type": "image",
    "location": "s3://bucket/img3.jpg",
    "project_id": 1
  }
]
```

---

## Annotation Endpoints

### Create Annotation

**Endpoint:** `POST /annotations/`

Create a new annotation.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "status": "ml annotation",
  "label": "cat",
  "annotation_score": 0.95,
  "data_id": 100,
  "project_id": 1
}
```

### Get Annotation

**Endpoint:** `GET /annotations/{annotation_id}`

Get annotation details.

### Update Annotation

**Endpoint:** `PUT /annotations/{annotation_id}`

Update an existing annotation.

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting implemented. For production, consider adding rate limiting middleware.

## Pagination

For endpoints returning lists, pagination will be added in future versions:

```
?page=1&size=50
```

## Next Steps

- [Database Schema](../architecture/database.md) - Schema reference
- [User Management](../USER_MANAGEMENT.md) - Auth implementation
- [Contributing](../contributing.md) - Testing and development guide
