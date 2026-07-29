"""FastAPI application entry point."""

from fastapi import FastAPI

from app.schemas import HealthResponse, ServiceInfo

app = FastAPI(
    title="Stock Intelligence API",
    description="Backend services for stock research and portfolio intelligence.",
    version="0.1.0",
)


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

