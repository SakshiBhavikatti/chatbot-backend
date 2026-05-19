import re
from fastapi import APIRouter
from app.schemas import ChatRequest, ChatResponse, FAQItem
from app.services.embedding_service import semantic_search
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

        if faq.Questions.strip().lower() == user_text_lower:

            return ChatResponse(
                reply=faq.Answers,
                matched_faq=faq.Questions,
                source="faq"
            )

    # SEMANTIC SEARCH

    semantic_match, semantic_score = semantic_search(
        user_text,
        faqs
    )

    # FUZZY SEARCH

    fuzzy_match, fuzzy_score = match_faq(
        user_text,
        faqs
    )

    matched = None
    score = 0

    # BOTH MATCH SAME FAQ

    if (
        semantic_match
        and fuzzy_match
        and semantic_match.Questions == fuzzy_match.Questions
    ):

        matched = semantic_match

        score = max(
            semantic_score,
            fuzzy_score
        ) + 10

    # SEMANTIC STRONG MATCH

    elif semantic_match and semantic_score >= 65:

        matched = semantic_match
        score = semantic_score

    # FUZZY FALLBACK

    elif fuzzy_match and fuzzy_score >= 60:

        matched = fuzzy_match
        score = fuzzy_score

    # STRONG MATCH

    if matched and score >= 75:

        return ChatResponse(
            reply=matched.Answers,
            matched_faq=matched.Questions,
            source="faq"
        )

    # MEDIUM MATCH

    if matched and score >= 60:

        return ChatResponse(
            reply=(
                "Based on the available SAP support knowledge:\n\n"
                f"{matched.Answers}"
            ),
            matched_faq=matched.Questions,
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