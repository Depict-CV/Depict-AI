# Installation

## Prerequisites

Before installing Depict AI, ensure you have:

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - Python dependency manager ([Install Poetry](https://python-poetry.org/docs/#installation))
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm** - Comes with Node.js

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Depict-CV/Depict-AI.git
cd Depict-AI
```

### 2. Install Backend Dependencies

Using Poetry:

```bash
poetry install
```

This will create a virtual environment and install all Python dependencies including:
- FastAPI
- SQLModel
- httpx (for OAuth2)
- python-jose (for JWT)
- And more...

### 3. Install Frontend Dependencies

```bash
cd src/frontend
npm install
cd ../..
```

### 4. Configure Environment Variables

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` to set:
- JWT secret key
- OAuth2 credentials (optional)
- Database URL
- Sentry DSN (optional)

See [OAuth2 Setup](oauth2_setup.md) for social login configuration.

## Verify Installation

### Start Backend Server

```bash
# Using Makefile
make backend

# Or manually
cd src/backend
poetry run fastapi dev endpoints.py
```

Backend will be available at: http://localhost:8000

API documentation at: http://localhost:8000/docs

### Start Frontend Server

```bash
# Using Makefile (in another terminal)
make frontend

# Or manually
cd src/frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

## Using Makefile Commands

For convenience, use the provided Makefile:

```bash
# Install all dependencies
make install

# Start backend
make backend

# Start frontend (in another terminal)
make frontend

# Run tests
make test

# Clean cache
make clean

# Rebuild environment
make rebuild
```

## Troubleshooting

### Poetry Command Not Found

Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add to PATH (check Poetry documentation for your OS).

### Python Version Issues

Check your Python version:
```bash
python --version  # Should be 3.12+
```

Set Poetry to use specific Python:
```bash
poetry env use python3.12
```

### Node/npm Issues

Ensure Node.js 18+ is installed:
```bash
node --version
npm --version
```

Clear npm cache if needed:
```bash
npm cache clean --force
```

### Port Already in Use

If port 8000 or 5173 is already in use, you can change them:

**Backend:** Edit `uvicorn` command port
**Frontend:** Edit `vite.config.js` or use `--port` flag

## Next Steps

- [Quick Start Guide](quickstart.md)
- [OAuth2 Setup](oauth2_setup.md)
- [Backend Documentation](backend/overview.md)
- [Frontend Documentation](frontend/overview.md)
