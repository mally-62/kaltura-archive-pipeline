# storage.py
import logging
from pathlib import Path

# Internal
from config import STORAGE_ROOT

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Public                                                              #
# ------------------------------------------------------------------ #

def get_storage_root() -> Path:
    # Returns the base storage path from config
    return Path(STORAGE_ROOT)

def build_video_path(video: dict) -> Path:
    # Takes a video dictionary and returns the full path where the file should be saved
    # Structure: STORAGE_ROOT/videos/YEAR/MONTH/VIDEO_ID.mp4

    # created_at looks like "2017-03-22" - we split it to get year and month
    date_parts = video["created_at"].split("-")
    year = date_parts[0]   # "2017"
    month = date_parts[1]  # "03"

    # Build the folder path
    folder = get_storage_root() / "videos" / year / month

    # Build the full file path using the Kaltura video ID as the filename
    file_path = folder / f"{video['id']}.mp4"

    logger.debug("Built path for video %s: %s", video["id"], file_path)

    return file_path

def ensure_directory(path: Path):
    # Creates the folder at the given path if it does not already exist
    # parents=True creates any missing parent folders along the way
    # exist_ok=True means no crash if the folder already exists
    path.mkdir(parents=True, exist_ok=True)
    logger.debug("Directory ready: %s", path)