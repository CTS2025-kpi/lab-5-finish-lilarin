from microservices.collections_service.config import config, logger
from microservices.libs.services.collections import CollectionsService

collections_service = CollectionsService(
    kafka_broker_url=config.kafka_broker_url,
    tags_service_url=config.tags_service_url,
    logger=logger
)


def get_collections_service() -> CollectionsService:
    return collections_service
