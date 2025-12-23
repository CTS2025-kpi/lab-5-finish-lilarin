import os

from dotenv import load_dotenv

from microservices.libs.utils.logger import setup_logger


class Config:
    def __init__(self):
        load_dotenv()

        self.google_api_key: str = self._get_env_variable("GOOGLE_API_KEY")
        self.api_gateway_url: str = os.environ.get("API_GATEWAY_URL")

    @staticmethod
    def _get_env_variable(var_name: str) -> str:
        value = os.environ.get(var_name)
        if not value:
            exit(1)
        return value


config = Config()
logger = setup_logger("ai-service")
