from fastapi import APIRouter, Request

from microservices.api_gateway.api.utils import forward_request
from microservices.api_gateway.config import config

router = APIRouter()


@router.get("/health-report", summary="Proxy health report request to Router Service")
async def proxy_health_report(request: Request):
    return await forward_request(config.router_service_url, "ops/health-report", request)
