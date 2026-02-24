.PHONY: help setup dev stop logs logs-backend logs-frontend logs-celery \
       migrate migrate-new migrate-history rebuild clean test shell psql \
       redis-cli check-env build status

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ====================
# Setup
# ====================

setup: ## Initial project setup - copy env template and prompt for configuration
	@echo "=== Marketing Agent System Setup ==="
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env; \
		echo "Created backend/.env from template."; \
		echo ""; \
		echo "IMPORTANT: Edit backend/.env and add your API keys:"; \
		echo "  - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)"; \
		echo "  - GOOGLE_API_KEY (get from https://aistudio.google.com/app/apikey)"; \
		echo "  - SECRET_KEY (generate with: python3 -c \"import secrets; print(secrets.token_hex(32))\")"; \
		echo ""; \
	else \
		echo "backend/.env already exists, skipping copy."; \
	fi
	@echo "Run 'make dev' to start all services."

check-env: ## Verify required environment variables are set in backend/.env
	@if [ ! -f backend/.env ]; then \
		echo "ERROR: backend/.env not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@grep -q "^ANTHROPIC_API_KEY=sk-ant-your-" backend/.env 2>/dev/null && \
		echo "WARNING: ANTHROPIC_API_KEY is still a placeholder" || true
	@grep -q "^GOOGLE_API_KEY=your-" backend/.env 2>/dev/null && \
		echo "WARNING: GOOGLE_API_KEY is still a placeholder" || true
	@grep -q "^SECRET_KEY=your-" backend/.env 2>/dev/null && \
		echo "WARNING: SECRET_KEY is still a placeholder" || true

# ====================
# Docker Operations
# ====================

build: ## Build all Docker images
	docker compose build

dev: check-env ## Start all services in development mode
	docker compose up -d
	@echo ""
	@echo "Services starting..."
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"
	@echo ""
	@echo "Run 'make logs' to follow logs, 'make status' to check health."

stop: ## Stop all services
	docker compose down

status: ## Show service status
	docker compose ps

logs: ## Follow logs for all services
	docker compose logs -f

logs-backend: ## Follow backend logs only
	docker compose logs -f backend

logs-frontend: ## Follow frontend logs only
	docker compose logs -f frontend

logs-celery: ## Follow Celery worker logs only
	docker compose logs -f celery-worker

# ====================
# Database
# ====================

migrate: ## Run database migrations (alembic upgrade head)
	docker compose exec backend alembic upgrade head

migrate-new: ## Generate a new migration (use MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make migrate-new MSG=\"your migration description\""; \
		exit 1; \
	fi
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

migrate-history: ## Show migration history
	docker compose exec backend alembic history --verbose

psql: ## Open PostgreSQL shell
	docker compose exec postgres psql -U marketing_user -d marketing_agents

# ====================
# Development
# ====================

shell: ## Open bash shell in backend container
	docker compose exec backend bash

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli

test: ## Run backend tests
	docker compose exec backend pytest -v

# ====================
# Cleanup
# ====================

clean: ## Stop services and remove volumes (WARNING: deletes database data)
	docker compose down -v
	@echo "All services stopped and volumes removed."

rebuild: ## Full rebuild - stop, remove volumes, rebuild images, start
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d
	@echo "Full rebuild complete. Run 'make migrate' to set up database."
