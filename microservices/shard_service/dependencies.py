from microservices.libs.services.storage import StorageService
from microservices.shard_service.config import config, logger

storage_service = StorageService(
    router_service_url=config.router_service_url,
    advertised_url=config.advertised_url,
    group_id=config.group_id,
    is_leader=config.is_leader,
    kafka_broker_url=config.kafka_broker_url,
    kafka_topic=config.kafka_topic,
    logger=logger
)


def get_storage_service() -> StorageService:
    return storage_service
