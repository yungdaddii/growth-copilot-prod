# Growth Co-pilot Project Structure

```
growth-copilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app with WebSocket
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database connection
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py
│   │   │   ├── analysis.py
│   │   │   └── benchmarks.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py
│   │   │   ├── analysis.py
│   │   │   └── message.py
│   │   ├── api/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── websocket.py
│   │   │   ├── analysis.py
│   │   │   └── share.py
│   │   ├── core/                # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py      # Main analysis orchestrator
│   │   │   ├── nlp.py           # GPT-4 integration
│   │   │   └── revenue.py       # Revenue calculations
│   │   ├── analyzers/           # Modular analyzers
│   │   │   ├── __init__.py
│   │   │   ├── performance.py   # PageSpeed API
│   │   │   ├── conversion.py    # Conversion analysis
│   │   │   ├── competitors.py   # Competitor comparison
│   │   │   ├── seo.py          # SEO & AI visibility
│   │   │   └── mobile.py        # Mobile experience
│   │   ├── utils/               # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── cache.py         # Redis caching
│   │   │   ├── queue.py         # Celery tasks
│   │   │   └── monitoring.py    # Sentry integration
│   │   └── migrations/          # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx             # Main chat interface
│   │   └── share/
│   │       └── [slug]/
│   │           └── page.tsx     # Shared conversation view
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── Message.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── analysis/
│   │   │   ├── RevenueCard.tsx
│   │   │   ├── CompetitorCard.tsx
│   │   │   └── QuickActions.tsx
│   │   └── ui/                  # Radix UI components
│   ├── lib/
│   │   ├── websocket.ts         # WebSocket client
│   │   ├── api.ts              # API client
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   └── useChat.ts
│   ├── store/
│   │   └── chat.ts              # Zustand store
│   ├── styles/
│   │   └── globals.css
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```