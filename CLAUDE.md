# CLAUDE.md - Marketing Agent System

## Project Overview

Multi-agent marketing campaign generation system. Users provide a product category URL and budget; AI agents generate a comprehensive marketing campaign including ad copy, social posts, email sequences, Google Ads structure, and analytics recommendations.

## Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, Celery, Playwright
- **Frontend:** React 18, TypeScript, Axios, Socket.IO
- **Infrastructure:** Docker Compose, PostgreSQL 16, Redis 7
- **AI:** Anthropic Claude (orchestration/research), Google Gemini 2.5 Flash (content generation)
- **Orchestration:** LangGraph for agent workflow

## Architecture

```
Frontend (React :3000) --> Backend (FastAPI :8000) --> Celery Worker
                                |                          |
                           PostgreSQL :5432           Redis :6379
```

The Overlord agent (`backend/app/agents/overlord.py`) orchestrates these agents:
1. Research Agent - Playwright web scraping + Claude analysis
2. Content Agent - Marketing copy generation
3. Social Media Agent - Instagram/Facebook/TikTok content
4. PPC Agent - Google Ads campaign structure
5. Meta Ads Agent - Meta advertising campaigns
6. CRM Agent - Email marketing with MJML templates
7. Analyst Agent - Budget allocation and ROI analysis

## Quick Setup

```bash
make setup          # Copy .env.example to .env, show instructions
# Edit backend/.env with your API keys
make dev            # Start all Docker services
make migrate        # Run Alembic migrations
```

## Required Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:
- `ANTHROPIC_API_KEY` - from https://console.anthropic.com/
- `GOOGLE_API_KEY` - from https://aistudio.google.com/app/apikey
- `SECRET_KEY` - generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL` - default: `postgresql://marketing_user:marketing_pass@localhost:5432/marketing_agents`

## Key File Locations

- **Entry point:** `backend/app/main.py`
- **Configuration:** `backend/app/core/config.py` (pydantic-settings, loads from .env)
- **Database models:** `backend/app/models/database.py` (6 tables)
- **Database connection:** `backend/app/core/database.py`
- **API routes:** `backend/app/api/routes.py`
- **Agents:** `backend/app/agents/` (overlord.py orchestrates all)
- **Agent state:** `backend/app/agents/state.py`
- **Celery config:** `backend/app/core/celery_app.py`
- **Celery tasks:** `backend/app/tasks/campaign_tasks.py`
- **Alembic config:** `backend/alembic.ini` (sqlalchemy.url overridden at runtime by env.py)
- **Alembic migrations:** `backend/alembic/versions/`
- **Frontend API client:** `frontend/src/services/api.ts`
- **Docker Compose:** `docker-compose.yml` (5 services)

## Database

- PostgreSQL 16, database `marketing_agents`, user `marketing_user`
- 6 tables: campaigns, agent_executions, assets, campaign_results, generated_articles, bi_reports
- UUID primary keys, JSONB columns for agent outputs
- Alembic for migrations; `init_db()` auto-creates tables in development mode
- Connect: `make psql`

## Common Commands

```bash
make dev              # Start all services
make stop             # Stop all services
make logs             # Follow all logs
make logs-backend     # Follow backend logs only
make migrate          # Run alembic upgrade head
make migrate-new MSG="description"  # Generate new migration
make clean            # Stop and remove volumes (fresh database)
make rebuild          # Rebuild all containers from scratch
make test             # Run backend pytest
make shell            # Bash into backend container
make psql             # Open psql session
make status           # Show service status
```

## Important Notes

- NEVER commit .env files containing real API keys
- `backend/.env.example` is safe to commit (contains only placeholders)
- Docker Compose uses `env_file` to load `backend/.env`, then overrides DB/Redis URLs with container hostnames
- pydantic-settings loads `env_file=".env"` relative to working directory (`/app` in Docker = `./backend` via volume mount)
- Alembic `env.py` overrides `sqlalchemy.url` from `settings.database_url` at runtime
- Dev mode calls `init_db()` on startup (auto-creates tables); production should use `alembic upgrade head`
