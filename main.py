# main.py
import json
import logging
from pathlib import Path

# Internal
import logger
import auth
import fetcher
import db
import download
from config import STORAGE_ROOT

# ------------------------------------------------------------------ #
# JSON export                                                         #
# ------------------------------------------------------------------ #

def _export_to_json():
    # Reads all completed videos from the database
    # and writes them to videos.json on the drive

    conn = db._get_connection()
    try:
        cursor = conn.execute("""
            SELECT id, title, owner, created_at, duration, local_path
            FROM videos
            WHERE status = 'completed'
        """)
        rows = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    # Strip the absolute path down to a relative path
    # so search.html works regardless of drive letter
    for row in rows:
        if row["local_path"]:
            path = Path(row["local_path"])
            storage_root = Path(STORAGE_ROOT)
            row["path"] = str(path.relative_to(storage_root)).replace("\\", "/")
        del row["local_path"]

    # Write videos.json to the root of the drive
    output_path = Path(STORAGE_ROOT) / "videos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    logging.info("Exported %d completed videos to %s", len(rows), output_path)


# ------------------------------------------------------------------ #
# Main pipeline                                                       #
# ------------------------------------------------------------------ #

def main():
    # Step 1 - initialize logging first before anything else
    logger.setup_logging()
    logging.info("Pipeline started")

    # Step 2 - authenticate with Kaltura
    kaltura_auth = auth.KalturaAuth()
    kaltura_auth.get_client()
    logging.info("Authentication successful")

    # Step 3 - fetch all video metadata from Kaltura
    videos = fetcher.fetch_all_videos(kaltura_auth)
    logging.info("Fetched %d video records", len(videos))

    # Step 4 - create the database table if it does not exist
    db.create_table()

    # Step 5 - insert all records into the database
    db.insert_videos(videos)

    # Step 6 - reset stuck downloads
    db.reset_stuck_downloads()
    
    # Step 7 - run all downloads
    download.run_downloads()

    # Step 8 - export completed videos to JSON for search.html
    _export_to_json()

    logging.info("Pipeline complete")
    stats = db.get_stats()
    logging.info("Final stats: %s", stats)


if __name__ == "__main__":
    main()