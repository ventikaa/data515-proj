from dotenv import load_dotenv
from pathlib import Path
from kroger_api.utils.env import load_and_validate_env

_ENV_LOADED = False


def init_kroger_env() -> None:
    """
    Load and validate Kroger credentials exactly once.
    Safe to call multiple times.
    """
    global _ENV_LOADED

    if _ENV_LOADED:
        return

    # project_root/.env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)

    load_and_validate_env([
        "KROGER_CLIENT_ID",
        "KROGER_CLIENT_SECRET",
    ])

    print("CREDENTIALS LOADED")

    _ENV_LOADED = True