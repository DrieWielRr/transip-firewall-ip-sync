import logging
import os
import time

from ipcheck import get_public_ip
from sync import sync_firewall
from state import get_last_sync, update_sync



def mask_value(value):
    """
    Show only the last 3 characters of a value.
    """

    if not value:
        return "<not set>"

    if len(value) <= 3:
        return "***"

    return f"****{value[-3:]}"


def log_configuration():
    logging.info(
        "Configuration: IP_CHECK_INTERVAL=%ss TRANSIP_UPDATE_COOLDOWN=%ss",
        IP_CHECK_INTERVAL,
        TRANSIP_UPDATE_COOLDOWN,
    )

    logging.info(
        "TransIP configuration: access_token=%s vps=%s",
        mask_value(
            os.getenv("TRANSIP_ACCESS_TOKEN")
        ),
        mask_value(
            os.getenv("TRANSIP_VPS_NAME")
        ),
    )


IP_CHECK_INTERVAL = int(
    os.getenv("IP_CHECK_INTERVAL", "30")
)

TRANSIP_UPDATE_COOLDOWN = int(
    os.getenv("TRANSIP_UPDATE_COOLDOWN", "300")
)


def check_ip():
    current_ip = get_public_ip()
    last_sync = get_last_sync()

    if last_sync is None:
        logging.info(
            "No previous synchronization found"
        )

        if sync_firewall(current_ip):
            update_sync(current_ip)

        return

    last_ip = last_sync.get("ip")

    if current_ip != last_ip:
        logging.info(
            "IP change detected: %s -> %s",
            last_ip,
            current_ip,
        )

        if sync_firewall(current_ip):
            update_sync(current_ip)

    else:
        logging.info(
            "IP unchanged and already synchronized: %s",
            current_ip,
        )


def main():
    logging.info(
        "TransIP firewall IP sync started"
    )

    logging.info(
        "Configuration: IP_CHECK_INTERVAL=%ss TRANSIP_UPDATE_COOLDOWN=%ss",
        IP_CHECK_INTERVAL,
        TRANSIP_UPDATE_COOLDOWN,
    )

    while True:
        try:
            check_ip()

        except Exception as e:
            logging.exception(
                "IP check cycle failed: %s",
                e,
            )

        time.sleep(IP_CHECK_INTERVAL)


if __name__ == "__main__":
    main()