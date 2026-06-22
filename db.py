# db.py
import sqlite3
import logging
from datetime import datetime

# Internal - our own config.py, no install needed
from config import DB_PATH

# Logger named after this file
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Connection                                                           #
# ------------------------------------------------------------------ #

def _get_connection():
    # Opens a connection to the SQLite database file at DB_PATH
    # If the file does not exist SQLite creates it automatically
    # check_same_thread=False allows multiple threads to use the connection
    # which is necessary when downloader.py runs concurrent workers
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    # Row factory makes results return as dictionaries instead of tuples
    # so you can access columns by name: row["title"] instead of row[0]
    conn.row_factory = sqlite3.Row
    return conn

# ------------------------------------------------------------------ #
# Table creation                                                       #
# ------------------------------------------------------------------ #

def create_table():
    # Creates the videos table if it does not already exist
    # Running this multiple times is safe - IF NOT EXISTS prevents duplication
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id            TEXT PRIMARY KEY,  -- Kaltura video ID
                title         TEXT,              -- video title
                description   TEXT,              -- video description
                duration      INTEGER,           -- duration in seconds
                created_at    TEXT,              -- date as YYYY-MM-DD
                download_url  TEXT,              -- Kaltura download URL
                file_size_mb  REAL,              -- file size in MB, NULL for now
                owner         TEXT,              -- Kaltura uploader username
                status        TEXT DEFAULT 'pending', -- pending, downloading, completed, failed
                local_path    TEXT,              -- where the file lives on your drive
                downloaded_at TEXT               -- when the download completed
            )
        """)
        conn.commit()
        logger.info("Database table verified at %s", DB_PATH)
    finally:
        conn.close()

# ------------------------------------------------------------------ #
# Insert                                                               #
# ------------------------------------------------------------------ #

def insert_videos(videos: list):
    # Takes the list of video dictionaries from fetcher.py
    # and inserts them all into the database
    # INSERT OR IGNORE skips any video that already exists
    # preventing duplicates if you run fetcher.py more than once
    conn = _get_connection()
    try:
        conn.executemany("""
            INSERT OR IGNORE INTO videos (
                id, title, description, duration,
                created_at, download_url, file_size_mb, owner
            ) VALUES (
                :id, :title, :description, :duration,
                :created_at, :download_url, :file_size, :owner
            )
        """, videos)
        conn.commit()
        logger.info("Inserted %d video records into database", len(videos))
    finally:
        conn.close()

# ------------------------------------------------------------------ #
# Status updates                                                       #
# ------------------------------------------------------------------ #

def update_status(video_id: str, status: str):
    # Updates the status of a single video by its Kaltura ID
    # Called by downloader.py as each download progresses
    conn = _get_connection()
    try:
        conn.execute("""
            UPDATE videos
            SET status = ?
            WHERE id = ?
        """, (status, video_id))
        conn.commit()
        logger.debug("Video %s status updated to %s", video_id, status)
    finally:
        conn.close()

def update_local_path(video_id: str, local_path: str):
    # Records where the video file was saved on your drive
    # and marks the download as completed with a timestamp
    conn = _get_connection()
    try:
        conn.execute("""
            UPDATE videos
            SET local_path    = ?,
                status        = 'completed',
                downloaded_at = ?
            WHERE id = ?
        """, (local_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), video_id))
        conn.commit()
        logger.info("Video %s saved to %s", video_id, local_path)
    finally:
        conn.close()

# ------------------------------------------------------------------ #
# Queries                                                              #
# ------------------------------------------------------------------ #

def get_pending_videos() -> list:
    # Returns all videos that still need to be downloaded
    # includes both pending and failed so failed downloads get retried
    conn = _get_connection()
    try:
        cursor = conn.execute("""
            SELECT * FROM videos
            WHERE status IN ('pending', 'failed')
            ORDER BY created_at ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_stats() -> dict:
    # Returns a summary of the current state of the archive
    # useful for monitoring progress during a long download run
    conn = _get_connection()
    try:
        cursor = conn.execute("""
            SELECT
                COUNT(*)                          AS total,
                SUM(status = 'completed')         AS completed,
                SUM(status = 'pending')           AS pending,
                SUM(status = 'downloading')       AS downloading,
                SUM(status = 'failed')            AS failed
            FROM videos
        """)
        row = dict(cursor.fetchone())
        logger.info("Stats: %s", row)
        return row
    finally:
        conn.close()

def reset_stuck_downloads():
    # Resets any videos stuck as 'downloading' back to 'pending'
    # Called at the start of every pipeline run to handle crashed sessions
    conn = _get_connection()
    try:
        conn.execute("""
            UPDATE videos
            SET status = 'pending'
            WHERE status = 'downloading'
        """)
        conn.commit()
        logger.info("Reset stuck downloads to pending")
    finally:
        conn.close()