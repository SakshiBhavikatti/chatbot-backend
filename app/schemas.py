from pydantic import BaseModel, Field
from typing import Optional


class FAQItem(BaseModel):
    Question: str 
    Answer: str 


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
    suggestion: Optional[str] = None
    status: str