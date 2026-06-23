# Kaltura Video Migration Pipeline

> Automated ETL pipeline to archive an institutional video collection of 38,000+ videos from Kaltura to local hardware storage, with a queryable metadata database and a browser-based search interface.

**99.12% success rate — 5,642 videos successfully archived in pilot run**

---

## Background

Oral Roberts University Library manages a Kaltura video collection spanning over 38,000 videos accumulated since 2017. Ahead of an institutional deadline, the library needed a cost-effective technical solution to migrate this collection — including all video files and their metadata — to local hardware storage for long-term preservation.

This pipeline was designed and built from scratch by a freshman student to automate that migration entirely. According to the supervising librarian, the solution enabled the library to meet its deadline *"efficiently and at a fraction of the cost of alternative approaches."*

---

## What It Does

- Authenticates with the Kaltura API and retrieves metadata for every video in the collection
- Filters by date range and downloads video files concurrently to an external hard drive
- Stores all metadata in a local SQLite database indexed by Kaltura video ID
- Tracks download status per video — enabling the pipeline to resume after crashes without re-downloading completed files
- Exports metadata to JSON for use by the search interface
- Provides a browser-based search UI that lets users find and play any archived video locally

---

## Architecture

```
project/
├── .env                  # credentials and configuration (never committed)
├── config.py             # loads .env, validates required variables, exposes constants
├── auth.py               # Kaltura session management and token refresh
├── fetcher.py            # paginates Kaltura API, retrieves video metadata
├── db.py                 # SQLite database — schema, inserts, status tracking
├── storage.py            # directory structure and file path management on hardware
├── retry.py              # retry decorator with backoff for failed API calls
├── logger.py             # centralized logging configuration
├── downloader.py         # concurrent video downloads via ThreadPoolExecutor
├── main.py               # orchestrates the full pipeline
│
├── search.html           # browser-based search interface
├── videos.json           # metadata export powering the UI
├── server.py             # local server bridging the UI to files on the drive
└── start.bat             # launches the search interface on Windows
```

---

## Pipeline Logic

| File | Role |
|---|---|
| `.env` | Stores all sensitive credentials and configuration — never committed to version control |
| `config.py` | Translates `.env` into Python constants. Crashes immediately with a clear message if anything required is missing |
| `auth.py` | Authenticates with Kaltura, manages the session token, and silently refreshes it before expiry |
| `fetcher.py` | Calls the Kaltura API, paginates through the full video catalog, and retrieves metadata for each entry |
| `db.py` | Creates and manages the SQLite database. Tracks each video's download status — pending, downloading, completed, failed |
| `storage.py` | Creates the folder structure on the external drive and manages file path assignments |
| `retry.py` | Wraps API and download calls with retry logic and exponential backoff |
| `logger.py` | Configures centralized logging across all modules |
| `downloader.py` | Downloads video files concurrently using `MAX_WORKERS` parallel threads |
| `main.py` | Orchestrates the full pipeline from authentication to a completed, indexed archive |

---

## Search Interface

Outside the core pipeline, four additional files power a local browser-based search UI:

- **`search.html`** — the web interface where users search and play videos
- **`videos.json`** — metadata export connecting all video records to the UI
- **`index.db`** — the SQLite database containing all metadata
- **`server.py`** — local server that bridges the browser interface to video files on the drive
- **`start.bat`** — Windows batch file that launches the interface, bypassing Chrome's local file restrictions

---

## Setup

### Requirements
- Python 3.x
- An IDE (Visual Studio Code recommended)

### Install dependencies
```bash
pip install KalturaApiClient
pip install lxml
pip install python-dotenv
pip install requests
```

All other libraries used (`sqlite3`, `logging`, `pathlib`, `json`, `time`, `functools`, `concurrent.futures`, `os`) are native to Python 3 — no additional installation required.

### Configure `.env`
Create a `.env` file at the project root with the following:
```
KALTURA_PARTNER_ID=your_partner_id
KALTURA_ADMIN_SECRET=your_admin_secret
KALTURA_SERVICE_URL=https://www.kaltura.com
KALTURA_SESSION_DURATION=86400
STORAGE_ROOT=D:\kaltura_archive
DB_PATH=D:\kaltura_archive\index.db
MAX_WORKERS=5
PAGE_SIZE=500
DAILY_LIMIT=22000
FILTER_DATE_TO=2017-12-31
```

> **The UI is locally hosted and requires the Hard drive as a gateway**

---

## Pilot Run Results

The pilot scoped to 2017 content — 5,692 videos.

```
Date completed : 2026-06-05
Total entries  : 5,692
Completed      : 5,642
Failed         : 43
Pending        : 0


Success rate   : 99.12%
Failure rate   : 0.88%
```

Post-run review confirmed that the majority of failed downloads are attributable to invalid URLs originating from Kaltura's ecosystem — not pipeline errors.

---

## Known Limitations

- A small number of videos in the Kaltura catalog are corrupted or audio-only files. These are passed through from Kaltura and cannot be resolved at the pipeline level.
- The search interface displays and plays videos through the system's default video player but does not support direct download from the UI. To download a specific video, retrieve its ID from the interface and locate it on the external drive.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| External API | Kaltura API via `KalturaApiClient` |
| Database | SQLite via `sqlite3` |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| Configuration | `python-dotenv` |
| Frontend | HTML, JavaScript |
| Logging | Python `logging` |

---

## Context

This pipeline was built as part of a real institutional archival project at Oral Roberts University Library. The pilot covers content from 2015 to 2017 (~3.7TB). The full collection spans 38,000+ videos across multiple years and represents a long-term preservation initiative.

---

*Built by a freshman. Runs in production.*
