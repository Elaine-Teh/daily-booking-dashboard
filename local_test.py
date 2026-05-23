import http.server, socketserver, os

os.chdir(r'c:\Users\elaineteh\WorkBuddy\20260522180506\daily-booking-dashboard')

PORT = 8765
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}/")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()
