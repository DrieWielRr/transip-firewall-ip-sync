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

    try:
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

    except OSError as e:
        logging.error(
            "Unable to save state file %s: %s",
            STATE_FILE,
            e,
        )


def get_last_sync():
    """
    Return the last successful synchronization data.
    """

    state = load_state()

    return state.get("last_sync")


def update_sync(ip):
    """
    Store a successful TransIP synchronization.
    """

    state = load_state()

    previous_ip = state.get("observed_ip")

    state["observed_ip"] = ip

    if previous_ip and previous_ip != ip:
        state["last_ip_change"] = {
            "old_ip": previous_ip,
            "new_ip": ip,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    state["last_sync"] = {
        "ip": ip,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "success",
    }

    save_state(state)

    return state


def update_sync_failed(ip, error):
    """
    Store a failed synchronization attempt.
    """

    state = load_state()

    state["observed_ip"] = ip

    state["last_sync"] = {
        "ip": state.get("last_sync", {}).get("ip"),
        "attempted_ip": ip,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": "failed",
        "error": error,
    }

    save_state(state)

    return state