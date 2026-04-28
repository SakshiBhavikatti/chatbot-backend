import os
from dotenv import load_dotenv

load_dotenv()

AICORE_BASE_URL = os.getenv("AICORE_BASE_URL", "").strip()
AICORE_AUTH_URL = os.getenv("AICORE_AUTH_URL", "").strip()
AICORE_CLIENT_ID = os.getenv("AICORE_CLIENT_ID", "").strip()
AICORE_CLIENT_SECRET = os.getenv("AICORE_CLIENT_SECRET", "").strip()
AICORE_RESOURCE_GROUP = os.getenv("AICORE_RESOURCE_GROUP", "").strip()
AICORE_DEPLOYMENT_ID = os.getenv("AICORE_DEPLOYMENT_ID", "").strip()
MODEL_ENDPOINT = os.getenv("MODEL_ENDPOINT", "").strip()

# CAPM
CAPM_BASE_URL = os.getenv("CAPM_BASE_URL", "").strip()
CAPM_FAQ_ENDPOINT = os.getenv("CAPM_FAQ_ENDPOINT", "").strip()
CAPM_INCIDENT_ENDPOINT = os.getenv("CAPM_INCIDENT_ENDPOINT", "").strip()
CAPM_AUTH_URL = os.getenv("CAPM_AUTH_URL", "").strip()
CAPM_CLIENT_ID = os.getenv("CAPM_CLIENT_ID", "").strip()
CAPM_CLIENT_SECRET = os.getenv("CAPM_CLIENT_SECRET", "").strip()


def validate_config():
    required = {
        "AICORE_BASE_URL": AICORE_BASE_URL,
        "AICORE_AUTH_URL": AICORE_AUTH_URL,
        "AICORE_CLIENT_ID": AICORE_CLIENT_ID,
        "AICORE_CLIENT_SECRET": AICORE_CLIENT_SECRET,
        "AICORE_DEPLOYMENT_ID": AICORE_DEPLOYMENT_ID,
        "CAPM_BASE_URL": CAPM_BASE_URL,
        "CAPM_AUTH_URL": CAPM_AUTH_URL,
        "CAPM_CLIENT_ID": CAPM_CLIENT_ID,
        "CAPM_CLIENT_SECRET": CAPM_CLIENT_SECRET
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise ValueError(f"Missing env vars: {', '.join(missing)}")