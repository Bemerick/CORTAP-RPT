"""API v1 router configuration."""

from fastapi import APIRouter
from app.api.v1.endpoints import test, documents, data

# Temporarily commented out until authentication is implemented (Epic 0)
# from app.core.users import fastapi_users
# from app.core.security import auth_backend
# from app.schemas.user import UserRead, UserCreate, UserUpdate

api_v1_router = APIRouter(prefix="/api/v1")

# FastAPI-Users routers (TODO: Enable in Epic 0 - Multi-Tenant Foundation)
# api_v1_router.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth",
#     tags=["auth"],
# )
# api_v1_router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["auth"],
# )
# api_v1_router.include_router(
#     fastapi_users.get_verify_router(UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
# api_v1_router.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )

# Custom routers
api_v1_router.include_router(test.router, tags=["Test"])
api_v1_router.include_router(data.router, tags=["Data"])
api_v1_router.include_router(documents.router, tags=["Documents"])
