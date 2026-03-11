# Demo Quick Reference Card

## 🚀 Start Commands

```bash
# Terminal 1 - Backend (Use demo server for Python 3.13)
cd backend
python demo_server.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🌐 URLs

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 Demo Script (5 minutes)

### 1. Login & Role Selection (30 seconds)
- Enter any credentials
- Click "Auditor" role

### 2. Dataset Upload (30 seconds)
- Go to "Analysis" page
- Upload `backend/test_anomaly_dataset.csv`
- Click "Commence AI Scan"

### 3. Agent Pipeline (2 minutes)
- Click "Authorize & Execute" for each step
- Show progress messages
- Highlight 6 specialized agents:
  1. Data Ingestion
  2. Anomaly Detection (8 anomalies found)
  3. Pattern Recognition (5 patterns)
  4. Compliance Rules (3 violations)
  5. Risk Scoring (5 high-risk cases)
  6. LLM Explanations

### 4. View Results (1.5 minutes)
- Show 5 flagged cases
- Expand INV-2024-DUP-001 (85/100 HIGH)
- Point out:
  * Risk score with visual bar
  * Detected flags
  * Automated reasoning
  * Supporting evidence
  * Action buttons

### 5. Chatbot Demo (1 minute)
- Go to "Chatbot" page
- Ask: "What is ERP?"
- Show detailed AI response
- Ask: "What are duplicate invoices?"

## 📊 Key Numbers to Mention

- **6 AI Agents** working in orchestration
- **5 Flagged Cases** identified
- **85/100** highest risk score (duplicate invoice)
- **15 Transactions** analyzed
- **98.2%** AI accuracy (from insights dashboard)

## 🎨 UI Features to Highlight

- Modern glass-morphism design
- Real-time progress tracking
- Color-coded risk levels (red/amber/green)
- Expandable case details
- Smooth animations
- Professional audit terminology

## 💬 Sample Chatbot Questions

1. "What is ERP?"
2. "What are duplicate invoices?"
3. "Why are weekend transactions risky?"
4. "What is threshold avoidance?"

## 🔍 Case Details to Show

**INV-2024-DUP-001** (Best example):
- Risk: 85/100 HIGH
- Type: Duplicate Invoice
- Amount: $15,000
- Evidence: "Invoice appears twice with same vendor and amount"
- Recommendation: "Verify supporting documentation and contact vendor"

## ⚡ Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No flagged cases | Rebuild frontend: `npm run build` |
| Chatbot placeholder | Check `.env` has Gemini API key |
| Backend won't start | Check port 8000 is free |
| Frontend won't start | Run `npm install` first |

## 🎤 Key Talking Points

1. **AI-Powered**: "6 specialized AI agents work together to analyze transactions"
2. **Risk-Based**: "Automatically scores and prioritizes high-risk cases"
3. **Explainable**: "LLM generates human-readable explanations for every finding"
4. **Interactive**: "Auditors can drill down into evidence and take action"
5. **Intelligent Assistant**: "AI chatbot provides audit expertise on demand"

## 📝 Demo Notes

- This is a **prototype** with hardcoded data for demonstration
- Real version would connect to live database and ML models
- Emphasize the **workflow** and **user experience**
- Focus on how AI **augments** auditor capabilities
- Highlight **time savings** and **risk detection**

## ✨ Wow Moments

1. Watching all 6 agents execute in sequence
2. Seeing the 85/100 high-risk duplicate invoice
3. Expanding a case to see detailed evidence
4. Getting instant AI responses in chatbot
5. Visual risk scoring with color-coded badges

## 🎬 Closing Statement

"This AI-powered audit platform demonstrates how machine learning and LLMs can transform traditional audit processes, automatically detecting anomalies, scoring risks, and providing actionable insights - all while maintaining full transparency and explainability for auditors."

---

**Print this card and keep it handy during the demo!**
