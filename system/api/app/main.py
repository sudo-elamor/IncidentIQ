from fastapi import FastAPI # type: ignore
from prometheus_client import make_asgi_app

from app.api.health import router as health_router
from app.api.logs import router as logs_router

app = FastAPI(
    title="IncidentIQ API",
    description="API for IncidentIQ system",
    version="1.0.0"
)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.include_router(health_router, prefix="/health")
app.include_router(logs_router, prefix="/logs")
