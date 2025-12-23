from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


class A2AResponse(BaseModel):
    status: str
    producer_report: str
    consumer_report: str
