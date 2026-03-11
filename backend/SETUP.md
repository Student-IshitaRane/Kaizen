# Setup Guide for Audit Analytics Platform Backend

## Step 1: Install Dependencies

Run the following command to install all required dependencies:

```bash
pip install -r minimal_requirements.txt
```

If you want the full set of dependencies (including AI/ML libraries), use:
```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/audit_analytics
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: LLM API keys (for future AI features)
GEMINI_API_KEY=your-gemini-api-key
GROK_API_KEY=your-grok-api-key
LLM_PROVIDER=gemini

UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600
ENVIRONMENT=development
```

## Step 3: Initialize Database

Run the database initialization script:
```bash
python scripts/init_database.py
```

## Step 4: Run the Backend

Start the FastAPI server:
```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Step 5: Test the API

Once running, access:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Quick Test Commands

### 1. Register a user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Auditor",
    "email": "auditor@test.com",
    "password": "test123",
    "role": "auditor"
  }'
```

### 2. Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "auditor@test.com",
    "password": "test123"
  }'
```

### 3. Test upload endpoint (requires authentication):
```bash
# First get token from login response, then:
curl -X POST "http://localhost:8000/upload/dataset" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample_data.csv" \
  -F "dataset_type=vendor_master"
```

## Troubleshooting

### 1. ModuleNotFoundError: No module named 'sqlalchemy'
- Make sure you installed dependencies: `pip install -r minimal_requirements.txt`

### 2. Database connection errors
- Check your PostgreSQL is running
- Verify DATABASE_URL in .env file
- Ensure database 'audit_analytics' exists

### 3. Import errors
- Make sure all __init__.py files exist in directories
- Check Python path is set correctly

### 4. Port already in use
- Change port in run.py or use: `uvicorn main:app --reload --host 0.0.0.0 --port 8001`

## Project Structure

```
backend/
├── main.py                    # FastAPI application
├── database.py               # Database configuration
├── core/                     # Configuration and constants
├── models/                   # SQLAlchemy models
├── schemas/                  # Pydantic schemas
├── auth/                     # Authentication
├── routes/                   # API endpoints
├── services/                 # Business logic
└── scripts/                  # Utility scripts
```

## Next Steps

1. Test all API endpoints using Swagger UI
2. Create sample data for testing
3. Implement frontend integration
4. Add Kafka integration for real-time processing
5. Implement AI agent pipeline