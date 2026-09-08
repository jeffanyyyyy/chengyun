#!/usr/bin/env python3
"""Static server for the Budarina page.

`python3 -m http.server` answers every Range request with the whole file and a
plain 200. Safari treats that as a broken source and refuses to play the video
at all, so the reel silently falls back to the generated canvas. This serves
the 206 Partial Content responses that video playback actually needs, and it
threads, because a video element opens several connections at once.

    python3 serve.py          # http://localhost:8080
    python3 serve.py 8081     # a different port, if 8080 is taken
"""

import http.server
import os
import re
import socketserver
import sys

RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)\s*$")


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    range_remaining = None

    def send_head(self):
        header = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not header or os.path.isdir(path):
            return super().send_head()

        match = RANGE_RE.fullmatch(header.strip())
        if not match:
            return super().send_head()

        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        size = os.fstat(f.fileno()).st_size
        first, last = match.group(1), match.group(2)

        if first == "":                      # "bytes=-500" means the last 500 bytes
            if last == "":
                f.close()
                self.send_error(400, "Malformed Range header")
                return None
            start = max(0, size - int(last))
            end = size - 1
        else:
            start = int(first)
            end = int(last) if last else size - 1
            end = min(end, size - 1)

        if start >= size or start > end:
            f.close()
            self.send_response(416, "Requested Range Not Satisfiable")
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        self.send_response(206, "Partial Content")
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()

        f.seek(start)
        self.range_remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = self.range_remaining
        if remaining is None:
            return super().copyfile(source, outputfile)
        self.range_remaining = None
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        with Server(("127.0.0.1", port), RangeHandler) as httpd:
            print(f"\n  Budarina  ->  http://localhost:{port}/")
            print("  Leave this window open. Press Control + C to stop.\n")
            httpd.serve_forever()
    except OSError as err:
        print(f"\n  Could not use port {port}: {err}")
        print(f"  Something else is probably using it. Try: python3 serve.py {port + 1}\n")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n  Stopped.\n")


if __name__ == "__main__":
    main()
