from fastapi import APIRouter

from microservices.collections_service.api.v1.collections import router as collections_router

router = APIRouter(prefix="/v1")

router.include_router(collections_router, tags=["Collections"])
