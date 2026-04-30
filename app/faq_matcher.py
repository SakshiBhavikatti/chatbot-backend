from rapidfuzz import process, fuzz

def match_faq(user_text, faqs, threshold=85):
    user_text_lower = user_text.lower().strip()
    user_words = set(user_text_lower.split())

    # Ignore greeting/noise words
    ignore_words = {
        "hi", "hello", "hey", "ok", "okay", "thanks", "thank you"
    }

    # Exact or keyword match first
    for faq in faqs:
        faq_question_lower = faq.Question.lower().strip()
        faq_words = set(faq_question_lower.split())

        # Exact match
        if faq_question_lower == user_text_lower:
            return faq, 100

        # Partial match (allow short business terms like mts, mrp, bom)
        # but block generic greeting words
        if user_text_lower not in ignore_words and user_text_lower in faq_question_lower:
            return faq, 95

        # Keyword overlap boost
        common_words = user_words.intersection(faq_words)

        # For single-word inputs like "mts", "bom", "mrp"
        # allow 1 common word if it is meaningful
        if len(common_words) >= 1:
            score = fuzz.token_set_ratio(user_text_lower, faq_question_lower)

            if score >= threshold:
                return faq, score

    # Fuzzy match fallback
    questions = [faq.Question for faq in faqs]

    result = process.extractOne(
        user_text,
        questions,
        scorer=fuzz.token_set_ratio
    )

    if result and result[1] >= threshold:
        matched_question = result[0]

        for faq in faqs:
            if faq.Question == matched_question:
                return faq, result[1]

    return None, 0