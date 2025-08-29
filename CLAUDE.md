# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Growth Co-pilot is an AI-powered revenue intelligence tool that analyzes websites and identifies revenue opportunities. It consists of a FastAPI backend with WebSocket support and a Next.js frontend with real-time chat interface.

## Development Commands

### Start Application (Docker)
```bash
docker-compose up        # Start all services
docker-compose down       # Stop services
docker-compose logs -f    # View logs
```

### Alternative: Start with Make
```bash
make up      # Start all services with Docker
make down    # Stop Docker services
make dev     # Start development servers (mixed local/Docker)
make clean   # Clean up containers and volumes
```

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linting
npm run type-check   # TypeScript type checking
```

### Testing & Code Quality
```bash
# Backend
cd backend
pytest tests/        # Run tests
black .             # Format code
ruff check .        # Lint code
mypy .              # Type checking

# Frontend
cd frontend
npm run lint        # Lint code
npm run type-check  # TypeScript checking
```

### Database Operations
```bash
cd backend
alembic upgrade head                                    # Apply migrations
alembic revision --autogenerate -m "Description"       # Create new migration
```

## Architecture

### Backend Structure
- **app/api/** - WebSocket and REST endpoints
  - `websocket.py` - Main WebSocket handler for chat
  - `analysis.py` - Analysis result endpoints
  - `share.py` - Share functionality
  
- **app/core/** - Business logic
  - `analyzer.py` - Domain analysis orchestration
  - `metrics.py` - Metrics calculation engine
  - `nlp.py` - Natural language processing
  
- **app/analyzers/** - Modular analysis components
  - `performance.py` - PageSpeed metrics
  - `seo.py` - SEO analysis
  - `competitors.py` - Competitor comparison
  - `conversion.py` - Conversion optimization
  - `mobile.py` - Mobile responsiveness
  - `visual.py` - Visual analysis
  
- **app/models/** - SQLAlchemy database models
- **app/schemas/** - Pydantic validation schemas

### Frontend Structure
- **app/** - Next.js App Router pages
- **components/chat/** - Chat interface components
  - `ChatInterface.tsx` - Main chat container
  - `MessageList.tsx` - Message display
  - `MessageInput.tsx` - User input handling
  
- **hooks/useWebSocket.ts** - WebSocket connection management
- **store/chat.ts** - Zustand state management

## Key Implementation Details

### WebSocket Communication
The application uses WebSocket for real-time chat. Messages follow this flow:
1. Frontend connects to `ws://localhost:8000/ws/chat`
2. User sends analysis request via WebSocket
3. Backend streams updates in real-time during analysis
4. Results are progressively disclosed through chat interface

### Analysis Pipeline
1. Domain analyzer orchestrates multiple analysis modules
2. Each analyzer runs independently and streams updates
3. Results are cached in Redis for performance
4. Metrics engine calculates comparative scores
5. NLP generates conversational responses

### Environment Configuration
Required environment variables in `.env`:
- `OPENAI_API_KEY` - GPT-4 API access
- `GOOGLE_PAGESPEED_API_KEY` - PageSpeed Insights (optional but recommended)
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis cache connection
- `SECRET_KEY` - Application security key

### Service Dependencies
- PostgreSQL 15+ for data persistence
- Redis 7+ for caching and Celery broker
- Celery for background task processing
- OpenAI GPT-4 for AI analysis

## Running the Application

1. Ensure `.env` file has required API keys
2. Run `docker-compose up` to start all services
3. Access frontend at http://localhost:3000
4. Backend API docs at http://localhost:8000/docs

## Common Development Tasks

### Adding a New Analyzer
1. Create new module in `backend/app/analyzers/`
2. Implement analyzer class with `analyze()` method
3. Register in `backend/app/core/analyzer.py`
4. Add corresponding schema in `backend/app/schemas/`

### Modifying Chat Interface
1. Components are in `frontend/components/chat/`
2. WebSocket logic in `frontend/hooks/useWebSocket.ts`
3. State management in `frontend/store/chat.ts`
4. Message types defined in `frontend/types/chat.ts`

### Database Schema Changes
1. Modify models in `backend/app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`