# Backend Overview

The Depict AI backend is built with **FastAPI**, providing a high-performance REST API for managing computer vision datasets, annotations, and user authentication.

## Architecture

```
src/backend/
├── api/
│   ├── __init__.py
│   ├── annotations.py    # Annotation CRUD endpoints
│   ├── auth.py          # Authentication & JWT
│   ├── data.py          # Data/image management
│   ├── deps.py          # FastAPI dependencies
│   ├── ml.py            # ML model endpoints
│   ├── oauth2.py        # Social login (Google, Microsoft, GitHub)
│   ├── projects.py      # Project management
│   └── users.py         # User management
├── db/
│   ├── database.py      # Database connection & initialization
│   └── tables.py        # SQLModel table definitions
└── endpoints.py         # Main FastAPI app & router registration
```

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLModel** - SQL databases with Pydantic models
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **httpx** - Async HTTP client for OAuth2
- **Sentry SDK** - Error monitoring

## Key Features

### 🔐 Authentication

- **Local Auth**: Email/password with SHA-256 hashing
- **OAuth2**: Social login with Google, Microsoft, GitHub
- **JWT Tokens**: Secure stateless authentication
- **Role-Based Access**: User permissions (view, edit, delete, certify)

### 📊 Data Management

- **Projects**: Organize images into projects
- **Images**: Upload, store, and manage image data
- **Annotations**: Create, read, update annotations
- **ML Integration**: Run ML models on images

### 🔗 API Design

- **RESTful**: Standard HTTP methods (GET, POST, PUT, DELETE)
- **OpenAPI**: Auto-generated API documentation at `/docs`
- **Async**: Non-blocking I/O for high performance
- **CORS**: Configured for frontend integration

## Database Schema

See [Database Schema](../architecture/database.md) for complete schema details.

Main entities:
- **User** - Authentication and profile
- **Project** - Image collection container
- **Data** - Image/video metadata
- **Annotation** - Labels, boxes, masks
- **ProjectUserLink** - Many-to-many user-project relation

## API Endpoints

### Authentication
- `POST /signup` - Create new user
- `POST /login` - Email/password login
- `POST /token` - OAuth2 token endpoint
- `GET /me` - Get current user info

### OAuth2
- `GET /auth/{provider}/login` - Initiate OAuth2 flow
- `GET /auth/{provider}/callback` - OAuth2 callback

### Projects
- `GET /projects/my-projects` - List user's projects
- `POST /projects/` - Create new project
- `POST /projects/join/{code}` - Join project by code
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Data (Images)
- `POST /data/` - Upload image
- `POST /data/batch` - Batch upload
- `GET /data/non-labeled` - Get unlabeled images

### Annotations
- `POST /annotations/` - Create annotation
- `GET /annotations/{id}` - Get annotation
- `PUT /annotations/{id}` - Update annotation

See [API Reference](api.md) for complete endpoint documentation.

## Running the Backend

### Development Mode

```bash
# Using Makefile
make backend

# Using Poetry
cd src/backend
poetry run fastapi dev endpoints.py

# Using uvicorn directly
poetry run uvicorn endpoints:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
poetry run fastapi run endpoints.py
```

## Environment Configuration

Create `.env` file in project root:

```env
# API
API_URL="http://localhost:8000"

# JWT
JWT_SECRET_KEY="your-secret-key-here"

# OAuth2 (optional)
GOOGLE_CLIENT_ID="..."
GOOGLE_CLIENT_SECRET="..."
MICROSOFT_CLIENT_ID="..."
MICROSOFT_CLIENT_SECRET="..."
GITHUB_CLIENT_ID="..."
GITHUB_CLIENT_SECRET="..."

# Monitoring (optional)
SENTRY_DSN="..."
```

## Testing

See [Testing](../contributing.md) for testing strategies.

```bash
# Run all tests
make test

# Run with coverage
poetry run pytest --cov=src/backend
```

## Next Steps

- [API Reference](api.md) - Complete API documentation
- [Database Schema](../architecture/database.md) - Schema details
- [User Management](../USER_MANAGEMENT.md) - Auth implementation details
- [Contributing](../contributing.md) - Testing guide
