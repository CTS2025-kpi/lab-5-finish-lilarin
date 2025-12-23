from fastapi import APIRouter, Request, Body, Depends

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.auth import verify_token
from microservices.api_gateway.config import config
from microservices.libs.schemas.tags import AddTagToItemRequest

router = APIRouter()


@router.get("/")
async def proxy_get_all_tags(request: Request):
    return await forward_request(config.tags_service_url, "", request)


@router.post(
    "/",
    dependencies=[Depends(verify_token)]
)
async def proxy_tags_post(request: Request, body: AddTagToItemRequest = Body(...)):
    return await forward_request(config.tags_service_url, "", request)
