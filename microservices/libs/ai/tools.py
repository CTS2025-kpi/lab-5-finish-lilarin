from typing import Dict, Any, List

import httpx
from langchain_core.tools import tool, BaseTool


def create_toolkit(api_gateway_url: str) -> List[BaseTool]:
    base_url = api_gateway_url.rstrip("/")

    def _make_request(method: str, path: str, json_data: Dict = None) -> Dict[str, Any]:
        url = f"{base_url}/{path}"
        try:
            with httpx.Client(timeout=10.0) as client:
                if method == "GET":
                    response = client.get(url)
                else:
                    response = client.post(url, json=json_data)

                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        return {
                            "status_code": response.status_code,
                            "error": error_data.get("error", response.text),
                            "detail": "Action failed. Read the error message to understand why."
                        }
                    except Exception:
                        return {
                            "status_code": response.status_code,
                            "error": f"HTTP Error {response.status_code}",
                            "detail": response.text
                        }

                return response.json()
        except Exception as e:
            return {"error": f"Connection failed: {str(e)}"}

    @tool
    def get_item_tags(item_id: int) -> Dict[str, Any]:
        """
        Retrieve the list of tags associated with a specific item ID.
        """
        return _make_request("GET", f"collections/{item_id}/tags")

    @tool
    def add_tag_to_item(item_id: int, tag_name: str) -> Dict[str, Any]:
        """
        Add a specific tag to an item.
        """
        return _make_request("POST", f"collections/{item_id}/tags", {"tag_name": tag_name})

    @tool
    def list_available_tags() -> Dict[str, Any]:
        """
        Get a list of all tags currently available in the system.
        """
        return _make_request("GET", "tags/")

    @tool
    def list_tables() -> Dict[str, Any]:
        """
        List all database tables managed by the storage service.
        Use this to see if a table exists before trying to create it or read from it.
        """
        return _make_request("GET", "storage/tables")

    @tool
    def register_table(table_name: str, primary_key: str) -> Dict[str, Any]:
        """
        Create (register) a new table definition with a specific name and primary key.
        Use this if the requested table does not exist in the list_tables output.
        """
        return _make_request("POST", "storage/tables", {"table_name": table_name, "primary_key": primary_key})

    @tool
    def create_record(table_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new record into a specific table.
        The record_data should contain the primary key and other fields.
        IMPORTANT: Fails if the table does not exist. Use register_table first if needed.
        """
        return _make_request("POST", "storage/records", {"table_name": table_name, "value": record_data})

    return [
        get_item_tags,
        add_tag_to_item,
        list_available_tags,
        list_tables,
        register_table,
        create_record
    ]
