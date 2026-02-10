"""Test endpoints."""

from fastapi import APIRouter
# TODO: Enable authentication in Epic 0
# from fastapi import Depends
# from app.core.users import current_active_user

router = APIRouter()


@router.get("/test")  # TODO: Add dependencies=[Depends(current_active_user)] in Epic 0
async def test():
    return {"message": "Hello World from CORTAP-RPT!"}
