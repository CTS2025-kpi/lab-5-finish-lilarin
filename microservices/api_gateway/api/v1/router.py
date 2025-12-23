from fastapi import APIRouter

from microservices.api_gateway.api.v1.ai import router as ai_router
from microservices.api_gateway.api.v1.auth import router as auth_router
from microservices.api_gateway.api.v1.collections import router as collections_router
from microservices.api_gateway.api.v1.filter import router as filter_router
from microservices.api_gateway.api.v1.ops import router as ops_router
from microservices.api_gateway.api.v1.storage import router as storage_router
from microservices.api_gateway.api.v1.tags import router as tags_router

router = APIRouter(prefix="/v1")

router.include_router(collections_router, prefix="/collections", tags=["Collections Proxy"])
router.include_router(tags_router, prefix="/tags", tags=["Tags Proxy"])
router.include_router(filter_router, prefix="/filter", tags=["Filter Proxy"])
router.include_router(storage_router, prefix="/storage", tags=["Storage Proxy"])
router.include_router(ops_router, prefix="/ops", tags=["Operations Proxy"])
router.include_router(ai_router, prefix="/ai", tags=["AI Proxy"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
