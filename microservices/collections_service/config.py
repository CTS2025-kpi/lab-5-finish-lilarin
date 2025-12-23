import os

from dotenv import load_dotenv
from microservices.libs.utils.logger import setup_logger


class Config:
    def __init__(self):
        load_dotenv()
        self.tags_service_url: str = self._get_env_variable("TAGS_SERVICE_URL")
        self.kafka_broker_url: str = self._get_env_variable("KAFKA_BROKER_URL")

    @staticmethod
    def _get_env_variable(var_name: str) -> str:
        value = os.environ.get(var_name)
        if not value:
            exit(1)
        return value


config = Config()
logger = setup_logger("collections-service")
