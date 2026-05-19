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
    "please",
    "can",
    "could",
    "would",
    "should",
    "give",
    "tell",
    "explain",
    "details",
    "detail",
    "about",
    "more",
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "to",
    "for",
    "of",
    "in",
    "on",
    "with"
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


IMPORTANT_TERMS = {
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
    "reservation",
    "backflush",
    "capacity",
    "planning",
    "material",
    "batch",
    "scrap",
    "goods",
    "receipt",
    "issue"
}


def normalize_text(text: str):

    text = text.lower().strip()

    # remove dots/hyphens/slashes between letters
    # m.r.p -> mrp
    # back-flush -> backflush
    text = re.sub(
        r'(?<=[a-zA-Z])[\.\-_\/\\](?=[a-zA-Z])',
        '',
        text
    )

    # remove remaining special chars
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    # synonym expansion
    for short, full in SAP_SYNONYMS.items():

        text = re.sub(
            rf"\b{re.escape(short)}\b",
            full,
            text
        )

    return text.strip()


def tokenize(text: str):

    words = text.split()

    filtered = []

    for word in words:
        if word not in IGNORE_WORDS:
            filtered.append(word)

    return set(filtered)


def keyword_overlap_score(user_words, faq_words):

    if not faq_words:
        return 0

    common_words = user_words.intersection(faq_words)

    return (
        len(common_words) / len(faq_words)
    ) * 100


def important_term_bonus(user_words, faq_words):

    common_important = (
        user_words
        .intersection(faq_words)
        .intersection(IMPORTANT_TERMS)
    )

    return len(common_important) * 12


def contains_core_phrase(user_words, faq_words):

    common = user_words.intersection(faq_words)

    # strong overlap
    if len(common) >= 2:
        return True

    # important SAP keyword present
    strong_terms = IMPORTANT_TERMS.intersection(common)

    if len(strong_terms) >= 1:
        return True

    return False


def match_faq(user_text, faqs, threshold=60):

    user_text_normalized = normalize_text(user_text)

    if user_text_normalized in IGNORE_WORDS:
        return None, 0

    user_words = tokenize(user_text_normalized)

    if not user_words:
        return None, 0

    best_match = None
    best_score = 0

    for faq in faqs:

        faq_question_normalized = normalize_text(
            faq.Questions
        )

        faq_words = tokenize(
            faq_question_normalized
        )

        # 1. EXACT MATCH

        if faq_question_normalized == user_text_normalized:
            return faq, 100

        # 2. CORE PHRASE MATCH

        if contains_core_phrase(
            user_words,
            faq_words
        ):
            return faq, 95

        # 3. RAPIDFUZZ

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

        # 5. IMPORTANT TERM BONUS

        bonus = important_term_bonus(
            user_words,
            faq_words
        )

        # 6. FINAL SCORE

        final_score = (
            (token_score * 0.30) +
            (partial_score * 0.35) +
            (sort_score * 0.15) +
            (keyword_score * 0.20) +
            bonus
        )

        # 7. EXTRA BOOST FOR IMPORTANT SAP TERMS

        important_matches = (
            user_words
            .intersection(faq_words)
            .intersection(IMPORTANT_TERMS)
        )

        if len(important_matches) >= 1:
            final_score += 10

        if final_score > best_score:
            best_score = final_score
            best_match = faq

    # 8. FALLBACK RAPIDFUZZ

    questions = [faq.Questions for faq in faqs]

    result = process.extractOne(
        user_text_normalized,
        questions,
        scorer=fuzz.token_set_ratio
    )

    if result and result[1] > best_score:

        matched_question = result[0]

        for faq in faqs:
            if faq.Questions == matched_question:
                best_match = faq
                best_score = result[1]

    # 9. FINAL RETURN

    if best_match and best_score >= threshold:
        return best_match, round(best_score)

    return None, 0