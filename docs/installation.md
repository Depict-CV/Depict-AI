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

See [Authentication Setup](USER_MANAGEMENT.md) for social login configuration.

## Verify Installation

### Start Backend Server

```bash
cd src/backend
poetry run fastapi dev endpoints.py
```

Backend will be available at: http://localhost:8000

API documentation at: http://localhost:8000/docs

### Start Frontend Server

```bash
cd src/frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Useful Commands

```bash
# Install dependencies
poetry install
cd src/frontend
npm install

# Run backend
cd ../backend
poetry run fastapi dev endpoints.py

# Run frontend
cd ../frontend
npm run dev

# Run tests
cd ../..
poetry run pytest

# Serve docs
poetry run mkdocs serve
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

If port 8000 or 3000 is already in use, you can change them:

**Backend:** Edit `uvicorn` command port
**Frontend:** Edit `nuxt.config.ts` or run `npm run dev -- --port <PORT>`

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Authentication Setup](USER_MANAGEMENT.md)
- [Backend Documentation](backend/overview.md)
- [Frontend Documentation](frontend/overview.md)
