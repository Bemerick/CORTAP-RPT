"""
CORTAP-RPT FastAPI Application.

Main application module that creates the FastAPI app instance,
configures middleware, and includes route handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.config import settings


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
