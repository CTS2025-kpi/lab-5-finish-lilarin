import os
import uvicorn  # Added for backup

import httpx
from mcp.server.fastmcp import FastMCP

from microservices.libs.ai.guardrails import SecurityGuardrail
from microservices.mcp_server.config import config

mcp = FastMCP("Microservices-Manager")

security_guard = SecurityGuardrail(api_key=config.google_api_key)


@mcp.tool()
async def manage_storage(action: str, table_name: str, data: dict = None):
    """
    Creates tables or records
    action: ‘create_table’ or ‘create_record’
    """
    if security_guard and not security_guard.is_safe(f"{action} on {table_name}"):
        return "Security policy violation"

    async with httpx.AsyncClient() as client:
        if action == "create_table":
            resp = await client.post(f"{config.api_gateway_url}/storage/tables", json={
                "table_name": table_name,
                "primary_key": data.get("primary_key", "id") if data else "id"
            })
        elif action == "create_record":
            resp = await client.post(f"{config.api_gateway_url}/storage/records", json={
                "table_name": table_name,
                "value": data
            })
        else:
            return "Unknown action"
        return resp.json()


@mcp.tool()
async def get_item_info(item_id: int):
    """Receives tags and updates for a specific collection item"""
    async with httpx.AsyncClient() as client:
        try:
            tags_resp = await client.get(f"{config.api_gateway_url}/collections/{item_id}/tags")
            updates_resp = await client.get(f"{config.api_gateway_url}/filter/updates/{item_id}")
            return {
                "tags": tags_resp.json() if tags_resp.status_code == 200 else "Error fetching tags",
                "history": updates_resp.json() if updates_resp.status_code == 200 else "Error fetching history"
            }
        except Exception as e:
            return f"Connection error: {str(e)}"


if __name__ == "__main__":
    print("Starting MCP Server on 0.0.0.0:8000...")

    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    mcp.run(transport="sse")