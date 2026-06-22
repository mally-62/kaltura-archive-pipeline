# fetcher.py
import logging
from datetime import datetime

# Internal - our own files, no install needed
from config import PAGE_SIZE, FILTER_DATE_TO
from auth import KalturaAuth

# Kaltura official Python client - pip install KalturaApiClient
from KalturaClient.Plugins.Core import (
    KalturaMediaEntryFilter,      # filters which videos to retrieve
    KalturaFilterPager,           # controls pagination
    KalturaMediaEntryOrderBy,     # defines sort order
)

# Logger named after this file
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Helper                                                               #
# ------------------------------------------------------------------ #

def _parse_date(kaltura_timestamp):
    # Kaltura stores dates as Unix timestamps (large integers)
    # This converts them to readable strings like "2021-09-01"
    if kaltura_timestamp is None:
        return None
    return datetime.utcfromtimestamp(kaltura_timestamp).strftime("%Y-%m-%d")

def _date_to_timestamp(date_string):
    # Converts "2024-12-31" from .env into a Unix timestamp
    # Kaltura's filter only understands Unix timestamps not date strings
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    return int(dt.timestamp())

# ------------------------------------------------------------------ #
# Main fetcher function                                                #
# ------------------------------------------------------------------ #

def fetch_all_videos(auth: KalturaAuth) -> list:
    """
    Fetches all video records from Kaltura created on or before FILTER_DATE_TO.
    Returns a list of dictionaries, one per video.
    """
    client = auth.get_client()

    # --- Filter setup ---
    # KalturaMediaEntryFilter is Kaltura's own class
    # We configure it to only return videos up to December 31st 2024
    filter = KalturaMediaEntryFilter()
    filter.createdAtLessThanOrEqual = _date_to_timestamp(FILTER_DATE_TO)
    filter.orderBy = KalturaMediaEntryOrderBy.CREATED_AT_ASC  # oldest first

    # --- Pagination setup ---
    # KalturaFilterPager is Kaltura's own class
    # pageSize comes from your .env via config.py
    pager = KalturaFilterPager()
    pager.pageSize = PAGE_SIZE
    pager.pageIndex = 1  # Kaltura pages start at 1 not 0

    all_videos = []   # this list will hold every video record we retrieve
    total_fetched = 0

    logger.info("Starting video fetch - filter up to %s", FILTER_DATE_TO)

    while True:
        # Tell the user which page we are on
        print(f"Fetching page {pager.pageIndex} | Videos retrieved so far: {total_fetched}")

        # --- The actual API call ---
        # client.media is the Kaltura media service built into KalturaClient
        # .list() takes our filter and pager and returns a page of results
        result = client.media.list(filter, pager)

        # result.objects is the list of video entries Kaltura returned
        # result.totalCount is the total number of videos matching our filter
        entries = result.objects

        # If Kaltura returns nothing we have reached the end
        if not entries:
            print("No more videos found - fetch complete")
            break

        # Loop through each video entry on this page
        for entry in entries:
            video = {
                "id":           entry.id,
                "title":        entry.name,
                "description":  entry.description,
                "duration":     entry.duration,
                "created_at":   _parse_date(entry.createdAt),
                "download_url": entry.downloadUrl,
                "file_size":    None,
                "owner":        entry.userId,
            }
            all_videos.append(video)

        total_fetched += len(entries)
        logger.info("Page %d fetched - %d videos retrieved so far", pager.pageIndex, total_fetched)

        # If we got fewer results than PAGE_SIZE we are on the last page
        if len(entries) < PAGE_SIZE:
            print(f"Last page reached - total videos fetched: {total_fetched}")
            break

        # Move to the next page
        pager.pageIndex += 1

    logger.info("Fetch complete - total videos retrieved: %d", total_fetched)
    return all_videos