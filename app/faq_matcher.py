from rapidfuzz import process, fuzz

def match_faq(user_text, faqs, threshold=70):
    user_text_lower = user_text.lower().strip()

    # Exact or keyword match first
    for faq in faqs:
        faq_question_lower = faq.Question.lower().strip()

        # Exact match
        if faq_question_lower == user_text_lower:
            return faq

        # Keyword/partial match
        if user_text_lower in faq_question_lower:
            return faq

    # Fuzzy match fallback
    questions = [faq.Question for faq in faqs]

    result = process.extractOne(
        user_text,
        questions,
        scorer=fuzz.token_sort_ratio
    )

    if result and result[1] >= threshold:
        matched_question = result[0]

        for faq in faqs:
            if faq.Question == matched_question:
                return faq

    return None