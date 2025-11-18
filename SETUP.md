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

### 1. Clone the repository

```bash
cd marketing-social-agent
```

### 2. Set up environment variables

```bash
# Copy the example environment file
cp backend/.env.example backend/.env.development

# Edit the file and add your API keys
# Required:
# - ANTHROPIC_API_KEY
# - GOOGLE_API_KEY
```

Edit `backend/.env.development` and set your API keys:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. Start all services

```bash
# Start PostgreSQL, Redis, Backend, and Frontend
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Verify everything is working

```bash
# Check service health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}
```

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
cp .env.example .env.development
# Edit .env.development with your API keys

# Start PostgreSQL and Redis locally (or use Docker just for these)
docker-compose up -d postgres redis

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
docker-compose down
docker-compose up -d
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
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

## Useful Commands

```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Rebuild containers
docker-compose build --no-cache

# Access PostgreSQL directly
docker-compose exec postgres psql -U marketing_user -d marketing_agents

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Next Steps

Once the system is running:

1. **Phase 1 (Current)**: Implement core agents
   - Research Agent (web scraping & analysis)
   - Content Agent (with Gemini 2.5 Flash)
   - Basic UI for input and results

2. **Test the API**:
   ```bash
   # Create a test campaign
   curl -X POST http://localhost:8000/api/campaigns \
     -H "Content-Type: application/json" \
     -d '{
       "category_url": "https://example.com/baby-sleepsuits",
       "budget": 5000
     }'
   ```

3. **Access API Documentation**: http://localhost:8000/docs

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
└── README.md               # Full specification
```

## Support

For issues or questions:
- Check the full specification in README.md
- Review the troubleshooting section above
- Check Docker logs: `docker-compose logs -f`
