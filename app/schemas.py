from pydantic import BaseModel, Field
from typing import Optional


class FAQItem(BaseModel):
    question: str = Field(validation_alias="Question")
    answer: str = Field(validation_alias="Answer")


class ChatRequest(BaseModel):
    description: str


class ChatResponse(BaseModel):
    reply: str
    matched_faq: Optional[str] = None
    source: str


class IncidentCreate(BaseModel):
    incident_id: int
    name: str
    email: str
    category: str
    priority: str
    description: str
    suggestion: Optional[str] = None