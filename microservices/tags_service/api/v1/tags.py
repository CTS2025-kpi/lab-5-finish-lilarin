from fastapi import APIRouter, Body, Depends

from microservices.libs.schemas.tags import (
    TagValidationResponse,
    TagValidationRequest,
    TagsListResponse
)
from microservices.libs.services.tags import TagsService
from microservices.tags_service.dependencies import get_tags_service

router = APIRouter()


@router.get(
    "/",
    response_model=TagsListResponse
)
async def get_all_tags(service: TagsService = Depends(get_tags_service)):
    all_tags = service.get_all()
    return TagsListResponse(tags=all_tags)


@router.post(
    "/",
    response_model=TagValidationResponse
)
async def validate_tag(
        payload: TagValidationRequest = Body(...),
        service: TagsService = Depends(get_tags_service)
) -> TagValidationResponse:
    validated_tag_name = service.validate_tag(payload)
    return TagValidationResponse(tag_name=validated_tag_name)
