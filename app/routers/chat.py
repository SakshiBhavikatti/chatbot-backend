from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse, FAQItem
from app.services.capm_service import fetch_faqs
from app.faq_matcher import match_faq
from app.prompt_builder import build_faq_prompt, build_direct_prompt
from app.ai_service import ask_claude

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest):

    faq_data = await fetch_faqs()

    faqs = [FAQItem(**faq) for faq in faq_data]

    # 1. Exact FAQ match → return DB answer directly
    for faq in faqs:
        if faq.Question.strip().lower() == data.description.strip().lower():
            return ChatResponse(
                reply=faq.Answer,
                matched_faq=faq.Question,
                source="faq"
            )

    # 2. Keyword/partial FAQ match → use FAQ context + AI Core
    matched = match_faq(
        data.description,
        faqs
    )

    if matched:
        prompt = build_faq_prompt(
            data.description,
            matched
        )

        reply = ask_claude(prompt)

        return ChatResponse(
            reply=reply,
            matched_faq=matched.Question,
            source="faq+llm"
        )

    # 3. No FAQ match → direct AI Core
    prompt = build_direct_prompt(
        data.description
    )

    reply = ask_claude(prompt)

    return ChatResponse(
        reply=reply,
        source="llm"
    )