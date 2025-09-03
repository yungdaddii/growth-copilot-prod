from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.config import settings
from app.database import engine, Base
from app.api import websocket, analysis, share, test_ws, test_conversation, test_enhanced, health

# Import auth module safely (in case User table doesn't exist yet)
try:
    from app.api import auth
    AUTH_AVAILABLE = True
except Exception as e:
    import structlog
    logger = structlog.get_logger()
    logger.warning(f"Auth module not available (migration may be needed): {e}")
    AUTH_AVAILABLE = False

# Import debug endpoint
try:
    from app.api import debug_firebase
    DEBUG_AVAILABLE = True
except:
    DEBUG_AVAILABLE = False
from app.utils.cache import init_redis
from app.integrations.google_ads import google_ads_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    deployment_version = "v5.1-REST-API-V18"
    logger.info("Starting Keelo.ai", version=settings.APP_VERSION, deployment=deployment_version)
    logger.info("Google Ads API Fix: Using POST for listAccessibleCustomers")
    logger.info("Docker cache issue fixed - fresh code deployed")
    
    # Initialize Redis
    await init_redis()
    
    # Create database tables (in production, use Alembic migrations)
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Keelo.ai")
    await engine.dispose()


# Initialize Sentry if DSN is provided
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "message": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


# Include routers
app.include_router(health.router)  # Health check routes
if AUTH_AVAILABLE:
    app.include_router(auth.router)  # Auth routes at /api/auth
if DEBUG_AVAILABLE:
    app.include_router(debug_firebase.router)  # Debug routes
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
app.include_router(test_ws.router, prefix="/ws", tags=["test"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(share.router, prefix="/api/share", tags=["share"])
app.include_router(test_conversation.router, prefix="/api/test", tags=["test"])
app.include_router(test_enhanced.router, prefix="/api/test", tags=["test-enhanced"])

# Include integration routers
from app.integrations import is_integration_enabled
# Temporarily always enable Google Ads router for testing
# if is_integration_enabled("google_ads"):
app.include_router(google_ads_router.router)
logger.info("Google Ads integration router registered")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "deployment": "v5.1-REST-API-V18",
        "google_ads_fix": "REST API v18 with GET for listAccessibleCustomers",
        "docker_fix": "Cache layer issue resolved", 
        "message": "AI that finds hidden revenue in 60 seconds"
    }