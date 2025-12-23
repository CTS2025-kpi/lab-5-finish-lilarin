from fastapi import APIRouter, Request

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.config import config

router = APIRouter()


@router.get("/{path:path}")
async def proxy_filter_get(path: str, request: Request):
    return await forward_request(config.filter_service_url, path, request)
