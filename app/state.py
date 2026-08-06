import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path


STATE_FILE = Path(
    os.getenv("STATE_FILE", "/data/state.json")
)


def load_state():
    """
    Load state from JSON file.
    Returns an empty dictionary if no state exists.
    """

    if not STATE_FILE.exists():
        logging.info("No state file found, starting fresh")
        return {}

    try:
        with STATE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError) as e:
        logging.warning(
            "Unable to read state file %s: %s",
            STATE_FILE,
            e,
        )
        return {}


def save_state(state):
    """
    Save state to JSON file.
    """

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=2,
        )


def get_last_ip():
    state = load_state()
    return state.get("last_ip")


def set_last_ip(ip):
    state = load_state()

    old_ip = state.get("last_ip")

    state["last_ip"] = ip

    if old_ip and old_ip != ip:
        state["last_ip_change"] = {
            "old_ip": old_ip,
            "new_ip": ip,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        logging.info(
            "IP change detected: %s -> %s",
            old_ip,
            ip,
        )

    save_state(state)