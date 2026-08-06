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

    if not client.update_firewall_ip(ip):
        logging.error(
            "Firewall update failed"
        )
        return False

    logging.info(
        "TransIP firewall synchronization successful"
    )

    return True
