# config.py
import os
from dotenv import load_dotenv  # pip install python-dotenv

# Loads all key=value pairs from .env into the process environment
load_dotenv()

# ------------------------------------------------------------------ #
# Validation                                                           #
# ------------------------------------------------------------------ #

# These variables are non-negotiable — the pipeline cannot run without them
_REQUIRED = [
    "KALTURA_PARTNER_ID",
    "KALTURA_ADMIN_SECRET",
    "KALTURA_SERVICE_URL",
    "STORAGE_ROOT",
    "DB_PATH",
    "FILTER_DATE_TO",
    "LOG_PATH",
]

_missing = [var for var in _REQUIRED if not os.getenv(var)]
if _missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(_missing)}\n"
        f"Check your .env file."
    )

# ------------------------------------------------------------------ #
# Kaltura — uses the official KalturaApiClient library                 #
# pip install KalturaApiClient                                         #
# ------------------------------------------------------------------ #

PARTNER_ID       = int(os.getenv("KALTURA_PARTNER_ID"))
ADMIN_SECRET     = os.getenv("KALTURA_ADMIN_SECRET")
SERVICE_URL      = os.getenv("KALTURA_SERVICE_URL")
SESSION_DURATION = int(os.getenv("KALTURA_SESSION_DURATION", 86400))

# ------------------------------------------------------------------ #
# Storage — local hardware paths                                       #
# No external library, handled by Python's built-in os and pathlib    #
# ------------------------------------------------------------------ #

STORAGE_ROOT = os.getenv("STORAGE_ROOT")
DB_PATH      = os.getenv("DB_PATH")

# ------------------------------------------------------------------ #
# Pipeline tuning                                                      #
# ------------------------------------------------------------------ #

MAX_WORKERS  = int(os.getenv("MAX_WORKERS", 4))    # concurrent downloads
PAGE_SIZE    = int(os.getenv("PAGE_SIZE", 500))     # videos per API page
#DAILY_LIMIT  = int(os.getenv("DAILY_LIMIT", 20000)) # max downloads per day
FILTER_DATE_TO = os.getenv("FILTER_DATE_TO")

# log file
LOG_PATH = os.getenv("LOG_PATH")
