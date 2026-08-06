import logging

from transip import TransIPClient


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

    logging.info(
        "TransIP API connection successful"
    )

    return True