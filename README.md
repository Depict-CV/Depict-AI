
# Depict AI

Image data tool for computer vision from raw images to model training/fine-tuning.

## Installation

### Prerequisites
- Python 3.12+
- Poetry
- Node.js & npm

### Setup

1. **Install Python dependencies:**
   ```bash
   poetry install
   ```

2. **Install frontend dependencies:**
   ```bash
   cd src/frontend
   npm install
   ```

## Quick Start

### Using Makefile

```bash
# Install all dependencies
make install

# Start backend server
make backend

# Start frontend (in another terminal)
make frontend

# Start documentation
make docs

# Run tests
make test

# Activate Poetry shell
make shell
```

### Manual Commands

**Backend (FastAPI):**
```bash
cd src/backend
poetry run fastapi dev endpoints.py
# or
poetry shell
fastapi dev endpoints.py
```

**Frontend (Vue.js):**
```bash
cd src/frontend
npm run dev
```

**Documentation:**
```bash
poetry run mkdocs serve
```


## Testing

Run tests with:
```bash
make test
# or
poetry run pytest
```


## API Documentation & Testing

Access the interactive API docs at: **http://127.0.0.1:8000/docs**

### Option 1: Testing Without Authentication (Development Only)

For quick testing and experimentation, you can disable authentication:

1. **Set environment variable:**
   ```bash
   # In your .env file or terminal
   DISABLE_AUTH=true
   ```

2. **Restart the backend server:**
   ```bash
   make backend
   # or
   cd src/backend
   poetry run fastapi dev endpoints.py
   ```

3. **Test endpoints:**
   - All endpoints will now work without authentication
   - A mock test user (`test_user`) with full access will be used automatically
   - No need to provide JWT tokens in the Authorize dialog

⚠️ **WARNING:** Only use `DISABLE_AUTH=true` in development! Never in production!

### Option 2: Testing With Authentication

1. **Sign in to the frontend:**
   - Navigate to [http://localhost:3000](http://localhost:3000)
   - Sign in with your Clerk account

2. **Get your authentication token:**
   - Open browser DevTools (F12)
   - Go to **Application** → **Cookies** → `localhost:3000`
   - Find and copy the value of `_clerk_db_jwt`

3. **Authorize in API docs:**
   - Go back to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Click the **"Authorize"** button (🔒 lock icon at top right)
   - Paste the JWT token in the **"Value"** field
   - Click **"Authorize"**, then **"Close"**

4. **Test endpoints:**
   - All protected endpoints will now work with your authenticated session
   - Try `GET /test/whoami` to verify authentication
   - Tokens expire after ~1 hour - re-authorize if you get 401 errors

### Alternative: Get Token via Console

You can also get the token directly from the browser console:

```javascript
// In the frontend (localhost:3000), open console and run:
const token = await window.$nuxt.$clerk.session.getToken()
console.log(token)
```

Copy the printed token and use it in the Authorize dialog.

## Monitoring (Optional)

Self-host Sentry locally with Docker:

```bash
docker run -d --name sentry -p 9000:9000 sentry
```

Visit http://localhost:9000 to access the Sentry dashboard.

Create a project to get the local DSN (usually `http://<host>:9000/<project_id>`).
