import os

from dotenv import load_dotenv

from microservices.libs.utils.logger import setup_logger


class Config:
    def __init__(self):
        load_dotenv()
        self.google_api_key: str = os.environ.get("GOOGLE_API_KEY")
        self.api_gateway_url: str = os.environ.get("API_GATEWAY_URL", "http://api-gateway/api/v1")


config = Config()
logger = setup_logger("mcp-server")
