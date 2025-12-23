from fastapi import APIRouter

from microservices.tags_service.api.v1.tags import router as tags_router

router = APIRouter(prefix="/v1")

router.include_router(tags_router, tags=["Tags"])
