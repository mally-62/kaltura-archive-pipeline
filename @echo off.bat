@echo off
cd /d D:\kaltura_archive
start "" "http://localhost:8000/search.html"
python -m http.server 8000