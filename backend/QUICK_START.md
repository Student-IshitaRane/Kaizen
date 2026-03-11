# Quick Start Guide

## Problem: Python 3.13 Compatibility Issue

The error you're seeing is because Python 3.13 changed the `ForwardRef._evaluate()` signature, breaking Pydantic v1 compatibility.

## Solution 1: Use Python 3.11 (Recommended)

1. Install Python 3.11 from python.org
2. Create virtual environment:
```bash
py -3.11 -m venv venv
venv\Scripts\activate
pip install fastapi==0.95.0 uvicorn==0.21.0 sqlalchemy==2.0.20 pydantic==1.10.7 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-multipart==0.0.6 python-dotenv==1.0.0
```

3. Run server:
```bash
python run.py
```

## Solution 2: Use Docker (Easiest)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    command: >
      sh -c "pip install -r simple_requirements.txt && python run.py"
```

Run: `docker-compose up`

## Solution 3: Quick Test Without FastAPI

Run the minimal server:
```bash
python minimal_app.py
```

This uses a simple HTTP server as fallback.

## Verify Setup

Once running, visit:
- http://localhost:8000/docs (API documentation)
- http://localhost:8000/health (Health check)

## Next Steps

1. Register a user: POST /auth/register
2. Login: POST /auth/login
3. Upload dataset: POST /upload/dataset
4. Create transaction: POST /transactions
5. View flagged cases: GET /cases