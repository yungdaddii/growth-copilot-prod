# Growth Co-pilot 🚀

AI-powered revenue intelligence that finds $100K+ hidden opportunities in 60 seconds.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 🎯 What is Growth Co-pilot?

Growth Co-pilot is an AI revenue intelligence platform that analyzes any website and identifies high-impact revenue opportunities. Unlike generic AI tools, we provide:

- **Real Browser Testing**: Actually tests signup/checkout flows using Playwright
- **Traffic Intelligence**: Real visitor data and channel analysis via SimilarWeb API
- **Competitive Analysis**: Side-by-side comparison with top competitors
- **Revenue Quantification**: Every issue linked to specific dollar impact
- **60-Second Analysis**: Complete analysis in under a minute

## 🔥 Key Features

### Revenue Intelligence
- 🚨 Conversion blocker detection with monthly revenue impact
- 💰 Pricing strategy optimization
- 🛒 Checkout flow analysis
- 📝 Form optimization (signup, demo, contact)
- 🔒 Trust signal assessment

### Growth Opportunities
- 📈 Untapped acquisition channels
- 🎯 Keyword gap analysis
- 🤝 Partnership opportunities
- 📱 Viral mechanics identification
- 📊 Content strategy gaps

### Technical Analysis
- ⚡ Core Web Vitals & performance metrics
- 📱 Mobile responsiveness testing
- 🔍 SEO technical audit
- 🤖 AI search readiness (ChatGPT, Perplexity)
- 🌐 Browser compatibility

### Competitive Intelligence
- 📊 Market share analysis
- 🏃 Growth rate comparison
- 🔄 Feature gap identification
- 💡 Strategy insights
- 📈 Traffic source comparison
- **Frontend**: Next.js 14 with TypeScript
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Queue**: Celery
- **AI**: OpenAI GPT-4

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Google PageSpeed API key (optional but recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/growth-copilot.git
cd growth-copilot
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-your-openai-api-key
GOOGLE_PAGESPEED_API_KEY=your-pagespeed-key  # Optional
```

4. Start the application:
```bash
docker-compose up
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Usage

1. Open http://localhost:3000
2. Type `analyze domain.com` in the chat
3. Wait ~45-60 seconds for analysis
4. Explore insights with follow-up questions:
   - "show competitors"
   - "quick wins"
   - "mobile issues"
   - "tell me more"

## Architecture

```
growth-copilot/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints & WebSocket
│   │   ├── core/         # Business logic
│   │   ├── analyzers/    # Modular analyzers
│   │   ├── models/       # Database models
│   │   └── schemas/      # Pydantic schemas
│   └── tests/
├── frontend/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   ├── hooks/            # Custom hooks
│   └── store/            # Zustand state
└── docker-compose.yml
```

## Key Components

### Domain Analyzer
- Orchestrates multiple analysis modules
- Streams real-time updates via WebSocket
- Caches competitor data for performance

### Metrics Engine
- Calculates comparative metrics (no revenue estimates)
- Prioritizes issues by impact score
- Generates quick wins with implementation steps

### Chat Interface
- WebSocket-based real-time communication
- Progressive disclosure of insights
- Rich cards for data visualization

## API Endpoints

- `WS /ws/chat` - WebSocket for real-time chat
- `GET /api/analysis/{id}` - Get analysis results
- `GET /api/share/{slug}` - Get shared conversation
- `GET /health` - Health check

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `GOOGLE_PAGESPEED_API_KEY` | PageSpeed Insights API | Recommended |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | Application secret key | Yes |

## Deployment

### Railway/Render

1. Create PostgreSQL and Redis instances
2. Set environment variables
3. Deploy backend and frontend services
4. Configure custom domain

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set up Sentry for error monitoring
- [ ] Enable SSL/TLS
- [ ] Configure rate limiting
- [ ] Set up backup strategy
- [ ] Monitor API usage and costs

## Future Roadmap

1. **Phase 1**: Current MVP
2. **Phase 2**: Slack integration
3. **Phase 3**: Connect analytics platforms (GA, Mixpanel)
4. **Phase 4**: Real-time monitoring & alerts
5. **Phase 5**: Autonomous optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Proprietary - All rights reserved

## Support

For issues or questions, please open a GitHub issue.