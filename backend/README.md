# Audit Analytics Platform - Backend

## Overview
FastAPI backend for the AI-powered audit analytics platform.

## Features
- JWT-based authentication with role support (Auditor/Finance)
- Dataset upload and processing
- Transaction management
- Flagged transaction/case management
- PostgreSQL database
- Modular architecture

## Setup

### 1. Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# DATABASE_URL, SECRET_KEY, etc.
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb audit_analytics

# Initialize database tables
python scripts/init_db.py
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main script
python -m app.main
```

## API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Upload (Auditor only)
- `POST /api/v1/upload/dataset` - Upload historical dataset
- `GET /api/v1/upload/{upload_id}/status` - Check upload status
- `GET /api/v1/upload/history` - Get upload history

### Transactions (Finance only)
- `POST /api/v1/transactions` - Create new transaction
- `GET /api/v1/transactions` - List transactions with filters
- `GET /api/v1/transactions/{transaction_id}` - Get transaction details

### Cases (Auditor only)
- `GET /api/v1/cases` - List flagged transactions/cases
- `GET /api/v1/cases/{case_id}` - Get case details
- `PUT /api/v1/cases/{case_id}/review` - Review case
- `POST /api/v1/cases/{case_id}/assign` - Assign case to auditor

## Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Docker
```bash
# Build image
docker build -t audit-analytics-backend .

# Run container
docker run -p 8000:8000 --env-file .env audit-analytics-backend
```

## Development
- Use `black` for code formatting
- Use `ruff` for linting
- Write tests in `tests/` directory
- Follow FastAPI best practices