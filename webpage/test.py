import http.server
import socket
import socketserver
import threading
from zeroconf import ServiceInfo, Zeroconf
import os

# Function to get the local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Define the web server handler
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve the HTML content from a local file
        if self.path == "/":
            self.path = "/index.html"
        try:
            file_path = self.path.lstrip("/")
            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"File not found")

# Get the local IP address
local_ip = get_local_ip()
print(f"Local IP address: {local_ip}")

# Set up the HTTP server
PORT = 80  # Use port 80 for default HTTP access
handler = MyHttpRequestHandler
httpd = socketserver.TCPServer((local_ip, PORT), handler)

# Function to start the web server
def start_server():
    print(f"Serving on {local_ip}:{PORT}")
    httpd.serve_forever()

# Set up mDNS service info
desc = {'path': '/'}
info = ServiceInfo(
    "_http._tcp.local.",
    "dude._http._tcp.local.",
    addresses=[socket.inet_aton(local_ip)],
    port=PORT,
    properties=desc,
    server="dude.local."
)

# Register mDNS service
zeroconf = Zeroconf()
print("Registering mDNS service...")
zeroconf.register_service(info)

# Run the server in a separate thread to allow mDNS to work simultaneously
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

try:
    input("Press enter to exit...\n\n")
finally:
    print("Unregistering mDNS service...")
    zeroconf.unregister_service(info)
    zeroconf.close()
    httpd.shutdown()
