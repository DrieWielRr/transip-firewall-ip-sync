import logging
import os
import time

from ipcheck import get_public_ip
from state import get_last_ip, set_last_ip


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


IP_CHECK_INTERVAL = int(
    os.getenv("IP_CHECK_INTERVAL", "30")
)

TRANSIP_UPDATE_COOLDOWN = int(
    os.getenv("TRANSIP_UPDATE_COOLDOWN", "300")
)


def check_ip():
    current_ip = get_public_ip()
    last_ip = get_last_ip()

    if last_ip is None:
        logging.info(
            "No previous IP found. Saving current IP: %s",
            current_ip,
        )

        set_last_ip(current_ip)
        return

    if current_ip != last_ip:
        logging.info(
            "Public IP changed: %s -> %s",
            last_ip,
            current_ip,
        )

        set_last_ip(current_ip)

    else:
        logging.info(
            "Public IP unchanged: %s",
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