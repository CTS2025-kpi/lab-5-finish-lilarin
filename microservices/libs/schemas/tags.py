from typing import List

from pydantic import BaseModel, Field


class TagValidationRequest(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=50)


class TagValidationResponse(BaseModel):
    tag_name: str


class TagsListResponse(BaseModel):
    tags: List[str] = Field(..., description="A list of all available tags")


class AddTagToItemRequest(BaseModel):
    tag_name: str = Field(..., min_length=1, max_length=50, description="The name of the tag to add")
