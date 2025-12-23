from fastapi import APIRouter, Depends

from microservices.libs.schemas.router import ShardRegistration
from microservices.libs.services.coordinator import CoordinatorService
from microservices.router_service.dependencies import get_coordinator_service

router = APIRouter()


@router.post("/register_shard", status_code=200)
async def register_shard(
        payload: ShardRegistration,
        service: CoordinatorService = Depends(get_coordinator_service)
):
    await service.register_shard_node(
        group_id=payload.group_id,
        shard_url=str(payload.shard_url),
        is_leader=payload.is_leader
    )
    return {"status": "registered"}
