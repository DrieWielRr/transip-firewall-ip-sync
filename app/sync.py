import logging

from datetime import datetime, timezone
from transip import TransIPClient
from state import get_last_sync
from config import TRANSIP_UPDATE_COOLDOWN



def sync_firewall(ip):
    """
    Synchronize firewall with the given IP.
    """

    logging.info(
        "Starting firewall synchronization for %s",
        ip,
    )

    client = TransIPClient()

    if not client.test_connection():
        logging.error(
            "TransIP API connection failed"
        )
        return False

    if not client.update_firewall_ip(ip):
        logging.error(
            "Firewall update failed"
        )
        return False

    logging.info(
        "TransIP firewall synchronization successful"
    )

    return True


def sync_dns(ip):
    """
    Synchronize dns with the given IP.
    """

    logging.info(
        "Starting dns synchronization for %s",
        ip,
    )

    client = TransIPClient()

    if not client.test_connection():
        logging.error(
            "TransIP API connection failed"
        )
        return False

    if not client.update_dns_records(ip):
        logging.error(
            "dns update failed"
        )
        return False

    logging.info(
        "TransIP dns synchronization successful"
    )

    return True



def can_sync():
    """
    Check whether a TransIP update is allowed.
    """

    last_sync = get_last_sync()

    if not last_sync:
        return True

    if last_sync.get("status") != "success":
        return True

    try:
        last_time = datetime.fromisoformat(
            last_sync["timestamp"]
        )
    except (KeyError, ValueError) as e:
        logging.warning(
            "Invalid last sync timestamp: %s",
            e,
        )
        return True

    age = (
        datetime.now(timezone.utc)
        - last_time
    ).total_seconds()

    if age < TRANSIP_UPDATE_COOLDOWN:
        logging.info(
            "TransIP update skipped: cooldown active (%ss remaining)",
            int(TRANSIP_UPDATE_COOLDOWN - age),
        )
        return False

    return True