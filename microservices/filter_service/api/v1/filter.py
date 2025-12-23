from fastapi import APIRouter, Path, Depends

from microservices.filter_service.dependencies import get_filter_service
from microservices.libs.schemas.filter import ItemUpdatesResponse
from microservices.libs.services.filter import FilterService

router = APIRouter()


@router.get(
    "/updates/{item_id}",
    response_model=ItemUpdatesResponse,
    summary="Get all updates for a specific item"
)
async def get_item_updates(
        item_id: str = Path(..., description="The ID of the item"),
        service: FilterService = Depends(get_filter_service)
):
    updates = service.get_updates_for_item(item_id)
    return ItemUpdatesResponse(item_id=item_id, updates=updates)
