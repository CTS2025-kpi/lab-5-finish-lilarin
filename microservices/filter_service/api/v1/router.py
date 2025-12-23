from fastapi import APIRouter

from api.v1.filter import router as filter_router

router = APIRouter(prefix="/v1")

router.include_router(filter_router, tags=["Filter"])
