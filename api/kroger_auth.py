"""
Utility module that loads in the Kroger API secrets.

Used by kroger_shopping_cart and kroger_store_locator.
"""
from pathlib import Path
from dotenv import load_dotenv
from kroger_api.utils.env import load_and_validate_env

ENV_LOADED = False


def init_kroger_env() -> None:
    """
    Load and validate Kroger credentials exactly once.

    Safe to call multiple times.

    :return: None
    """
    global ENV_LOADED # pylint: disable=global-statement

    if ENV_LOADED:
        return

    # project_root/.env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    load_and_validate_env([
        "KROGER_CLIENT_ID",
        "KROGER_CLIENT_SECRET",
    ])

    # print("CREDENTIALS LOADED")

    ENV_LOADED = True
