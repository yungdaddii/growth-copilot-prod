#!/bin/bash

# Prepare clean repository for deployment
# This creates a deployment-ready version without sensitive data

set -e

echo "🚀 Preparing Growth Copilot for deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Create new clean directory
DEPLOY_DIR="growthcopilot-deploy"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${YELLOW}Creating clean deployment directory...${NC}"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy essential files only
echo -e "${YELLOW}Copying essential files...${NC}"

# Backend
mkdir -p $DEPLOY_DIR/backend
cp -r backend/app $DEPLOY_DIR/backend/
cp backend/requirements.txt $DEPLOY_DIR/backend/
cp backend/alembic.ini $DEPLOY_DIR/backend/
cp -r backend/migrations $DEPLOY_DIR/backend/

# Frontend
mkdir -p $DEPLOY_DIR/frontend
cp -r frontend/app $DEPLOY_DIR/frontend/
cp -r frontend/components $DEPLOY_DIR/frontend/
cp -r frontend/hooks $DEPLOY_DIR/frontend/
cp -r frontend/lib $DEPLOY_DIR/frontend/
cp -r frontend/store $DEPLOY_DIR/frontend/
cp -r frontend/types $DEPLOY_DIR/frontend/
cp frontend/package*.json $DEPLOY_DIR/frontend/
cp frontend/tsconfig.json $DEPLOY_DIR/frontend/
cp frontend/tailwind.config.js $DEPLOY_DIR/frontend/
cp frontend/next.config.js $DEPLOY_DIR/frontend/
cp frontend/next-env.d.ts $DEPLOY_DIR/frontend/

# Docker files
cp docker-compose.yml $DEPLOY_DIR/
cp -r nginx $DEPLOY_DIR/

# Create optimized Dockerfiles for Railway
cat > $DEPLOY_DIR/backend/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright with only Chromium
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8000}/health')"

# Start command
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
EOF

cat > $DEPLOY_DIR/frontend/Dockerfile <<'EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Create Railway.toml for multi-service deployment
cat > $DEPLOY_DIR/railway.toml <<'EOF'
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "always"

[[services]]
name = "backend"
root = "backend"
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[services.backend.healthcheck]
path = "/health"
interval = 30

[[services]]
name = "frontend"
root = "frontend"
buildCommand = "npm ci && npm run build"
startCommand = "npm start"

[services.frontend.healthcheck]
path = "/"
interval = 30

[[services]]
name = "worker"
root = "backend"
startCommand = "celery -A app.celery_config worker --loglevel=info"

[[plugins]]
name = "postgresql"

[[plugins]]
name = "redis"
EOF

# Create .env.example
cat > $DEPLOY_DIR/.env.example <<'EOF'
# Core Configuration
APP_NAME="Growth Co-pilot"
ENVIRONMENT=production
DEBUG=false

# Security (MUST CHANGE)
SECRET_KEY=generate-a-secure-random-key-here

# Database (Railway provides automatically)
DATABASE_URL=${DATABASE_URL}

# Redis (Railway provides automatically)
REDIS_URL=${REDIS_URL}

# Required API Keys
OPENAI_API_KEY=your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key

# Optional but recommended
GOOGLE_PAGESPEED_API_KEY=your-pagespeed-key
SENTRY_DSN=your-sentry-dsn

# Rate Limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_PERIOD=60

# Feature Flags (start conservative)
ENABLE_AUTH=false
ENABLE_PAYMENT=false
EOF

# Create deployment instructions
cat > $DEPLOY_DIR/DEPLOY_RAILWAY.md <<'EOF'
# Railway Deployment Guide

## Prerequisites
- Railway CLI installed: `npm i -g @railway/cli`
- GitHub account
- API keys ready

## Step 1: Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit"
gh repo create growthcopilot --public
git push -u origin main
```

## Step 2: Deploy to Railway
```bash
# Login to Railway
railway login

# Create new project
railway init

# Link GitHub repo
railway link

# Add services
railway add postgresql
railway add redis

# Set environment variables
railway variables set OPENAI_API_KEY=xxx
railway variables set CLAUDE_API_KEY=xxx
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Deploy
railway up
```

## Step 3: Verify Deployment
```bash
# Get your app URL
railway domain

# Check logs
railway logs

# Open in browser
railway open
```

## Troubleshooting

### WebSocket Issues
- Ensure CORS_ORIGINS includes your Railway domain
- Check that nginx config allows WebSocket upgrade headers

### Playwright Issues
- Ensure container has at least 2GB RAM
- May need to upgrade Railway plan for more resources

### Database Issues
- Run migrations: `railway run alembic upgrade head`
- Check connection string: `railway variables get DATABASE_URL`
EOF

# Create GitHub Actions workflow
mkdir -p $DEPLOY_DIR/.github/workflows
cat > $DEPLOY_DIR/.github/workflows/railway.yml <<'EOF'
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway
        run: npm i -g @railway/cli
      
      - name: Deploy
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
EOF

# Remove sensitive files
echo -e "${YELLOW}Removing sensitive files...${NC}"
rm -f $DEPLOY_DIR/.env
rm -f $DEPLOY_DIR/.env.production
rm -rf $DEPLOY_DIR/**/__pycache__
rm -rf $DEPLOY_DIR/**/.pytest_cache
find $DEPLOY_DIR -name "*.pyc" -delete
find $DEPLOY_DIR -name ".DS_Store" -delete

# Create .gitignore
cat > $DEPLOY_DIR/.gitignore <<'EOF'
# Environment
.env
.env.local
.env.production
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Node
node_modules/
.next/
out/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.coverage
.pytest_cache/
coverage/

# Deployment
*.tar
*.zip
EOF

echo -e "${GREEN}✅ Deployment directory created: $DEPLOY_DIR${NC}"
echo
echo "Next steps:"
echo "1. cd $DEPLOY_DIR"
echo "2. Review and update .env.example with your API keys"
echo "3. git init && git add ."
echo "4. git commit -m 'Initial deployment'"
echo "5. Create GitHub repo and push"
echo "6. Follow DEPLOY_RAILWAY.md instructions"