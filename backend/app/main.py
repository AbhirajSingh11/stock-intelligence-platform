"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.dashboard import router as dashboard_router
from app.config import get_cors_origins
from app.schemas.system import HealthResponse, ServiceInfo

app = FastAPI(
    title="Stock Intelligence API",
    description="Backend services for stock research and portfolio intelligence.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)

app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/", response_model=ServiceInfo, tags=["system"])
def read_root() -> ServiceInfo:
    """Return basic service links for developers."""

    return ServiceInfo(
        name="Stock Intelligence API",
        docs="/docs",
        health="/health",
    )


@app.get("/health", response_model=HealthResponse, tags=["system"])
def read_health() -> HealthResponse:
    """Confirm that the API process is ready to serve requests."""

    return HealthResponse(
        status="ok",
        service="stock-intelligence-backend",
    )
