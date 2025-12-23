from fastapi import APIRouter, Body, Path, Depends

from microservices.collections_service.dependencies import get_collections_service
from microservices.libs.schemas.collections import (
    AddTagRequest,
    ItemResponse,
    ItemTagsResponse
)
from microservices.libs.services.collections import CollectionsService

router = APIRouter()


@router.post(
    "/{item_id}/tags",
    response_model=ItemResponse,
    summary="Add a tag to an item in a collection",
)
async def add_tag_to_item(
        item_id: int = Path(..., description="The ID of the item to tag"),
        payload: AddTagRequest = Body(...),
        service: CollectionsService = Depends(get_collections_service)
):
    validated_tag = await service.add_tag_to_item(item_id, payload)
    return ItemResponse(item_id=item_id, validated_tag=validated_tag)


@router.get(
    "/{item_id}/tags",
    response_model=ItemTagsResponse,
    summary="Get all tags for an item"
)
async def get_item_tags(
        item_id: int = Path(..., description="The ID of the item to get tags for"),
        service: CollectionsService = Depends(get_collections_service)
):
    tags = service.get_item_tags(item_id)
    return ItemTagsResponse(item_id=item_id, tags=tags)
