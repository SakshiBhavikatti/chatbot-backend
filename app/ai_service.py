import httpx
from app.config import (
    AICORE_BASE_URL,
    AICORE_AUTH_URL,
    AICORE_CLIENT_ID,
    AICORE_CLIENT_SECRET,
    AICORE_RESOURCE_GROUP,
    MODEL_ENDPOINT,
    validate_config
)

TIMEOUT = 60.0


def get_access_token():
    validate_config()

    response = httpx.post(
        AICORE_AUTH_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": AICORE_CLIENT_ID,
            "client_secret": AICORE_CLIENT_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=TIMEOUT
    )

    response.raise_for_status()
    return response.json()["access_token"]


def ask_claude(prompt: str):
    token = get_access_token()

    url = f"{AICORE_BASE_URL}{MODEL_ENDPOINT}"

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if AICORE_RESOURCE_GROUP:
        headers["AI-Resource-Group"] = AICORE_RESOURCE_GROUP

    response = httpx.post(
        url,
        json=payload,
        headers=headers,
        timeout=TIMEOUT
    )

    if response.status_code >= 400:
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        response.raise_for_status()

    data = response.json()
    print("SUCCESS RESPONSE:", data)

    return data["content"][0]["text"]