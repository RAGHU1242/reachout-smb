import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine
from app.models.base import Base

# Import all models so that Base.metadata knows about them
import app.models.models  # noqa

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.businesses import router as businesses_router
from app.api.v1.products import router as products_router
from app.api.v1.customers import router as customers_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.leads import router as leads_router
from app.api.v1.orders import router as orders_router
from app.api.v1.delivery_zones import router as delivery_router
from app.api.v1.followups import router as followups_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.webhooks_instagram import router as ig_webhook_router
from app.api.v1.webhooks_whatsapp import router as wa_webhook_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.simulator import router as simulator_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("reachout.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("ReachOut SMB backend initialized successfully.")
    yield
    await engine.dispose()
    logger.info("Database engine closed.")

app = FastAPI(
    title="ReachOut SMB API",
    description="AI Sales & Customer Assistant for WhatsApp and Instagram Businesses",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Root
@app.get("/")
async def root():
    return {
        "name": "ReachOut SMB Backend API",
        "version": "1.0.0",
        "status": "online",
        "channels": ["Instagram", "WhatsApp", "Mock"],
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Mount V1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(businesses_router, prefix=api_v1_prefix)
app.include_router(products_router, prefix=api_v1_prefix)
app.include_router(customers_router, prefix=api_v1_prefix)
app.include_router(conversations_router, prefix=api_v1_prefix)
app.include_router(leads_router, prefix=api_v1_prefix)
app.include_router(orders_router, prefix=api_v1_prefix)
app.include_router(delivery_router, prefix=api_v1_prefix)
app.include_router(followups_router, prefix=api_v1_prefix)
app.include_router(analytics_router, prefix=api_v1_prefix)
app.include_router(ig_webhook_router, prefix=api_v1_prefix)
app.include_router(wa_webhook_router, prefix=api_v1_prefix)
app.include_router(integrations_router, prefix=api_v1_prefix)
app.include_router(simulator_router, prefix=api_v1_prefix)
