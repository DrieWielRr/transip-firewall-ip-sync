import base64
import json
import logging
import os
import time
import uuid

import requests

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


TRANSIP_API_URL = "https://api.transip.nl/v6/auth"

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
            "label": "transip-firewall-ip-sync",
            "global_key": True,
        }

        payload = json.dumps(
            request_body,
            separators=(",", ":"),
        )

        signature = self._create_signature(
            payload
        )

        response = requests.post(
            TRANSIP_API_URL,
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

        return (
            token,
            time.time() + 1800,
        )