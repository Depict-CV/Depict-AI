# Project name
PROJECT = Depict-AI
PYTHON = python

# Poetry commands
POETRY = poetry
POETRY_INSTALL = $(POETRY) install
POETRY_RUN = $(POETRY) run

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install      : Install Python dependencies with Poetry"
	@echo "  make env_activate : Activate Poetry virtual environment"
	@echo "  make test         : Run tests with pytest"
	@echo "  make backend      : Start FastAPI backend server"
	@echo "  make frontend     : Start Vue.js frontend dev server"
	@echo "  make frontend-nuxt: Start Nuxt 3 frontend dev server"
	@echo "  make build-nuxt   : Build Nuxt 3 for production"
	@echo "  make docs         : Start documentation server with mkdocs"
	@echo "  make clean        : Cleanup pycache and build artifacts"
	@echo "  make rebuild      : Remove venv and reinstall dependencies"

# Install or update dependencies with Poetry
.PHONY: install
install:
	@echo "Installing dependencies with Poetry..."
	$(POETRY_INSTALL)

# Activate Poetry env activate
.PHONY: env_activate
env_activate:
	@echo "Activating Poetry virtual environment..."
	$(POETRY) env activate

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(POETRY_RUN) pytest

# Start backend server
.PHONY: backend
backend:
	@echo "Starting FastAPI backend server..."
	cd src/backend && $(POETRY_RUN) fastapi dev endpoints.py

# Start frontend dev server
.PHONY: frontend
frontend:
	@echo "Starting Vue.js frontend dev server..."
	cd src/frontend && npm run dev

# Start Nuxt 3 frontend dev server
.PHONY: frontend-nuxt
frontend-nuxt:
	@echo "Starting Nuxt 3 frontend dev server..."
	cd src/frontend_nuxt && npm run dev

# Build Nuxt 3 for production
.PHONY: build-nuxt
build-nuxt:
	@echo "Building Nuxt 3 for production..."
	cd src/frontend_nuxt && npm run build

# Start documentation server
.PHONY: docs
docs:
	@echo "Starting documentation server..."
	cd docs && $(POETRY_RUN) mkdocs serve

# Clean project (pycache + build artifacts)
.PHONY: clean
clean:
	@echo "Cleaning __pycache__ folders..."
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaning .pyc files..."
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage 2>/dev/null || true
	# poetry run pre-commit run --all-files
# Remove virtual environment and reinstall
.PHONY: rebuild
rebuild:
	@echo "Removing Poetry virtual environment..."
	$(POETRY) env remove --all || true
	@echo "Reinstalling dependencies..."
	$(POETRY_INSTALL)
	@echo "Environment rebuilt successfully!"
