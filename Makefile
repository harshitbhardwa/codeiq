.PHONY: help setup install test run docker-build docker-up docker-down clean

# Default target
help:
	@echo "AI Code Analysis Microservice - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Run initial setup script"
	@echo "  install        - Install Python dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run            - Run the application locally"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  lint           - Run linting"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-up      - Start services with Docker Compose"
	@echo "  docker-down    - Stop services"
	@echo "  docker-logs    - View logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          - Clean build artifacts"
	@echo "  clean-all      - Clean everything including Docker"

# Setup and Installation
setup:
	@echo "🚀 Running setup script..."
	python scripts/setup.py

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

install-dev: install
	@echo "🔧 Installing development dependencies..."
	pip install pytest pytest-cov black flake8

# Development
run:
	@echo "🏃 Running application..."
	python app.py

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	@echo "🔍 Running linting..."
	black src/ tests/ --check
	flake8 src/ tests/

# Docker Commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker-compose build

docker-up:
	@echo "🐳 Starting services..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

# Maintenance
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/*/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf *.egg-info/
	rm -rf dist/

clean-all: clean
	@echo "🧹 Cleaning Docker artifacts..."
	docker-compose down -v
	docker system prune -f
	rm -rf logs/
	rm -rf data/

# Database Commands
db-init:
	@echo "🗄️ Initializing database..."
	docker-compose exec db psql -U code_analysis_user -d code_analysis_db -f /docker-entrypoint-initdb.d/init-db.sql

db-reset:
	@echo "🗄️ Resetting database..."
	docker-compose down -v
	docker-compose up -d db
	sleep 5
	$(MAKE) db-init

# API Testing
test-api:
	@echo "🌐 Testing API endpoints..."
	@echo "Health check:"
	curl -s http://localhost:5000/health | python -m json.tool
	@echo ""
	@echo "Supported languages:"
	curl -s http://localhost:5000/api/v1/languages | python -m json.tool

# Development server with reload
dev:
	@echo "🔄 Starting development server with reload..."
	uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# Production server
prod:
	@echo "🚀 Starting production server..."
	uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4

# Security check
security-check:
	@echo "🔒 Running security checks..."
	safety check
	bandit -r src/

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	isort src/ tests/

# Type checking
type-check:
	@echo "🔍 Running type checks..."
	mypy src/

# Full development workflow
dev-setup: install-dev setup
	@echo "✅ Development environment ready!"

# Full test suite
test-full: lint type-check test-cov security-check
	@echo "✅ All tests passed!"

# Production deployment
deploy: docker-build docker-up
	@echo "🚀 Production deployment complete!"
	@echo "API available at: http://localhost:5000"
	@echo "Documentation at: http://localhost:5000/docs" 