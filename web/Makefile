.PHONY: install install-backend install-frontend ensure-venv dev backend frontend build test typecheck lint clean help

VENV_DIR := ../.venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
PYTHON_BOOTSTRAP := $(shell command -v python3 || command -v python)

# Default target
help:
	@echo "Gamalta Web Interface"
	@echo ""
	@echo "Usage:"
	@echo "  make install          Install all dependencies (backend + frontend)"
	@echo "  make install-backend  Install backend Python dependencies"
	@echo "  make install-frontend Install frontend npm dependencies"
	@echo "  make dev              Start both backend and frontend (requires 2 terminals)"
	@echo "  make backend          Start the backend server"
	@echo "  make frontend         Start the frontend dev server"
	@echo "  make build            Build frontend for production"
	@echo "  make clean            Remove build artifacts and caches"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make install"
	@echo "  2. In terminal 1: make backend"
	@echo "  3. In terminal 2: make frontend"
	@echo ""
	@echo "Then open http://localhost:5173 in your browser"

# Install all dependencies
install: install-backend install-frontend
	@echo "All dependencies installed successfully!"

# Create virtual environment if missing
ensure-venv:
	@if [ ! -x "$(PYTHON)" ]; then \
		echo "Creating virtual environment at $(VENV_DIR)"; \
		$(PYTHON_BOOTSTRAP) -m venv $(VENV_DIR); \
	fi

# Install backend dependencies
install-backend: ensure-venv
	$(PIP) install -e ..
	$(PIP) install -e ".[dev]"

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Start backend server
backend: ensure-venv
	$(PYTHON) -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080

# Start frontend dev server
frontend:
	cd frontend && npm run dev

# Convenience target that prints instructions for running both
dev:
	@echo "To run the full development environment, open two terminals:"
	@echo ""
	@echo "  Terminal 1: make backend"
	@echo "  Terminal 2: make frontend"
	@echo ""
	@echo "Backend will be at: http://localhost:8080"
	@echo "Frontend will be at: http://localhost:5173"
	@echo "API docs at: http://localhost:8080/docs"

# Build frontend for production
build:
	cd frontend && npm run build

# Run backend tests
test: ensure-venv
	$(PYTHON) -m pytest

# Type check backend
typecheck: ensure-venv
	$(PYTHON) -m mypy backend

# Lint frontend
lint:
	cd frontend && npm run lint

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist 2>/dev/null || true
	@echo "Cleaned build artifacts"
