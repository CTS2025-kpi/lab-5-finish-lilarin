from microservices.ai_service.config import config, logger
from microservices.libs.services.ai import AIService

ai_service = AIService(
    google_api_key=config.google_api_key,
    gateway_url=config.api_gateway_url,
    logger=logger
)


def get_ai_service() -> AIService:
    return ai_service
