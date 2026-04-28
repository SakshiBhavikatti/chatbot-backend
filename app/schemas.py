from pydantic import BaseModel
from typing import List, Optional

class FAQItem(BaseModel):
    question: str
    answer: str

class ChatRequest(BaseModel):
    incident_id: str
    message: str
    faqs: List[FAQItem]

class ChatResponse(BaseModel):
    reply: str
    matched_faq: Optional[str] = None
    source: str