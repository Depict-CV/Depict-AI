# Environment name
CONDA_ENV = Depict-AI
PYTHON = python

# Poetry flags
POETRY_INSTALL = poetry install --no-root
POETRY_CONFIG = poetry config virtualenvs.create false --local

# Default target
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make del_env      : Delete the Conda environment"
	@echo "  make create_env   : Create Conda env and install packages with Poetry"
	@echo "  make activate     : Activate the Conda environment (interactive shell)"
	@echo "  make install      : Install Python dependencies with Poetry"
	@echo "  make test         : Run tests with pytest"
	@echo "  make clean        : Run pre-commit hooks and cleanup pycache"
	@echo "  make jupyter      : Launch Jupyter notebook/lab"
	@echo "  make rebuild      : Recreate env from scratch"

# Delete Conda environment
.PHONY: del_env
del_env:
	conda env remove -n $(CONDA_ENV) -y

# Create Conda environment
.PHONY: create_env
create_env:
	@echo "Creating Conda environment '$(CONDA_ENV)'..."
	conda create -n $(CONDA_ENV) python=3.12 -y
	@echo "Activating environment..."
	conda activate $(CONDA_ENV) && \
	echo "Configuring Poetry to use current environment..." && \
	$(POETRY_CONFIG) && \
	echo "Installing Python dependencies..." && \
	$(POETRY_INSTALL)

# Activate environment interactively
.PHONY: activate
activate:
	@echo "Activating Conda environment '$(CONDA_ENV)'..."
	conda activate $(CONDA_ENV) && exec $$SHELL

# Install or update dependencies with Poetry
.PHONY: install
install:
	$(POETRY_CONFIG)
	$(POETRY_INSTALL)

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	pytest

# Clean project (pre-commit + pycache)
.PHONY: clean
clean:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "Cleaning __pycache__ folders..."
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Rebuild environment from scratch
.PHONY: rebuild
rebuild: del_env create_env
	@echo "Environment rebuilt successfully!"
