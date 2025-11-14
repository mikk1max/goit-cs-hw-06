import mimetypes
import socket
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import config


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path).path

        if parsed_path == "/":
            self.send_html_file("index.html")
        elif parsed_path == "/message.html":
            self.send_html_file("message.html")
        else:
            static_file = Path(parsed_path[1:])
            if static_file.exists():
                self.send_static_file(static_file)
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        if self.path == "/message":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length).decode("utf-8")
                form_data = parse_qs(post_data)

                message_data = {
                    "username": form_data.get("username", [""])[0],
                    "message": form_data.get("message", [""])[0],
                }

                self.send_to_socket_server(message_data)

                self.send_response(302)
                self.send_header("Location", "/message.html")
                self.end_headers()

            except Exception as e:
                logging.error(f"Помилка обробки POST-запиту: {e}")
                self.send_html_file("error.html", 500)
        else:
            self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            with open(filename, "rb") as f:
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.wfile.write(b"File not found")

    def send_static_file(self, filepath, status=200):
        self.send_response(status)
        mime_type, _ = mimetypes.guess_type(str(filepath))
        if mime_type:
            self.send_header("Content-type", mime_type)
        else:
            self.send_header("Content-type", "application/octet-stream")
        self.end_headers()
        try:
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.wfile.write(b"File not found")

    def send_to_socket_server(self, data):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Використовуємо 127.0.0.1 (localhost) для відправки всередині контейнера
        client_socket.sendto(
            json.dumps(data).encode("utf-8"), ("127.0.0.1", config.SOCKET_PORT)
        )
        client_socket.close()


def run_http_server():
    server_address = (config.HTTP_HOST, config.HTTP_PORT)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    logging.info(f"HTTP-сервер запущено на {config.HTTP_HOST}:{config.HTTP_PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        logging.info("HTTP-сервер зупинено.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    run_http_server()
