from typing import Any

from fastapi import APIRouter, Request, Body

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.config import config

router = APIRouter()


@router.post("/{path:path}", summary="Proxy requests to AI Service")
async def proxy_ai_post(path: str, request: Request, body: Any = Body(...)):
    return await forward_request(config.ai_service_url, path, request)
