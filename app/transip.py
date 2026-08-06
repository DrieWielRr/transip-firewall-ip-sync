import logging
import os
import time

import jwt
import requests


TRANSIP_API_URL = "https://api.transip.nl/rest"

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
        Load private key from file.
        """

        if not os.path.exists(
            TRANSIP_PRIVATE_KEY_FILE
        ):
            raise RuntimeError(
                f"TransIP private key file not found: "
                f"{TRANSIP_PRIVATE_KEY_FILE}"
            )

        try:
            with open(
                TRANSIP_PRIVATE_KEY_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                return file.read()

        except OSError as e:
            raise RuntimeError(
                f"Unable to read TransIP private key: {e}"
            )


    def _create_access_token(self):
        """
        Create a new TransIP access token.

        TODO:
        Implement TransIP Key Pair authentication.
        """

        private_key = self._get_private_key()

        logging.info(
            "Creating TransIP access token"
        )

        # Placeholder payload.
        # Will be replaced with TransIP authentication format.

        payload = {
            "login": TRANSIP_ACCOUNT_NAME,
            "nonce": str(time.time()),
        }

        signed_request = jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
        )

        response = requests.post(
            f"{TRANSIP_API_URL}/auth",
            json={
                "token": signed_request,
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        token = data["access_token"]

        expires = time.time() + data.get(
            "expires_in",
            3600,
        )

        return token, expires


    def get_access_token(self):
        """
        Return a valid cached access token.
        """

        if (
            self.access_token
            and time.time() < self.token_expires
        ):
            return self.access_token

        (
            self.access_token,
            self.token_expires,
        ) = self._create_access_token()

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
            f"{TRANSIP_API_URL}/"
        )

        response.raise_for_status()

        return True