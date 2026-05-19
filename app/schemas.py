from pydantic import BaseModel, Field
from typing import Optional


class FAQItem(BaseModel):
    Questions: str 
    Answers: str 


class ChatRequest(BaseModel):
    description: str


class ChatResponse(BaseModel):
    reply: str
    matched_faq: Optional[str] = None
    source: str


class IncidentCreate(BaseModel):
    name: str
    email: str
    category: str
    priority: str
    description: str
    suggestions: Optional[str] = None