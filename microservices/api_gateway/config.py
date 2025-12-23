import os

from dotenv import load_dotenv

from microservices.libs.utils.logger import setup_logger


class Config:
    def __init__(self):
        load_dotenv()

        # Core Application configuration
        self.account_service_url: str = self._get_env_variable("ACCOUNT_SERVICE_URL")
        self.collections_service_url: str = self._get_env_variable("COLLECTIONS_SERVICE_URL")
        self.tags_service_url: str = self._get_env_variable("TAGS_SERVICE_URL")
        self.links_service_url: str = self._get_env_variable("LINKS_SERVICE_URL")
        self.filter_service_url: str = self._get_env_variable("FILTER_SERVICE_URL")
        self.router_service_url: str = self._get_env_variable("ROUTER_SERVICE_URL")
        self.ai_service_url: str = self._get_env_variable("AI_SERVICE_URL")

        self.jwt_secret: str = self._get_env_variable("JWT_SECRET")
        self.supabase_url: str = self._get_env_variable("SUPABASE_URL")
        self.supabase_key: str = self._get_env_variable("SUPABASE_KEY")

    @staticmethod
    def _get_env_variable(var_name: str) -> str:
        value = os.environ.get(var_name)
        if not value:
            exit(1)
        return value


config = Config()
logger = setup_logger("api-gateway")
