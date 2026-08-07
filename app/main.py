import logging
import os
import time

from ipcheck import get_public_ip
from sync import sync_firewall, sync_dns, can_sync
from state import get_last_sync, update_sync

from config import (
    IP_CHECK_INTERVAL,
    TRANSIP_UPDATE_COOLDOWN,
    TRANSIP_FIREWALL_RULES,
    TRANSIP_UPDATE_DNS,
    TRANSIP_DNS_RECORDS,
    TRANSIP_DNS_TTL,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


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

    private_key_file = os.getenv(
        "TRANSIP_PRIVATE_KEY_FILE",
        "/config/transip_private_key.pem",
    )

    logging.info(
        "TransIP configuration: account=%s vps=%s private_key_file=%s exists=%s",
        mask_value(
            os.getenv("TRANSIP_ACCOUNT_NAME")
        ),
        mask_value(
            os.getenv("TRANSIP_VPS_NAME")
        ),
        private_key_file,
        os.path.exists(private_key_file),
    )

    logging.info(
        "TransIP firewall rules: %s",
        ", ".join(TRANSIP_FIREWALL_RULES)
        if TRANSIP_FIREWALL_RULES
        else "<none>",
    )

    logging.info(
        "TransIP update DNS: %s",
        TRANSIP_UPDATE_DNS,
    )

    logging.info(
        "TransIP firewall rules: %s",
        ", ".join(TRANSIP_FIREWALL_RULES)
        if TRANSIP_FIREWALL_RULES
        else "<none>",
    )

    logging.info(
        "TransIP DNS records: %s",
        ", ".join(
            f"{domain}=[{', '.join(records)}]"
            for domain, records in TRANSIP_DNS_RECORDS.items()
        )
        if TRANSIP_DNS_RECORDS
        else "<none>",
    )

    logging.info(
        "TransIP DNS TTL: %s",
        TRANSIP_DNS_TTL,
    )


def check_ip():
    current_ip = get_public_ip()
    last_sync = get_last_sync()

    if last_sync is None:
        logging.info(
            "No previous synchronization found"
        )

        firewall_ok = sync_firewall(current_ip)
        dns_ok = sync_dns(current_ip)

        if firewall_ok and dns_ok:
            update_sync(current_ip)

        return

    last_ip = last_sync.get("ip")

    if current_ip != last_ip:
        logging.info(
            "IP change detected: %s -> %s",
            last_ip,
            current_ip,
        )

        if not can_sync():
            return

        firewall_ok = sync_firewall(current_ip)
        dns_ok = sync_dns(current_ip)

        if firewall_ok and dns_ok:
            update_sync(current_ip)


def main():
    logging.info(
        "TransIP IP syncer started"
    )

    log_configuration()

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