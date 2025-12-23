from typing import List

from pydantic import BaseModel, Field


class AddTagRequest(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=50, description="The name of the tag to add")


class ItemResponse(BaseModel):
    item_id: int
    validated_tag: str


class ItemTagsResponse(BaseModel):
    item_id: int
    tags: List[str] = Field(..., description="List of tags associated with the item")
