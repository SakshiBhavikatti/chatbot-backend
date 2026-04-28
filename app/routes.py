from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse
from app.faq_matcher import match_faq
from app.prompt_builder import build_faq_prompt, build_direct_prompt
from app.ai_service import ask_claude

router = APIRouter()

@router.post("/invoke", response_model=ChatResponse)
def chat(data: ChatRequest):
    faq = match_faq(data.message, data.faqs)

    if faq:
        prompt = build_faq_prompt(data.message, faq)
        reply = ask_claude(prompt)

        return ChatResponse(
            reply=reply,
            matched_faq=faq.question,
            source="faq+llm"
        )

    prompt = build_direct_prompt(data.message)
    reply = ask_claude(prompt)

    return ChatResponse(
        reply=reply,
        source="llm"
    )