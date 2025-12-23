from typing import Any, Dict

from pydantic import BaseModel, Field, HttpUrl


class TableDefinition(BaseModel):
    table_name: str = Field(..., description="The name of the table to define")
    primary_key: str = Field(..., description="The name of the primary key field")


class CreateRecordRequest(BaseModel):
    table_name: str = Field(..., description="The name of the table to insert the record into")
    value: Dict[str, Any] = Field(..., description="The record data to store")


class RecordResponse(BaseModel):
    table_name: str
    primary_key: str
    value: Any


class ShardRegistration(BaseModel):
    shard_url: HttpUrl = Field(..., description="The advertised URL of the shard that is registering")
    group_id: str = Field(..., description="The ID of the shard group (replica set)")
    is_leader: bool = Field(False, description="Whether this node is the leader of the group")
