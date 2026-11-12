.PHONY: help install test lint format format-check ci-local frontend backend worker

# Help command to display available commands
help:
	@echo "Available commands:"
	@echo "  install      - Install all dependencies"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  ci-local     - Run all CI checks locally"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && uv sync
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run tests
test:
	@echo "Running Django tests..."
	cd backend && uv run python manage.py test

# Run linting
lint:
	@echo "Running backend linting..."
	cd backend && uv run ruff check .
	@echo "Running frontend linting..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	cd backend && uv run ruff format .
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Check code formatting
format-check:
	@echo "Formatting backend code..."
	cd backend && uv run ruff format . --check
	@echo "Formatting frontend code..."
	cd frontend && npm run format:check

# Run all CI checks locally
ci-local:
	@echo "Running all CI checks locally..."
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) format-check

# Run frontend
frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Run backend
backend:
	@echo "Starting backend development server..."
	cd backend && uv run python manage.py runserver

# Run worker
worker:
	@echo "Starting Celery worker..."
	cd worker && uv run python -m worker.main