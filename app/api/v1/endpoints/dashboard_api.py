from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, CallLog, Ticket
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func

router = APIRouter()

class LiveCallResponse(BaseModel):
    id: int
    caller_id: str
    transcript: str
    sentiment: str
    summary: str
    timestamp: datetime
    language: str

@router.get("/dashboard/live-calls", response_model=List[LiveCallResponse])
async def get_live_calls(db: Session = Depends(get_db)):
    calls = db.query(CallLog).order_by(CallLog.timestamp.desc()).limit(50).all()
    return calls

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_calls = db.query(CallLog).count()
    if total_calls == 0:
        return {"sla_percentage": 100.0, "avg_latency_ms": 0.0, "sentiment_breakdown": {"Positive": 0, "Neutral": 0, "Negative": 0}}

    # Mock SLA and Latency for now, as real calculation needs more data points
    sla_percentage = 99.8 # Placeholder
    avg_latency_ms = 645.0 # Placeholder

    sentiment_breakdown = db.query(CallLog.sentiment, func.count(CallLog.sentiment)).group_by(CallLog.sentiment).all()
    sentiment_dict = {s: c for s, c in sentiment_breakdown}

    return {
        "sla_percentage": sla_percentage,
        "avg_latency_ms": avg_latency_ms,
        "sentiment_breakdown": sentiment_dict
    }

@router.get("/dashboard/call-volume")
async def get_call_volume(db: Session = Depends(get_db)):
    today = datetime.now().date()
    call_volume_data = []
    for i in range(7):
        date = today - timedelta(days=6 - i)
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        count = db.query(CallLog).filter(CallLog.timestamp >= start_of_day, CallLog.timestamp < end_of_day).count()
        call_volume_data.append({"date": date.isoformat(), "count": count})
    return call_volume_data
