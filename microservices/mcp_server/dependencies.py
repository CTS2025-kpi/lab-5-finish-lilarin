from microservices.libs.ai.guardrails import SecurityGuardrail
from microservices.mcp_server.config import config

security_guard = SecurityGuardrail(api_key=config.google_api_key)


def get_security_guard() -> SecurityGuardrail:
    return security_guard
