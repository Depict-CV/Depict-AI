
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

## Monitoring (Optional)

Self-host Sentry locally with Docker:

```bash
docker run -d --name sentry -p 9000:9000 sentry
```

Visit http://localhost:9000 to access the Sentry dashboard.

Create a project to get the local DSN (usually `http://<host>:9000/<project_id>`).
