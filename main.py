import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os
import json

HOST = ""
PORT = 3000

SOCKET_SERVER_HOST = os.environ.get("SOCKET_SERVER_HOST", "socket_server")
SOCKET_SERVER_PORT = int(os.environ.get("SOCKET_SERVER_PORT", "5000"))


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"

        elif self.path == "/message.html":
            self.path = "/message.html"

        if (
            self.path.endswith(".html")
            or self.path.endswith(".css")
            or self.path.endswith(".png")
        ):
            try:
                mimetype = "text/html"
                if self.path.endswith(".css"):
                    mimetype = "text/css"
                elif self.path.endswith(".png"):
                    mimetype = "image/png"

                with open("." + self.path, "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", mimetype)
                    self.end_headers()
                    self.wfile.write(file.read())
            except IOError:
                self.send_error(404, "File Not Found")
                with open("./error.html", "rb") as file:
                    self.wfile.write(file.read())
        else:
            self.send_error(404, "File Not Found")
            with open("./error.html", "rb") as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = parse_qs(post_data.decode("utf-8"))
            username = data.get("username", [""])[0]
            message = data.get("message", [""])[0]

            # Send data to Socket server
            send_to_socket_server({"username": username, "message": message})

            # Redirect to thank you page or home
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404, "File Not Found")
            with open("./error.html", "rb") as file:
                self.wfile.write(file.read())


def run_http_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting HTTP server on port {PORT}...")
    httpd.serve_forever()


def send_to_socket_server(data):
    protocol = os.environ.get("PROTOCOL", "TCP")

    try:
        if protocol == "TCP":
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SOCKET_SERVER_HOST, SOCKET_SERVER_PORT))
                s.sendall(str(data).encode("utf-8"))
                # Receive response from the server
                response = s.recv(1024)
                if response == b"OK":
                    print(
                        "✅ Data sent successfully and received OK status from server"
                    )
                else:
                    print("❌ Error occurred while sending data")
                s.close()
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(
                    str(data).encode("utf-8"), (SOCKET_SERVER_HOST, SOCKET_SERVER_PORT)
                )
    except ConnectionRefusedError as e:
        print("Could not connect to the Socket server. Please ensure it is running:", e)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_http_server()
