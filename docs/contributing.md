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
poetry install
cd src/frontend
npm install
cd ../..
```

4. **Create a branch:**

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Backend Development

```bash
cd src/backend
poetry run fastapi dev endpoints.py
```


### Frontend Development

```bash
cd src/frontend
npm run dev
```


### Documentation

```bash
# Start documentation server
poetry run mkdocs serve

# Build static documentation
poetry run mkdocs build
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Maximum line length: 120 characters
- Use descriptive variable names

Run linting before opening a PR:

```bash
poetry run ruff check .
```

### JavaScript/Vue (Frontend)

- Use ES6+ features
- Use Composition API for Vue components
- Use `<script setup>` syntax
- Keep components under 300 lines

**Format with Prettier (if configured):**

```bash
cd src/frontend
npm run format
```

## Testing

### Backend Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/backend

# Run specific test file
poetry run pytest tests/test_specific.py
```

### Frontend Tests

```bash
cd src/frontend
npm run lint
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
3. **Ensure all tests pass**: `poetry run pytest`
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
├── app.vue          # Root app component
├── components/      # Reusable Vue components
├── composables/     # Shared composables
├── pages/           # Route pages
├── plugins/         # Nuxt plugins
└── nuxt.config.ts   # Nuxt configuration
```

## Common Tasks

### Adding a New API Endpoint

1. Create/update endpoint in `src/backend/api/`
2. Add tests in `tests/`
3. Update API documentation
4. Verify endpoint in interactive docs: `http://localhost:8000/docs`

### Adding a New Vue Component

1. Create component in `src/frontend/components/`
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
- Ask in GitHub Discussions

## License

By contributing, you agree that your contributions will be licensed under the project's AGPL-3.0 license.
