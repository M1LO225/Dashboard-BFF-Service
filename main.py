from fastapi import FastAPI
from api.v1 import dashboard_router

app = FastAPI(
    title="Dashboard BFF Service",
    description="API service to aggregate and serve dashboard data for the frontend.",
    version="1.0.0"
)

# Include the router for the dashboard API
app.include_router(
    dashboard_router.router,
    tags=["Dashboards"]
)

@app.get("/health", tags=["Health Check"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}