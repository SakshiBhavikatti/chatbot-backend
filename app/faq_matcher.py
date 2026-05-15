import re
from rapidfuzz import process, fuzz


IGNORE_WORDS = {
    "hi",
    "hello",
    "hey",
    "ok",
    "okay",
    "thanks",
    "thank you",
    "bye",
    "please"
}


SAP_SYNONYMS = {
    "po": "production order",
    "prod order": "production order",
    "production orders": "production order",

    "mrp": "material requirements planning",
    "bom": "bill of materials",
    "mts": "make to stock",
    "mto": "make to order",
    "teco": "technically completed",

    "pp": "production planning",
    "mm": "material management",
    "qm": "quality management",

    "gr": "goods receipt",
    "gi": "goods issue",

    "routing": "production routing",
    "wc": "work center"
}


def normalize_text(text: str):

    text = text.lower().strip()

    # remove special chars
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    # expand SAP synonyms
    for short, full in SAP_SYNONYMS.items():
        text = text.replace(short, full)

    return text.strip()


def keyword_overlap_score(user_words, faq_words):

    if not faq_words:
        return 0

    common_words = user_words.intersection(faq_words)

    return (len(common_words) / len(faq_words)) * 100


def match_faq(user_text, faqs, threshold=70):

    user_text_normalized = normalize_text(user_text)

    if user_text_normalized in IGNORE_WORDS:
        return None, 0

    user_words = set(user_text_normalized.split())

    best_match = None
    best_score = 0

    # LOOP THROUGH FAQS

    for faq in faqs:

        faq_question_normalized = normalize_text(
            faq.Question
        )

        faq_words = set(
            faq_question_normalized.split()
        )

        # 1. EXACT MATCH

        if faq_question_normalized == user_text_normalized:
            return faq, 100

        # 2. DIRECT CONTAINS

        if (
            user_text_normalized not in IGNORE_WORDS
            and user_text_normalized in faq_question_normalized
        ):
            return faq, 96

        # 3. RAPIDFUZZ SCORES

        token_score = fuzz.token_set_ratio(
            user_text_normalized,
            faq_question_normalized
        )

        partial_score = fuzz.partial_ratio(
            user_text_normalized,
            faq_question_normalized
        )

        sort_score = fuzz.token_sort_ratio(
            user_text_normalized,
            faq_question_normalized
        )

        # 4. KEYWORD OVERLAP

        keyword_score = keyword_overlap_score(
            user_words,
            faq_words
        )

        # 5. BONUS FOR IMPORTANT SAP TERMS

        important_terms = {
            "mrp",
            "bom",
            "mts",
            "mto",
            "teco",
            "production",
            "order",
            "routing",
            "work",
            "center",
            "quality",
            "stock",
            "reservation"
        }

        common_important = (
            user_words.intersection(faq_words)
            .intersection(important_terms)
        )

        important_bonus = len(common_important) * 5

        # 6. FINAL WEIGHTED SCORE
        
        final_score = (
            (token_score * 0.35) +
            (partial_score * 0.30) +
            (sort_score * 0.20) +
            (keyword_score * 0.15) +
            important_bonus
        )

        # 7. SAVE BEST MATCH

        if final_score > best_score:
            best_score = final_score
            best_match = faq

    # 8. FALLBACK extractOne

    questions = [faq.Question for faq in faqs]

    result = process.extractOne(
        user_text_normalized,
        questions,
        scorer=fuzz.token_set_ratio
    )

    if result and result[1] > best_score:

        matched_question = result[0]

        for faq in faqs:
            if faq.Question == matched_question:
                best_match = faq
                best_score = result[1]

    # 9. RETURN FINAL MATCH
    
    if best_match and best_score >= threshold:
        return best_match, round(best_score)

    return None, 0