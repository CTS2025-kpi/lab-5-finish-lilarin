from fastapi import APIRouter

from microservices.ai_service.api.v1.agent import router as agent_router

router = APIRouter(prefix="/v1")
router.include_router(agent_router, prefix="/agents", tags=["AI Agents"])
