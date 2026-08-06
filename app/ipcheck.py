import ipaddress
import logging
import requests


IP_PROVIDERS = [
    "https://checkip.amazonaws.com",
    "https://api.ipify.org",
    "https://ifconfig.me/ip",
    "https://icanhazip.com",
]


HEADERS = {
    "User-Agent": "transip-firewall-ip-sync"
}


def get_public_ip():
    """
    Try multiple public IP providers.
    Return the first valid IPv4 address found.
    """

    for provider in IP_PROVIDERS:
        try:
            logging.debug("Checking public IP using %s", provider)

            response = requests.get(
                provider,
                headers=HEADERS,
                timeout=(2, 5)
            )

            response.raise_for_status()

            ip = response.text.strip()

            if is_valid_ip(ip):
                logging.info(
                    "Public IP detected: %s (source: %s)",
                    ip,
                    provider,
                )
                return ip

            logging.warning(
                "Invalid IP returned by %s: %s",
                provider,
                ip,
            )

        except requests.RequestException as e:
            logging.warning(
                "IP provider failed (%s): %s",
                provider,
                e,
            )

    raise RuntimeError("Unable to determine public IP")


def is_valid_ip(ip):
    try:
        address = ipaddress.ip_address(ip)
        return isinstance(address, ipaddress.IPv4Address)

    except ValueError:
        return False