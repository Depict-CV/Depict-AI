# Contributing to Depict AI

Thank you for your interest in contributing to Depict AI! This guide will help you get started.

## Code of Conduct

Please read and follow our [Code of Conduct](code_of_conduct.md).

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry
- Node.js 18+
- Git

### Setup Steps

1. **Fork the repository**

2. **Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/Depict-AI.git
cd Depict-AI
```

3. **Install dependencies:**
```bash
make install
```

4. **Create a branch:**
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Backend Development

```bash
# Start backend server
make backend

# Run tests
make test

# Activate Poetry shell
make shell
```

### Frontend Development

```bash
# Start frontend server
make frontend

# Install new package
cd src/frontend
npm install <package-name>
```

### Documentation

```bash
# Start documentation server
make docs

# Generate API docs
poetry run python scripts/generate_api_docs.py
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 120 characters
- Use descriptive variable names

**Format with Ruff:**
```bash
poetry run ruff format .
poetry run ruff check .
```

### JavaScript/Vue (Frontend)

- Use ES6+ features
- Use Composition API for Vue components
- Use `<script setup>` syntax
- Keep components under 300 lines

**Format with Prettier (if configured):**
```bash
npm run format
```

## Testing

### Backend Tests

```bash
# Run all tests
make test

# Run with coverage
poetry run pytest --cov=src/backend

# Run specific test file
poetry run pytest tests/test_specific.py
```

### Frontend Tests

```bash
cd src/frontend
npm run test
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add GitHub OAuth2 support
fix(projects): resolve duplicate project creation bug
docs(api): update endpoint documentation
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**: `make test`
4. **Update CHANGELOG.md** (if applicable)
5. **Create pull request** with clear description

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] PR description explains changes

## Project Structure

### Backend Structure

```
src/backend/
├── api/              # API endpoints
│   ├── auth.py      # Authentication
│   ├── projects.py  # Projects
│   └── ...
├── db/              # Database
│   ├── database.py  # Connection
│   └── tables.py    # Models
└── endpoints.py     # Main app
```

### Frontend Structure

```
src/frontend/
├── src/
│   ├── components/  # Vue components
│   ├── pages/       # Page components
│   └── App.vue      # Root component
└── vite.config.js   # Build config
```

## Common Tasks

### Adding a New API Endpoint

1. Create/update endpoint in `src/backend/api/`
2. Add tests in `tests/`
3. Update API documentation
4. Generate OpenAPI spec: `python scripts/generate_api_docs.py`

### Adding a New Vue Component

1. Create component in `src/frontend/src/components/`
2. Use `<script setup>` syntax
3. Add scoped styles
4. Document props and emits
5. Update component docs

### Adding Database Model

1. Add model to `src/backend/db/tables.py`
2. Update database initialization
3. Run migrations (if using Alembic)
4. Update model documentation

## Environment Variables

Create `.env` file (never commit this!):

```env
JWT_SECRET_KEY="your-secret-here"
GOOGLE_CLIENT_ID="..."
GITHUB_CLIENT_ID="..."
```

## Database Changes

When modifying database schema:

1. Update models in `tables.py`
2. Test with fresh database
3. Document schema changes
4. Consider migration strategy

## Need Help?

- Check existing [documentation](index.md)
- Open an [issue](https://github.com/Depict-CV/Depict-AI/issues)
- Ask in discussions

## License

By contributing, you agree that your contributions will be licensed under the project's AGPL-3.0 license.
