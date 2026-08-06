import json
import os


IP_CHECK_INTERVAL = int(
    os.getenv(
        "IP_CHECK_INTERVAL",
        "30",
    )
)

TRANSIP_UPDATE_COOLDOWN = int(
    os.getenv(
        "TRANSIP_UPDATE_COOLDOWN",
        "300",
    )
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
    os.getenv(
        "TRANSIP_FIREWALL_RULES",
        "[]",
    )
)