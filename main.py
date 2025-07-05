from fastapi import FastAPI
from api.v1 import dashboard_router
from core.config import settings
from infrastructure.database.connection import Base, engine_scan, engine_asset, engine_vuln, engine_risk
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# NOTE: In a real multi-database setup, you would NOT use Base.metadata.create_all here.
# Each service is responsible for its own database schema.
# This is just for local testing convenience if all models are in one DB.
# For production, ensure separate DBs are managed by their respective services.
# Base.metadata.create_all(bind=engine_scan)
# Base.metadata.create_all(bind=engine_asset)
# Base.metadata.create_all(bind=engine_vuln)
# Base.metadata.create_all(bind=engine_risk)

app = FastAPI(
    title="Dashboard BFF Service",
    description="Backend-for-Frontend service to aggregate and serve risk assessment data.",
    version="1.0.0"
)

# Include the router for version 1 of the dashboard API
app.include_router(dashboard_router.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/health", tags=["Health Check"])
def health_check():
    """Simple health check endpoint."""
    logger.info("Health check requested.")
    return {"status": "ok"}

# Optional: Add startup/shutdown events for Redis connection
@app.on_event("startup")
async def startup_event():
    logger.info("Dashboard BFF Service starting up...")
    # You might want to test Redis connection here
    pass

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Dashboard BFF Service shutting down.")
    # Close Redis connection if necessary (redis-py handles this well)
    pass