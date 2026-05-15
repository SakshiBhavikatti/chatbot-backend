import re
from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse, FAQItem
from app.services.capm_service import fetch_faqs, get_incident_by_id
from app.faq_matcher import match_faq

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/", response_model=ChatResponse)
async def chat(data: ChatRequest):

    user_text = data.description.strip()
    user_text_lower = user_text.lower()

    # 0. GREETING FLOW

    greetings = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hello! How can I assist you today?",
        "hey": "Hello! How can I assist you today?",
        "thanks": "You're welcome!",
        "thank you": "You're welcome!",
        "ok": "Okay!",
        "okay": "Okay!",
        "bye": "Goodbye! Have a great day."
    }

    if user_text_lower in greetings:
        return ChatResponse(
            reply=greetings[user_text_lower],
            source="greeting"
        )

    # 1. INCIDENT STATUS CHECK

    incident_match = re.search(
        r'([0-9a-fA-F\-]{36})',
        user_text
    )

    incident_keywords = {
        "status",
        "incident",
        "ticket",
        "issue"
    }

    if (
        any(word in user_text_lower for word in incident_keywords)
        and incident_match
    ):

        incident_id = incident_match.group(1)

        try:
            incident = await get_incident_by_id(incident_id)

            return ChatResponse(
                reply=(
                    f"Incident ID: {incident_id}\n"
                    f"Status: {incident.get('status', 'Open')}"
                ),
                source="incident"
            )

        except:
            return ChatResponse(
                reply="Incident not found.",
                source="incident"
            )

    # 2. FAQ FLOW

    try:
        faq_data = await fetch_faqs()

    except:
        return ChatResponse(
            reply=(
                "Unable to access the SAP support knowledge base currently. "
                "Please try again later or raise an incident."
            ),
            source="system"
        )

    faqs = [FAQItem(**faq) for faq in faq_data]

    # Exact match
    for faq in faqs:
        if faq.Question.strip().lower() == user_text_lower:
            return ChatResponse(
                reply=faq.Answer,
                matched_faq=faq.Question,
                source="faq"
            )

    # Smart FAQ match
    matched, score = match_faq(user_text, faqs)

    # Strong match
    if matched and score >= 85:
        return ChatResponse(
            reply=matched.Answer,
            matched_faq=matched.Question,
            source="faq"
        )

    # Medium match
    if matched and score >= 70:
        return ChatResponse(
            reply=(
                "Based on the available SAP support knowledge:\n\n"
                f"{matched.Answer}"
            ),
            matched_faq=matched.Question,
            source="faq"
        )

    # 3. FALLBACK
    
    return ChatResponse(
        reply=(
            "I cannot answer this question from the available "
            "SAP support knowledge base. "
            "Please raise an incident for further assistance."
        ),
        source="fallback"
    )