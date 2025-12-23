from typing import Any, Dict, Optional

from pydantic import BaseModel


class RecordData(BaseModel):
    value: Dict[str, Any]


class RecordResponse(BaseModel):
    table_name: str
    primary_key: str
    value: Any


class ReplicationMessage(BaseModel):
    operation: str
    table_name: str
    primary_key: str
    value: Optional[Dict[str, Any]] = None
    timestamp: int
