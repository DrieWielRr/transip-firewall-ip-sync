import base64
import json
import logging
import os
import time
import uuid

import requests

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from state import (
    clear_access_token,
    get_access_token as get_cached_access_token,
    update_access_token,
)

from config import (
    TRANSIP_FIREWALL_RULES,
    TRANSIP_VPS_NAME,
)

TRANSIP_API_BASE_URL = "https://api.transip.nl/v6"
TRANSIP_AUTH_URL = f"{TRANSIP_API_BASE_URL}/auth"

TRANSIP_ACCOUNT_NAME = os.getenv(
    "TRANSIP_ACCOUNT_NAME"
)

TRANSIP_PRIVATE_KEY_FILE = os.getenv(
    "TRANSIP_PRIVATE_KEY_FILE",
    "/config/transip_private_key.pem",
)


class TransIPClient:
    """
    TransIP REST API client.
    """

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json",
        })

        self.access_token = None
        self.token_expires = 0


    def _get_private_key(self):
        """
        Load TransIP private key.
        """

        try:
            with open(
                TRANSIP_PRIVATE_KEY_FILE,
                "rb",
            ) as file:
                return serialization.load_pem_private_key(
                    file.read(),
                    password=None,
                )

        except Exception as e:
            raise RuntimeError(
                f"Unable to load private key: {e}"
            )


    def _create_signature(self, payload):
        """
        Sign request body using TransIP private key.
        """

        private_key = self._get_private_key()

        signature = private_key.sign(
            payload.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA512(),
        )

        return base64.b64encode(
            signature
        ).decode("ascii")


    def _create_access_token(self):
        """
        Generate a TransIP access token.
        """

        logging.info(
            "Creating TransIP access token"
        )

        request_body = {
            "login": TRANSIP_ACCOUNT_NAME,
            "nonce": uuid.uuid4().hex,
            "read_only": False,
            "expiration_time": "30 minutes",
            "label": (
                "transip-firewall-ip-sync-"
                f"{uuid.uuid4().hex[:8]}"
            ),
            "global_key": True,
        }

        payload = json.dumps(
            request_body,
            separators=(",", ":"),
        )

        signature = self._create_signature(
            payload
        )

        response = self.session.post(
            TRANSIP_AUTH_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Signature": signature,
            },
            timeout=10,
        )

        if not response.ok:
            raise RuntimeError(
                f"TransIP authentication failed "
                f"({response.status_code}): "
                f"{response.text[:500]}"
            )

        data = response.json()

        token = data["token"]
        expires = int(time.time()) + 1800

        return (
            token,
            expires,
        )


    def get_access_token(self):
        """
        Return a valid cached access token.
        """

        now = time.time()

        if (
            self.access_token
            and now < self.token_expires
        ):
            return self.access_token

        cached = get_cached_access_token()

        if (
            cached
            and now < cached.get(
                "expires",
                0,
            )
        ):
            logging.info(
                "Loaded cached TransIP access token"
            )

            self.access_token = cached["token"]
            self.token_expires = cached["expires"]

            return self.access_token

        (
            self.access_token,
            self.token_expires,
        ) = self._create_access_token()

        update_access_token(
            self.access_token,
            self.token_expires,
        )

        return self.access_token


    def test_connection(self):
        """
        Test authenticated API access.

        No firewall changes.
        """

        token = self.get_access_token()

        self.session.headers.update({
            "Authorization": f"Bearer {token}",
        })

        logging.info(
            "Testing TransIP API connection"
        )

        response = self.session.get(
            TRANSIP_API_BASE_URL,
        )

        if response.status_code == 401:
            clear_access_token()

            raise RuntimeError(
                "Cached TransIP access token expired or is invalid"
            )

        if not response.ok:
            raise RuntimeError(
                f"TransIP API connection failed "
                f"({response.status_code}): "
                f"{response.text[:500]}"
            )

        logging.info(
            "TransIP API connection successful"
        )

        return True


    def get_firewall(self):
        """
        Retrieve current VPS firewall configuration.
        """

        token = self.get_access_token()

        self.session.headers.update({
            "Authorization": f"Bearer {token}",
        })

        url = (
            f"{TRANSIP_API_BASE_URL}"
            f"/vps/{TRANSIP_VPS_NAME}/firewall"
        )

        logging.info(
            "Retrieving firewall configuration for %s",
            TRANSIP_VPS_NAME,
        )

        response = self.session.get(
            url,
            timeout=10,
        )

        if response.status_code == 401:
            clear_access_token()

            raise RuntimeError(
                "Cached TransIP access token expired or is invalid"
            )

        if not response.ok:
            raise RuntimeError(
                f"Unable to retrieve firewall "
                f"({response.status_code}): "
                f"{response.text[:500]}"
            )

        return response.json()


    def update_firewall_ip(self, ip):
        """
        Update whitelist IP for configured firewall rules.
        """

        firewall = self.get_firewall()

        rules = firewall["vpsFirewall"]["ruleSet"]

        matched = 0
        updated = 0

        for rule in rules:
            if rule.get("description") not in TRANSIP_FIREWALL_RULES:
                continue

            matched += 1

            desired_whitelist = [
                f"{ip}/32"
            ]

            if rule.get("whitelist") == desired_whitelist:
                logging.info(
                    "Firewall rule '%s' already up-to-date",
                    rule["description"],
                )

                continue

            logging.info(
                "Updating firewall rule '%s' with IP %s",
                rule["description"],
                ip,
            )

            logging.info(
                "Firewall rule '%s' whitelist: %s -> %s",
                rule["description"],
                rule.get("whitelist"),
                desired_whitelist,
            )

            rule["whitelist"] = desired_whitelist

            updated += 1

        if matched == 0:
            available = [
                rule.get("description")
                for rule in rules
            ]

            raise RuntimeError(
                "No matching firewall rules found. "
                f"Configured={TRANSIP_FIREWALL_RULES}, "
                f"Available={available}"
            )

        if updated == 0:
            logging.info(
                "Firewall configuration already up-to-date"
            )

            return True

        response = self.session.put(
            f"{TRANSIP_API_BASE_URL}/vps/{TRANSIP_VPS_NAME}/firewall",
            json=firewall,
            timeout=10,
        )

        if response.status_code == 401:
            clear_access_token()

            raise RuntimeError(
                "Cached TransIP access token expired or is invalid"
            )

        response.raise_for_status()

        logging.info(
            "Updated %s firewall rule(s)",
            updated,
        )

        return True