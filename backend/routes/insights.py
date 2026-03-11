from fastapi import APIRouter
import asyncio

router = APIRouter(prefix="/insights", tags=["Insights Dashboard"])

@router.get("/dashboard")
async def get_insights_dashboard(timeRange: str = "30D"):
    # Mocking database connection and aggregation query
    # In a real environment, this would hit the fastAPI database context via dependency.
    await asyncio.sleep(0.5)
    
    return {
        "trendData": [
            {"name": "Week 1", "anomalies": 4, "volume": 1200},
            {"name": "Week 2", "anomalies": 7, "volume": 1400},
            {"name": "Week 3", "anomalies": 3, "volume": 1100},
            {"name": "Week 4", "anomalies": 12, "volume": 2100},
            {"name": "Week 5", "anomalies": 8, "volume": 1600},
            {"name": "Week 6", "anomalies": 5, "volume": 1500},
        ],
        "riskDistribution": [
            {"name": "Duplicate Invoices", "value": 45},
            {"name": "Off-hours Processing", "value": 25},
            {"name": "Unusual Amounts", "value": 15},
            {"name": "New Vendor Spikes", "value": 10},
            {"name": "Offshore Routing", "value": 5},
        ],
        "departmentData": [
            {"name": "IT", "high": 12, "medium": 25, "low": 40},
            {"name": "Marketing", "high": 3, "medium": 15, "low": 30},
            {"name": "Operations", "high": 8, "medium": 20, "low": 60},
            {"name": "Sales", "high": 2, "medium": 10, "low": 50},
        ],
        "kpis": {
            "total_scanned": 14204,
            "active_anomalies": 42,
            "critical_risks": 3,
            "ai_accuracy": 98.2,
            "total_trend": "+12%",
            "anomalies_trend": "-5%",
            "critical_trend": "Stable",
            "accuracy_trend": "+0.4%"
        }
    }
