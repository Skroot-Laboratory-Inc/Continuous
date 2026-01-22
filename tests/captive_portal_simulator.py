#!/usr/bin/env python3
"""
Captive Portal Simulator for Testing
Simulates various captive portal authentication scenarios.
Run this in WSL and access from your main application for testing.
"""

import http.server
import socketserver
import urllib.parse
import sys
from pathlib import Path

PORT = 8080

class CaptivePortalHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that simulates various captive portal behaviors"""

    # Simulated user credentials
    VALID_CREDENTIALS = {
        'testuser': 'testpass',
        'netid@iastate.edu': 'password123',
        'student@university.edu': 'mypassword'
    }

    def do_GET(self):
        """Handle GET requests - show login page or redirect"""

        # Parse the path to separate from query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path_only = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Simulate connectivity check redirects
        if path_only in ['/success.txt', '/generate_204', '/hotspot-detect.html']:
            # Redirect to login page (simulating captive portal)
            self.send_response(302)
            self.send_header('Location', f'http://localhost:{PORT}/login')
            self.end_headers()
            return

        # Show login page
        if path_only == '/login' or path_only == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Generate different portal types based on query parameter
            portal_type = query_params.get('type', ['standard'])[0]

            html = self.get_login_page(portal_type)
            self.wfile.write(html.encode())
            return

        # Success page after authentication
        if path_only == '/success':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Connected</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Successfully Authenticated</h1>
                <p>You now have internet access.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return

        # Default 404
        self.send_error(404, "File not found")

    def do_POST(self):
        """Handle POST requests - process login"""

        # Parse the path to separate from query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path_only = parsed_url.path

        if path_only == '/auth' or path_only == '/login':
            # Parse form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)

            # Extract credentials (handle various field names)
            username = (form_data.get('username', [''])[0] or
                       form_data.get('user', [''])[0] or
                       form_data.get('netid', [''])[0])
            password = (form_data.get('password', [''])[0] or
                       form_data.get('pass', [''])[0])

            print(f"\n[AUTH ATTEMPT] Username: {username}, Password: {'*' * len(password)}")

            # Validate credentials
            if username in self.VALID_CREDENTIALS and self.VALID_CREDENTIALS[username] == password:
                print(f"[AUTH SUCCESS] {username} authenticated successfully")

                # Redirect to success page
                self.send_response(302)
                self.send_header('Location', f'http://localhost:{PORT}/success')
                self.end_headers()
            else:
                print(f"[AUTH FAILED] Invalid credentials for {username}")

                # Show error page
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = """
                <!DOCTYPE html>
                <html>
                <head><title>Login Failed</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">✗ Authentication Failed</h1>
                    <p>Invalid username or password.</p>
                    <a href="/login">Try Again</a>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            return

        self.send_error(404, "File not found")

    def get_login_page(self, portal_type='standard'):
        """Generate different types of login pages"""

        if portal_type == 'university':
            # Simulate university-style portal (like Iowa State)
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>University WiFi - Authentication Required</title>
                <style>
                    body { font-family: Arial; background: #f0f0f0; }
                    .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; font-size: 24px; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                    button { width: 100%; padding: 12px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #0052a3; }
                    .info { font-size: 12px; color: #666; margin-top: 15px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎓 University WiFi Login</h1>
                    <p>Please authenticate with your university credentials</p>
                    <form method="POST" action="/auth">
                        <input type="text" name="netid" placeholder="NetID (e.g., netid@iastate.edu)" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <input type="hidden" name="type" value="university">
                        <button type="submit">Login</button>
                    </form>
                    <div class="info">
                        <p><strong>Test Credentials:</strong></p>
                        <p>Username: netid@iastate.edu<br>Password: password123</p>
                    </div>
                </div>
            </body>
            </html>
            """

        elif portal_type == 'simple':
            # Simulate simple accept-terms portal
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Public WiFi - Terms of Service</title>
                <style>
                    body { font-family: Arial; text-align: center; padding: 50px; background: #fff; }
                    button { padding: 15px 30px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #218838; }
                </style>
            </head>
            <body>
                <h1>☕ Welcome to Public WiFi</h1>
                <p>By using this network, you agree to our terms of service.</p>
                <form method="POST" action="/auth">
                    <input type="hidden" name="username" value="guest">
                    <input type="hidden" name="password" value="guest">
                    <button type="submit">Accept and Connect</button>
                </form>
            </body>
            </html>
            """

        else:
            # Standard username/password portal
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WiFi Login Required</title>
                <style>
                    body { font-family: Arial; background: #f5f5f5; }
                    .container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                    button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #0056b3; }
                    .info { font-size: 12px; color: #666; margin-top: 15px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📶 WiFi Authentication</h1>
                    <p>Please login to access the internet</p>
                    <form method="POST" action="/auth">
                        <input type="text" name="username" placeholder="Username" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Connect</button>
                    </form>
                    <div class="info">
                        <p><strong>Test Credentials:</strong></p>
                        <p>Username: testuser<br>Password: testpass</p>
                        <p>or</p>
                        <p>Username: student@university.edu<br>Password: mypassword</p>
                    </div>
                </div>
            </body>
            </html>
            """

    def log_message(self, format, *args):
        """Custom logging"""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_server(port=PORT):
    """Start the captive portal simulator"""

    print("=" * 60)
    print("🌐 CAPTIVE PORTAL SIMULATOR")
    print("=" * 60)
    print(f"\nServer running on http://localhost:{port}")
    print(f"\nAvailable test portals:")
    print(f"  • Standard Portal:    http://localhost:{port}/login")
    print(f"  • University Portal:  http://localhost:{port}/login?type=university")
    print(f"  • Simple Portal:      http://localhost:{port}/login?type=simple")
    print(f"\nValid test credentials:")
    for username, password in CaptivePortalHandler.VALID_CREDENTIALS.items():
        print(f"  • {username} / {password}")
    print(f"\nTo test captive portal detection:")
    print(f"  • Connectivity check URLs will redirect to login page")
    print(f"  • Try: http://localhost:{port}/generate_204")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()

    with socketserver.TCPServer(("", port), CaptivePortalHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)


if __name__ == "__main__":
    # Allow custom port
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
