"""
config.py — Central configuration loader for FitHer Gym Manager.
Reads database credentials from the .env file using python-dotenv.
Never hardcode credentials here.
"""

import os
from dotenv import load_dotenv

# Load .env file from the project root (one level up from this file if needed)
load_dotenv()


def get_db_config() -> dict:
    """
    Return a dictionary of MySQL connection parameters loaded from environment
    variables.  Raises a clear error if required variables are missing.
    """
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please copy .env.example to .env and fill in your credentials."
        )

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME", "fither_gym"),
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": False,
        "connection_timeout": 10,
    }


# Application-level constants
APP_TITLE = "FitHer Gym Manager"
APP_VERSION = "1.0.0 — Phase 1 Prototype"
APP_ICON = "💪"
DEMO_MODE = True   # Label the app as a local demo; no login implemented

# Business rules
EXPIRY_WARNING_DAYS = 7       # Show warning for memberships expiring within N days
DEFAULT_GENDER = "Female"     # Sensible default for this female-only gym
PAYMENT_METHODS = ["Cash", "Bank Transfer", "Other"]
SUBSCRIPTION_STATUSES = ["active", "expired", "cancelled"]
