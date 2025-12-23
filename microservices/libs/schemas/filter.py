from typing import List, Dict, Any

from pydantic import BaseModel, Field


class UpdateRecord(BaseModel):
    action: str
    details: Dict[str, Any]


class ItemUpdatesResponse(BaseModel):
    item_id: str
    updates: List[UpdateRecord] = Field(..., description="List of updates for the item")
