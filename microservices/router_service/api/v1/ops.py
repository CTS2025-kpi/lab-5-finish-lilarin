from fastapi import APIRouter, Depends

from microservices.libs.services.coordinator import CoordinatorService
from microservices.router_service.dependencies import get_coordinator_service

router = APIRouter()


@router.get("/health-report")
async def get_health_report(
        service: CoordinatorService = Depends(get_coordinator_service)
):
    status = service.get_topology_status()
    return {
        "status": "active",
        "details": status
    }
