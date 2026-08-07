import json
import os


IP_CHECK_INTERVAL = int(
    os.getenv("IP_CHECK_INTERVAL") or "30"
)

TRANSIP_UPDATE_COOLDOWN = int(
    os.getenv("TRANSIP_UPDATE_COOLDOWN") or "300"
)

TRANSIP_ACCOUNT_NAME = os.getenv(
    "TRANSIP_ACCOUNT_NAME"
)

TRANSIP_VPS_NAME = os.getenv(
    "TRANSIP_VPS_NAME"
)

TRANSIP_PRIVATE_KEY_FILE = os.getenv(
    "TRANSIP_PRIVATE_KEY_FILE",
    "/config/transip_private_key.pem",
)

TRANSIP_FIREWALL_RULES = json.loads(
    os.getenv("TRANSIP_FIREWALL_RULES") or "[]"
)

TRANSIP_UPDATE_DNS = (
    os.getenv("TRANSIP_UPDATE_DNS", "false").lower()
    in ("true", "1", "yes", "on")
)

TRANSIP_DNS_RECORDS = json.loads(
    os.getenv("TRANSIP_DNS_RECORDS") or "{}"
)

TRANSIP_DNS_TTL = int(
    os.getenv("TRANSIP_DNS_TTL") or "300"
)