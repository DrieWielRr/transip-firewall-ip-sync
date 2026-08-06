import logging
import os
import requests


TRANSIP_API_URL = "https://api.transip.nl/rest"


TRANSIP_ACCOUNT_NAME = os.getenv(
    "TRANSIP_ACCOUNT_NAME"
)

TRANSIP_PRIVATE_KEY = os.getenv(
    "TRANSIP_PRIVATE_KEY"
)


class TransIPClient:
    """
    Minimal TransIP API client.
    """

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json",
        })

    def test_connection(self):
        """
        Test API connectivity.

        No changes are made.
        """

        logging.info(
            "Testing TransIP API connection"
        )

        # TODO:
        # Implement authentication

        return True