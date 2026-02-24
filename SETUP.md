# Marketing Agent System - Setup Guide

Quick start guide for getting the project running locally.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)
- Node.js 20+ (for local development without Docker)
- API Keys:
  - Anthropic API Key (Claude)
  - Google API Key (Gemini 2.5 Flash)

## Quick Start (Docker - Recommended)

### 1. Clone and setup

```bash
cd marketing-social-agent

# Copy env template and see instructions
make setup
```

### 2. Configure API keys

Edit `backend/.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GOOGLE_API_KEY=your-google-api-key-here
SECRET_KEY=generate-with-python3-c-import-secrets-print-secrets-token_hex-32
```

### 3. Start all services

```bash
make dev
```

### 4. Run database migrations

```bash
make migrate
```

### 5. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Verify everything is working

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

## Available Commands

Run `make help` to see all available commands.

| Command | Description |
|---------|-------------|
| `make setup` | Initial setup (copy env template) |
| `make dev` | Start all Docker services |
| `make stop` | Stop all services |
| `make logs` | Follow all service logs |
| `make logs-backend` | Follow backend logs only |
| `make migrate` | Run database migrations |
| `make migrate-new MSG="..."` | Generate new migration |
| `make psql` | Open PostgreSQL shell |
| `make shell` | Bash into backend container |
| `make test` | Run backend tests |
| `make status` | Show service status |
| `make clean` | Stop and remove all data |
| `make rebuild` | Full rebuild from scratch |

## Local Development (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start PostgreSQL and Redis locally (or use Docker just for these)
docker compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Environment Configuration

### Development (Local - Zero Cloud Costs!)

```bash
# Storage: Local filesystem
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage

# Database: Local PostgreSQL (Docker)
DATABASE_URL=postgresql://marketing_user:marketing_pass@localhost:5432/marketing_agents

# Redis: Local Redis (Docker)
REDIS_URL=redis://localhost:6379/0
```

### Production (AWS)

```bash
# Storage: AWS S3
STORAGE_TYPE=s3
S3_BUCKET=marketing-agents-production
AWS_REGION=eu-west-2
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Database: AWS RDS
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/marketing_agents

# Redis: AWS ElastiCache
REDIS_URL=redis://elasticache-endpoint:6379/0
```

## Getting Your API Keys

### Anthropic Claude API

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### Google Gemini API

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # or :3000, :5432, :6379

# Stop all containers and restart
make stop
make dev
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
make status

# Check logs
make logs-backend

# Restart with fresh database
make clean
make dev
make migrate
```

### Storage Permissions

```bash
# If you get permission errors with local storage
mkdir -p backend/storage
chmod 755 backend/storage
```

### Frontend Not Loading

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Project Structure

```
marketing-social-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Configuration & database
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── storage/         # Storage abstraction layer
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API clients
│   │   └── types/           # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
├── CLAUDE.md               # Claude Code project context
└── README.md               # Full specification
```

## Support

For issues or questions:
- Check the full specification in README.md
- Review the troubleshooting section above
- Check Docker logs: `make logs`
