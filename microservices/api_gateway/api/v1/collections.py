from typing import Any

from fastapi import APIRouter, Request, Body

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.config import config

router = APIRouter()


@router.get("/{path:path}")
async def proxy_collections_get(path: str, request: Request):
    return await forward_request(config.collections_service_url, path, request)


@router.post("/{path:path}")
async def proxy_collections_post(path: str, request: Request, body: Any = Body(...)):
    return await forward_request(config.collections_service_url, path, request)
