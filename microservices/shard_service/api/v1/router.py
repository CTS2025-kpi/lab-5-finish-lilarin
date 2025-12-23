from fastapi import APIRouter

from microservices.shard_service.api.v1.records import router as records_router

router = APIRouter(prefix="/v1")

router.include_router(records_router, prefix="/records", tags=["Records"])
