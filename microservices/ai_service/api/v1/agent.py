from fastapi import APIRouter, Body, Depends

from microservices.ai_service.dependencies import get_ai_service
from microservices.libs.schemas.ai import ChatRequest, ChatResponse, A2AResponse
from microservices.libs.services.ai import AIService

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat_endpoint(
        payload: ChatRequest = Body(...),
        service: AIService = Depends(get_ai_service)
):
    answer = service.execute_chat(payload.query)
    return ChatResponse(answer=answer)


@router.post(
    "/a2a",
    response_model=A2AResponse
)
async def a2a_endpoint(
        service: AIService = Depends(get_ai_service)
):
    result = service.run_a2a_simulation()
    return A2AResponse(
        status="success",
        producer_report=result["producer_report"],
        consumer_report=result["consumer_report"]
    )
