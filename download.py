# downloader.py
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Internal
from config import MAX_WORKERS
import db
import storage
from retry import retry

logger = logging.getLogger(__name__)

# Chunk size for writing files to disk - 1MB at a time
CHUNK_SIZE = 1024 * 1024

# ------------------------------------------------------------------ #
# Private                                                             #
# ------------------------------------------------------------------ #

@retry
def _download_single(video: dict):
    # Downloads one video file to disk
    # Called by each worker in the thread pool

    video_id = video["id"]
    url = video["download_url"]

    # Build the destination path and create the folder
    file_path = storage.build_video_path(video)
    storage.ensure_directory(file_path.parent)

    # Mark as downloading in the database
    db.update_status(video_id, "downloading")

    logger.info("Starting download: %s", video_id)

    # Make the HTTP request to Kaltura
    # stream=True means the response body is not loaded all at once
    # it flows in as we read it chunk by chunk
    response = requests.get(url, stream=True, timeout=60)

    # Raise an error if Kaltura returned a bad status code
    response.raise_for_status()

    # Write the file to disk one chunk at a time
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    # Record the file path and mark as completed
    db.update_local_path(video_id, str(file_path))

    logger.info("Completed: %s -> %s", video_id, file_path)

 
def _handle_failed(video: dict, error: Exception):
    # Called when all retries are exhausted for a video
    # Marks it as failed in the database so it gets retried next run
    db.update_status(video["id"], "failed")
    logger.error("Failed permanently: %s - %s", video["id"], str(error))


# ------------------------------------------------------------------ #
# Public                                                              #
# ------------------------------------------------------------------ #

def run_downloads():
    # Entry point called by main.py
    # Fetches all pending videos and downloads them concurrently

    pending_videos = db.get_pending_videos()

    if not pending_videos:
        logger.info("No pending videos found - nothing to download")
        return

    logger.info("Starting downloads - %d videos pending", len(pending_videos))

    # ThreadPoolExecutor creates a pool of MAX_WORKERS workers
    # each worker runs _download_single on a different video simultaneously
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        # Submit every video to the pool as a separate task
        # futures is a dictionary mapping each task to its video
        futures = {
            executor.submit(_download_single, video): video
            for video in pending_videos
        }

        # as_completed yields each future as it finishes
        # regardless of the order they were submitted
        for future in as_completed(futures):
            video = futures[future]
            try:
                future.result()
            except Exception as e:
                _handle_failed(video, e)

    logger.info("Download session complete")
    stats = db.get_stats()
    logger.info("Final stats: %s", stats)