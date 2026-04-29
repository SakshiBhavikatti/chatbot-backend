import re


def extract_incident_id(text: str):
    text_lower = text.lower()

    status_words = ["status", "incident", "ticket"]

    if not any(word in text_lower for word in status_words):
        return None

    patterns = [
        r'incident id[:\s\-]*([A-Za-z0-9\-]+)',
        r'incident[:\s\-]*([A-Za-z0-9\-]+)',
        r'id[:\s\-]*([A-Za-z0-9\-]+)',
        r'\b([A-Za-z0-9]{6,})\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return None