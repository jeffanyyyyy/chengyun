"""支援 Range 的靜態伺服器。python 內建的 http.server 不支援 Range，
   <video> 一律用 Range 取片段，所以用內建的那個影片永遠載不起來。"""
import os, re, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class R(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path): return super().send_head()
        rng = self.headers.get('Range')
        if not rng: return super().send_head()
        try: f = open(path, 'rb')
        except OSError: self.send_error(404); return None
        size = os.fstat(f.fileno()).st_size
        m = re.match(r'bytes=(\d*)-(\d*)', rng)
        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end: self.send_error(416); f.close(); return None
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        f.seek(start)
        self._remain = end - start + 1
        return f
    def copyfile(self, src, dst):
        n = getattr(self, '_remain', None)
        if n is None: return super().copyfile(src, dst)
        self._remain = None
        while n > 0:
            buf = src.read(min(65536, n))
            if not buf: break
            dst.write(buf); n -= len(buf)
    def end_headers(self):
        if self.command == 'GET' and not self.headers.get('Range'):
            self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()
    def log_message(self, *a): pass

os.chdir(sys.argv[1])
HTTPServer(('127.0.0.1', int(sys.argv[2])), R).serve_forever()
