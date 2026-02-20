.PHONY: help build up down restart logs clean etl dbt-run dbt-test dbt-docs test lint format check-env

# Default target
help:
	@echo "======================================"
	@echo "Docker ETL Pipeline - Make Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Pipeline Commands:"
	@echo "  make etl            - Run ETL extraction and loading"
	@echo "  make dbt-run        - Run dbt transformations"
	@echo "  make dbt-test       - Run dbt tests"
	@echo "  make dbt-docs       - Generate and serve dbt documentation"
	@echo "  make pipeline       - Run complete pipeline (ETL + dbt)"
	@echo ""
	@echo "Development Commands:"
	@echo "  make test           - Run Python tests"
	@echo "  make lint           - Run linters (black, flake8, sqlfluff)"
	@echo "  make format         - Format Python code with black"
	@echo "  make logs           - Show logs from all services"
	@echo "  make clean          - Clean up containers and volumes"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-source      - Connect to source database"
	@echo "  make db-target      - Connect to target database"
	@echo "  make db-reset       - Reset all databases (WARNING: deletes data)"
	@echo ""

# Check if .env file exists
check-env:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo "Please update .env with your configuration."; \
		exit 1; \
	fi

# Build all Docker images
build: check-env
	@echo "Building Docker images..."
	docker-compose build

# Start all services
up: check-env
	@echo "Starting services..."
	docker-compose up -d source_db target_db airflow_db
	@echo "Waiting for databases to be healthy..."
	@sleep 10
	docker-compose up -d airflow-webserver airflow-scheduler
	@echo ""
	@echo "Services started!"
	@echo "Airflow UI: http://localhost:8080 (admin/admin)"
	@echo "Source DB: localhost:5433"
	@echo "Target DB: localhost:5434"

# Stop all services
down:
	@echo "Stopping services..."
	docker-compose down

# Restart all services
restart: down up

# Show logs from all services
logs:
	docker-compose logs -f

# Run ETL process
etl: check-env
	@echo "Running ETL process..."
	docker-compose --profile etl run --rm etl

# Run dbt transformations
dbt-run: check-env
	@echo "Running dbt transformations..."
	docker-compose --profile dbt run --rm dbt dbt run --profiles-dir .

# Run dbt tests
dbt-test: check-env
	@echo "Running dbt tests..."
	docker-compose --profile dbt run --rm dbt dbt test --profiles-dir .

# Generate and serve dbt documentation
dbt-docs: check-env
	@echo "Generating dbt documentation..."
	docker-compose --profile dbt run --rm dbt dbt docs generate --profiles-dir .
	docker-compose --profile dbt run --rm dbt dbt docs serve --profiles-dir .

# Run complete pipeline
pipeline: etl dbt-run dbt-test
	@echo ""
	@echo "✅ Pipeline completed successfully!"

# Run Python tests
test:
	@echo "Running Python tests..."
	cd etl && pytest tests/ -v --cov=src --cov-report=term-missing

# Run linters
lint:
	@echo "Running linters..."
	@echo "1. Black (Python formatter check)..."
	black --check etl/src/ || true
	@echo ""
	@echo "2. Flake8 (Python linter)..."
	flake8 etl/src/ --max-line-length=100 --exclude=__pycache__ || true
	@echo ""
	@echo "3. SQLFluff (SQL linter)..."
	sqlfluff lint dbt/models/ --dialect postgres || true

# Format Python code
format:
	@echo "Formatting Python code with black..."
	black etl/src/

# Connect to source database
db-source: check-env
	@echo "Connecting to source database..."
	docker-compose exec source_db psql -U source_user -d source_oltp

# Connect to target database
db-target: check-env
	@echo "Connecting to target database..."
	docker-compose exec target_db psql -U target_user -d target_warehouse

# Reset all databases (WARNING: deletes all data)
db-reset:
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Resetting databases..."; \
		docker-compose down -v; \
		docker volume rm -f source_db_data target_db_data airflow_db_data; \
		make up; \
		echo "Databases reset complete."; \
	else \
		echo "Reset cancelled."; \
	fi

# Clean up everything
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "Cleanup complete!"

# Development setup (first time)
setup: check-env build up
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Wait 30 seconds for Airflow to initialize"
	@echo "2. Run 'make etl' to test ETL"
	@echo "3. Run 'make dbt-run' to run transformations"
	@echo "4. Access Airflow at http://localhost:8080"
	@echo ""
