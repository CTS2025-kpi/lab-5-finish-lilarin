import os

from microservices.libs.utils.logger import setup_logger


class Config:
    def __init__(self):
        self.router_service_url: str = self._get_env_variable("ROUTER_SERVICE_URL")
        self.advertised_url: str = self._get_env_variable("ADVERTISED_URL")

        self.group_id: str = self._get_env_variable("SHARD_GROUP_ID")
        self.is_leader: bool = os.environ.get("IS_LEADER", "false").lower() == "true"
        self.kafka_broker_url: str = self._get_env_variable("KAFKA_BROKER_URL")
        self.kafka_topic: str = self._get_env_variable("KAFKA_TOPIC")

    @staticmethod
    def _get_env_variable(var_name: str) -> str:
        value = os.environ.get(var_name)
        if not value:
            exit(1)
        return value


config = Config()
logger = setup_logger("shard-service")
