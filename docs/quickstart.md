# Quick Start

Get Depict AI running in under 5 minutes!

## 1. Install Dependencies

```bash
# Install Python dependencies
poetry install

# Install frontend dependencies
cd src/frontend && npm install && cd ../..
```

## 2. Start the Application

### Start backend and frontend in separate terminals

**Terminal 1 - Backend:**
```bash
cd src/backend
poetry run fastapi dev endpoints.py
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend
npm run dev
```

## 3. Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 4. Create Your First User

### Option 1: Sign Up via UI

1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter:
   - Username
   - Email
   - Password (min 6 characters)
4. Click "Sign Up"

### Option 2: Using API Docs

1. Go to http://localhost:8000/docs
2. Find `POST /signup` endpoint
3. Click "Try it out"
4. Enter user details:
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "hashed_password": "password123",
  "permission": "edit & delete"
}
```
5. Execute

## 5. Log In

1. Go to http://localhost:3000
2. Enter your email and password
3. Click "Sign In"

## 6. Explore Features

### Create a Project

1. Click on "Projects" in the sidebar
2. Click "Create Project"
3. Enter project name and description
4. Start adding images!

### Upload Images

1. Select a project
2. Click "Upload" panel
3. Drag and drop images or click to browse
4. Images will be processed and added to your project

### Annotate Images

1. Click on an image in the gallery
2. Use annotation tools to label
3. Save annotations

## Next Steps

### Set Up OAuth2 (Optional)

Enable social login with Google, Microsoft, or GitHub:

- [Authentication Setup Guide](USER_MANAGEMENT.md)

### Explore Documentation

- [Backend API Reference](backend/api.md)
- [Frontend Components](frontend/components.md)
- [Database Schema](architecture/database.md)

### Run Tests

```bash
poetry run pytest
```

### View Documentation

```bash
poetry run mkdocs serve
# Then visit http://127.0.0.1:8000
```

## Common Commands

```bash
# Backend
cd src/backend
poetry run fastapi dev endpoints.py  # Start FastAPI server

cd ../..
poetry run pytest                     # Run tests

# Frontend  
cd src/frontend
npm run dev                            # Start Nuxt dev server

# Docs
cd ../..
poetry run mkdocs serve                # Start MkDocs server

# Maintenance
poetry run ruff check .                # Lint Python code
```

## Troubleshooting

**Can't log in?**
- Check backend logs for errors
- Verify user was created successfully
- Ensure JWT_SECRET_KEY is set in `.env`

**Images not uploading?**
- Check file size limits
- Verify image format (jpg, png, etc.)
- Check backend logs for errors

**Port conflicts?**
- Backend default: 8000
- Frontend default: 3000
- Change ports in config if needed

## Getting Help

- Check [Backend Documentation](backend/overview.md)
- Check [Frontend Documentation](frontend/overview.md)
- Review [API Docs](http://localhost:8000/docs) when server is running
