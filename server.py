# server.py
import http.server
import os
import socketserver
import webbrowser
import threading
from urllib.parse import urlparse, parse_qs, unquote

class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Check if this is an open request from the Open button
        if self.path.startswith('/open?path='):
            # Extract the file path from the URL
            query = urlparse(self.path).query
            params = parse_qs(query)
            relative_path = unquote(params.get('path', [''])[0])

            # Build the full path on the drive
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
            full_path = os.path.normpath(full_path)

            # Open with default video player
            if os.path.exists(full_path):
                os.startfile(full_path)
                self.send_response(200)
                self.end_headers()
            else:
                self.send_error(404, "File not found")
            return

        # Everything else handled normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def send_head(self):
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            return http.server.SimpleHTTPRequestHandler.send_head(self)

        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None

        file_size = os.path.getsize(path)
        range_header = self.headers.get('Range')

        if range_header:
            byte_range = range_header.strip().replace('bytes=', '')
            start_str, end_str = byte_range.split('-')
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            end = min(end, file_size - 1)
            chunk_size = end - start + 1
            f.seek(start)
            self.send_response(206)
            self.send_header('Content-Type', self.guess_type(path))
            self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
            self.send_header('Content-Length', str(chunk_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            self.wfile.write(f.read(chunk_size))
            f.close()
            return None
        else:
            self.send_response(200)
            self.send_header('Content-Type', self.guess_type(path))
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            return f

    def log_message(self, format, *args):
        pass

def open_browser():
    webbrowser.open("http://localhost:8080/search.html")

PORT = 8080
print("Starting Kaltura Archive...")
threading.Timer(1.5, open_browser).start()

with socketserver.TCPServer(("", PORT), RangeRequestHandler) as httpd:
    print("Server running. Close this window to stop.")
    httpd.serve_forever()