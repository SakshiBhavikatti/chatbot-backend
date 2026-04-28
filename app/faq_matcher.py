from rapidfuzz import process, fuzz

def match_faq(user_text, faqs, threshold=70):
    questions = [faq.question for faq in faqs]

    result = process.extractOne(
        user_text,
        questions,
        scorer=fuzz.token_sort_ratio
    )

    if result and result[1] >= threshold:
        matched_question = result[0]

        for faq in faqs:
            if faq.question == matched_question:
                return faq

    return None