import re
from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse, FAQItem
from app.services.capm_service import fetch_faqs, get_incident_by_id
from app.faq_matcher import match_faq
from app.prompt_builder import build_faq_prompt, build_direct_prompt
from app.ai_service import ask_claude

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest):

    user_text = data.description.strip()

    # ===============================
    # 1. INCIDENT STATUS CHECK
    # ===============================
    incident_match = re.search(
        r'([0-9a-fA-F\-]{36})',
        user_text
    )

    if "status" in user_text.lower() and incident_match:
        incident_id = incident_match.group(1)

        try:
            incident = await get_incident_by_id(incident_id)

            return ChatResponse(
                reply=f"Incident ID: {incident_id}\nStatus: {incident.get('status', 'Open')}",
                source="incident"
            )

        except:
            return ChatResponse(
                reply="Incident not found.",
                source="incident"
            )

    # ===============================
    # 2. FAQ FLOW
    # ===============================
    faq_data = await fetch_faqs()

    faqs = [FAQItem(**faq) for faq in faq_data]

    for faq in faqs:
        if faq.Question.strip().lower() == user_text.lower():
            return ChatResponse(
                reply=faq.Answer,
                matched_faq=faq.Question,
                source="faq"
            )

    matched, score = match_faq(user_text, faqs)

    # Strong similar match → DB direct
    if matched and score >= 90:
        return ChatResponse(
            reply=matched.Answer,
            matched_faq=matched.Question,
            source="faq"
        )

    # Medium similar match → FAQ + LLM
    if matched and score >= 70:
        prompt = build_faq_prompt(user_text, matched)
        reply = ask_claude(prompt)

        return ChatResponse(
            reply=reply,
            matched_faq=matched.Question,
            source="faq+llm"
        )

    # ===============================
    # 3. DIRECT LLM
    # ===============================
    prompt = build_direct_prompt(user_text)

    reply = ask_claude(prompt)

    return ChatResponse(
        reply=reply,
        source="llm"
    )