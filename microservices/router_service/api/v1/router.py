from fastapi import APIRouter

from microservices.router_service.api.v1.internal import router as internal_router
from microservices.router_service.api.v1.ops import router as ops_router
from microservices.router_service.api.v1.records import router as records_router
from microservices.router_service.api.v1.tables import router as tables_router

router = APIRouter(prefix="/v1")

router.include_router(tables_router, prefix="/tables", tags=["Tables"])
router.include_router(records_router, prefix="/records", tags=["Records"])
router.include_router(ops_router, prefix="/ops", tags=["Operations"])
router.include_router(internal_router, prefix="/_internal", tags=["Internal"], include_in_schema=False)
