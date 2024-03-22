import urllib.parse
import mimetypes
import json
import socket
import logging

from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

from variables import *


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urllib.parse.urlparse(self.path).path
        match request:
            case "/":
                self.send_html("index.html")
            case "/message"|"/message.html":
                self.send_html("message.html")
            case "/error"|"/error.html":
                self.send_html("error.html")
            case _:
                file = BASE_PATH / 'assets' / request[1:]
                print(f"doGET, case: _, file: {file}")
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("error.html", status=404)


    def do_POST(self):
        request = urllib.parse.urlparse(self.path).path
        match request:
            case "/message":
                size = int(self.headers.get("Content-Length"))
                data = self.rfile.read(size).decode()
                if data:
                    Thread(target=self.send_message, args=(data,)).start()
                    # self.save_message(data)

                self.send_html("message.html")
            case _:
                self.send_html("error.html", status=404)
    

    def send_headers(self, status=200, content_type="text/html"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()


    def send_html(self, filename, status=200):
        self.send_headers(status, "text/html")
        file = BASE_PATH / 'html' / filename
        logging.info(f"send_html, file: {file}")
        with open(file, "rb") as f:
            self.wfile.write(f.read())


    def send_static(self, filename, status=200):
        mime_type = mimetypes.guess_type(filename)[0] if mimetypes.guess_type(filename) else "text/plain"
        self.send_headers(status, mime_type)
        with open(filename, "rb") as f:
            self.wfile.write(f.read())
    

    def send_message(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port_ws = int(config.get("WS_PORT", 5000))
            host_ws = config.get("WS_HOST", "")

            data = {pair.split("=")[0]: pair.split("=")[1] for pair in data.split("&")}
            data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

            try:
                s.connect((host_ws, port_ws))
                s.send(config.get("WS_SECRET", "secret").encode())
            except Exception as e:
                logging.error(f"Failed to connect to websocket server: {e}")
                return

            response = s.recv(32).decode()
            if response != config.get("WS_ACK", "secret"):
                logging.error(f"Failed to authenticate with websocket server")
                return
            
            s.send(json.dumps(data).encode())
        logging.info(f"Sent data {json.dumps(data)} to websocket server")


def start_http_server():
    host_http = config.get("HTTP_HOST", "")
    port_http = int(config.get("HTTP_PORT", 3000))

    httpd = HTTPServer((host_http, port_http), HttpHandler)
    try:
        logging.info(f"HTTP server started at http://{host_http if host_http else '*'}:{port_http}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping HTTP server")
    finally:
        logging.warning('HTTP server closed')
        httpd.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    start_http_server()