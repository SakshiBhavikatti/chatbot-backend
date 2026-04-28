import httpx
from app.config import (
    CAPM_BASE_URL,
    CAPM_FAQ_ENDPOINT,
    CAPM_INCIDENT_ENDPOINT,
    CAPM_AUTH_URL,
    CAPM_CLIENT_ID,
    CAPM_CLIENT_SECRET
)

TIMEOUT = 60.0


async def get_capm_token():
    response = httpx.post(
        CAPM_AUTH_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CAPM_CLIENT_ID,
            "client_secret": CAPM_CLIENT_SECRET
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=TIMEOUT
    )

    response.raise_for_status()

    return response.json()["access_token"]


async def fetch_faqs():
    token = await get_capm_token()

    url = f"{CAPM_BASE_URL}{CAPM_FAQ_ENDPOINT}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers
        )

        response.raise_for_status()

        data = response.json()

        return data.get("value", [])


async def create_incident(payload):
    token = await get_capm_token()

    url = f"{CAPM_BASE_URL}{CAPM_INCIDENT_ENDPOINT}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=payload,
            headers=headers
        )

        response.raise_for_status()

        return response.json()