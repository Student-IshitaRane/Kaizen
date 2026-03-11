#!/usr/bin/env python3
"""
Minimal test server to verify FastAPI works
"""

from fastapi import FastAPI
import uvicorn

# Create a simple FastAPI app
app = FastAPI(title="Test Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Test server is working"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting test server on http://localhost:8001")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")