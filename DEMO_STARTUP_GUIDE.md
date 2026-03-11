# Demo Startup Guide - Audit Analytics Platform

## Quick Start (For Demo)

### 1. Start Backend Server

**IMPORTANT**: Due to Python 3.13 compatibility issues with FastAPI/Pydantic, use the demo server:

```bash
cd backend
python demo_server.py
```

The backend will start on `http://localhost:8000`

**Note**: If you see FastAPI/Pydantic errors with `main.py`, this is expected with Python 3.13. The `demo_server.py` provides all necessary endpoints without those dependencies.

### 2. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Test the Demo Flow

1. **Login**: Use any credentials (authentication is simplified for demo)
2. **Select Role**: Choose "Auditor"
3. **Upload Dataset**: 
   - Go to "Analysis" page
   - Upload any CSV file (e.g., `backend/test_anomaly_dataset.csv`)
   - Click "Commence AI Scan"
4. **Watch Agent Pipeline**: 
   - Click "Authorize & Execute" for each step
   - Watch the progress through 6 agent steps
5. **View Results**: 
   - After final step, you'll see 5 hardcoded flagged cases
   - Each case shows risk score, evidence, and recommendations
6. **Test Chatbot**:
   - Go to "Chatbot" page
   - Ask questions like "What is ERP?" or "What are duplicate invoices?"
   - Responses will come from Gemini API (if configured) or fallback responses

## What's Hardcoded for Demo

### Backend (`backend/routes/analysis.py`)
- All 6 agent steps return mock success messages
- Risk Scoring and Explanation steps create 5 mock flagged cases in database:
  1. **INV-2024-DUP-001** (85/100 HIGH) - Duplicate invoice
  2. **INV-2024-THRESH-001** (65/100 MEDIUM) - Threshold avoidance
  3. **INV-2024-SPIKE-001** (72/100 HIGH) - Vendor payment spike
  4. **INV-2024-WEEKEND-001** (45/100 MEDIUM) - Weekend posting
  5. **INV-2024-ROUND-001** (40/100 MEDIUM) - Round number

### Frontend (`frontend/src/pages/auditor/Analysis.tsx`)
- Always displays 5 hardcoded flagged cases in results
- Each case includes:
  - Transaction ID
  - Risk score and level
  - Flag type
  - Reason summary
  - Detailed explanation
  - Recommendation

### Chatbot (`backend/routes/chatbot.py`)
- Uses Gemini API first (API key: `AIzaSyAf0g6ywxbHRqY2Rr4z0eapQOfF7xOkX1A`)
- Falls back to Grok if Gemini fails
- Has enhanced fallback responses for common questions:
  - ERP systems
  - Duplicate invoices
  - Weekend transactions
  - Offshore payments

## Testing Backend Endpoints

Run the test script:

```bash
cd backend
python test_backend.py
```

This will test:
- Health check endpoint
- Analysis step execution
- Chatbot query
- Flagged cases retrieval

## Troubleshooting

### Frontend shows "No Anomalies Detected"
1. Make sure you rebuilt the frontend: `cd frontend && npm run build`
2. If using dev server, restart it: `npm run dev`
3. Clear browser cache and reload

### Chatbot shows placeholder responses
1. Check `.env` file has `GEMINI_API_KEY` set
2. Verify API key is valid
3. Check backend logs for LLM provider errors

### Backend won't start
1. Check Python version (3.8+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check port 8000 is not in use

### Database errors
- The demo doesn't require a real database for flagged cases display
- SQLite database at `backend/audit_analytics.db` is used but can be empty
- Hardcoded data bypasses database requirements

## API Endpoints

### Analysis
- `POST /api/analysis/run_step` - Execute agent step (returns hardcoded results)

### Chatbot
- `POST /api/chatbot/query` - Query audit assistant

### Cases
- `GET /api/cases` - Get flagged cases (may be empty, frontend uses hardcoded data)

### Health
- `GET /health` - Check API health
- `GET /system-info` - Get system configuration

## Environment Variables

Key variables in `backend/.env`:

```env
GEMINI_API_KEY=AIzaSyAf0g6ywxbHRqY2Rr4z0eapQOfF7xOkX1A
GROK_API_KEY=xai-WYmKWr5JwkOwixzwU79WY7by0nMhzKprgPjjDdUpVTtgKjGQ1x9FG21l2ISAQVmF85HxkqdxAPmOLoO2
LLM_PROVIDER=gemini
```

## Demo Features Working

✅ Dataset upload
✅ 6-step agent pipeline with progress tracking
✅ 5 hardcoded flagged cases with full details
✅ Risk scoring and categorization
✅ Chatbot with Gemini integration
✅ Professional UI with animations
✅ Expandable case details
✅ Evidence and recommendations display

## Known Limitations (Demo Mode)

⚠️ Real agent execution disabled (SQLAlchemy compatibility issue)
⚠️ Database may be empty (hardcoded data used instead)
⚠️ No real anomaly detection (mock results)
⚠️ Authentication simplified
⚠️ No real-time streaming (Kafka disabled)

## Production Readiness

To make this production-ready:
1. Fix SQLAlchemy compatibility with Python 3.13
2. Implement real agent execution
3. Connect to production database
4. Enable real-time streaming
5. Implement proper authentication
6. Add comprehensive error handling
7. Remove hardcoded data
