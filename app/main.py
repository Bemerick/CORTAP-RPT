"""
CORTAP-RPT FastAPI Application.

Main application module that creates the FastAPI app instance,
configures middleware, and includes route handlers.
"""

from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.config import settings
from app.api.v1.api import api_v1_router
from app.exceptions import (
    CORTAPError,
    RiskuityAPIError,
    DocumentGenerationError,
    ValidationError,
    S3StorageError,
)


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    application = FastAPI(
        title=settings.project_name,
        description="Document generation microservice for CORTAP audit reports",
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if settings.environment != "production" else None,
        docs_url=f"{settings.api_v1_prefix}/docs" if settings.environment != "production" else None,
        redoc_url=f"{settings.api_v1_prefix}/redoc" if settings.environment != "production" else None,
    )

    # Configure CORS
    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

    return application


# Create FastAPI app instance
app = create_application()

# Include API v1 router
app.include_router(api_v1_router)


# Exception Handlers
@app.exception_handler(CORTAPError)
async def cortap_error_handler(request: Request, exc: CORTAPError) -> JSONResponse:
    """
    Handle custom CORTAP exceptions.

    Maps exception types to appropriate HTTP status codes:
    - ValidationError -> 400 Bad Request
    - RiskuityAPIError -> 502 Bad Gateway
    - DocumentGenerationError -> 500 Internal Server Error
    - S3StorageError -> 500 Internal Server Error
    - CORTAPError (base) -> 500 Internal Server Error

    Args:
        request: FastAPI request object
        exc: CORTAP exception instance

    Returns:
        JSONResponse with error details
    """
    # Map exception types to HTTP status codes
    status_code_map = {
        ValidationError: 400,
        RiskuityAPIError: 502,
        DocumentGenerationError: 500,
        S3StorageError: 500,
    }

    status_code = status_code_map.get(type(exc), 500)

    # Get correlation_id from request state if available
    correlation_id = getattr(request.state, "correlation_id", None)

    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": correlation_id,
        }
    )


@app.get("/")
async def root() -> dict:
    """
    Root endpoint.

    Returns:
        dict: Welcome message with API information
    """
    return {
        "message": f"Welcome to {settings.project_name}",
        "version": "0.1.0",
        "docs": f"{settings.api_v1_prefix}/docs" if settings.environment != "production" else None,
    }


@app.get("/health")
async def health() -> dict:
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "ok"}


# Lambda handler using Mangum
handler = Mangum(app, lifespan="off")
