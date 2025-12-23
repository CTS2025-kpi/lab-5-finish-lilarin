from microservices.filter_service.config import config, logger
from microservices.libs.services.filter import FilterService

filter_service = FilterService(
    kafka_broker_url=config.kafka_broker_url,
    logger=logger
)


def get_filter_service() -> FilterService:
    return filter_service
