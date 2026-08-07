"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.companies import router as companies_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.fundamentals import router as fundamentals_router
from app.clients.sec_edgar import SecEdgarClient, build_sec_http_client
from app.config import get_cors_origins, get_sec_settings
from app.exceptions import ApplicationError
from app.schemas.system import HealthResponse, ServiceInfo
from app.services.company_service import CompanyService
from app.services.fundamentals_service import FundamentalsService


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Create and close the shared SEC connection pool with the application."""

    settings = get_sec_settings()
    sec_http_client = None
    application.state.company_service = None
    application.state.fundamentals_service = None

    if settings.user_agent:
        sec_http_client = build_sec_http_client(settings)
        sec_client = SecEdgarClient(sec_http_client, settings)
        company_service = CompanyService(sec_client)
        application.state.company_service = company_service
        application.state.fundamentals_service = FundamentalsService(
            sec_client,
            company_service,
        )

    try:
        yield
    finally:
        if sec_http_client is not None:
            await sec_http_client.aclose()


app = FastAPI(
    title="Stock Intelligence API",
    description="Backend services for stock research and portfolio intelligence.",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)

app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(fundamentals_router, prefix="/api/v1")


@app.exception_handler(ApplicationError)
async def handle_application_error(
    _request: Request,
    error: ApplicationError,
) -> JSONResponse:
    """Return stable public errors without exposing upstream details."""

    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": {
                "code": error.code,
                "message": error.message,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _request: Request,
    _error: RequestValidationError,
) -> JSONResponse:
    """Normalize FastAPI parameter validation to the public error envelope."""

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "One or more request parameters are invalid.",
            }
        },
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
