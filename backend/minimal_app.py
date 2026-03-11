#!/usr/bin/env python3
"""
Minimal working FastAPI app that avoids problematic imports
"""

try:
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Audit Analytics API", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "Audit Analytics Platform API", "status": "running"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "database": "sqlite"}
    
    if __name__ == "__main__":
        print("Starting minimal API server on http://localhost:8000")
        print("Press Ctrl+C to stop")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying alternative approach...")
    
    # Fallback to simple HTTP server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/" or self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "message": "Audit Analytics Platform (Simple Server)",
                    "status": "running",
                    "note": "FastAPI compatibility issue - using simple HTTP server"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    print("Starting simple HTTP server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    server = HTTPServer(("0.0.0.0", 8000), SimpleHandler)
    server.serve_forever()