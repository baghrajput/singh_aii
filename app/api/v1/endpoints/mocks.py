from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import uuid
import datetime
from sqlalchemy.orm import Session
from app.database import get_db, Ticket, CallLog # Import Ticket and CallLog models

router = APIRouter()

# --- A'amer Mocks (now using PostgreSQL) ---
class TicketRequest(BaseModel):
    caller_id: str
    issue_type: str
    urgency: str
    description: str

class TicketUpdate(BaseModel):
    ticket_id: str
    status: Optional[str] = None
    new_schedule: Optional[datetime.datetime] = None

class TicketStatusResponse(BaseModel):
    ticket_id: str
    caller_id: str
    issue_type: str
    urgency: str
    description: str
    status: str
    created_at: datetime.datetime
    scheduled_time: Optional[datetime.datetime] = None

class TicketHistoryResponse(BaseModel):
    caller_id: str
    tickets: List[TicketStatusResponse]

class DuplicateCheckRequest(BaseModel):
    caller_id: str
    description: str

@router.post("/aamer/create-ticket")
async def aamer_create_ticket(request: TicketRequest, db: Session = Depends(get_db)):
    new_ticket = Ticket(
        ticket_id=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        caller_id=request.caller_id,
        issue_type=request.issue_type,
        urgency=request.urgency,
        description=request.description,
        status="Open",
        created_at=datetime.datetime.now()
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return {
        "status": "success",
        "ticket_id": new_ticket.ticket_id,
        "message": f"Ticket {new_ticket.ticket_id} created in A'amer system"
    }

@router.get("/aamer/ticket-status/{ticket_id}", response_model=TicketStatusResponse)
async def aamer_get_ticket_status(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketStatusResponse(**ticket.__dict__)

@router.post("/aamer/reschedule-ticket")
async def aamer_reschedule_ticket(update: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == update.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.scheduled_time = update.new_schedule
    ticket.status = "Rescheduled"
    db.commit()
    db.refresh(ticket)
    return {"status": "success", "message": f"Ticket {update.ticket_id} rescheduled to {update.new_schedule}"}

@router.post("/aamer/cancel-ticket")
async def aamer_cancel_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = "Cancelled"
    db.commit()
    db.refresh(ticket)
    return {"status": "success", "message": f"Ticket {ticket_id} cancelled"}

@router.get("/aamer/ticket-history/{caller_id}", response_model=TicketHistoryResponse)
async def aamer_get_ticket_history(caller_id: str, db: Session = Depends(get_db)):
    user_tickets = db.query(Ticket).filter(Ticket.caller_id == caller_id).all()
    return {"caller_id": caller_id, "tickets": [TicketStatusResponse(**t.__dict__) for t in user_tickets]}

@router.post("/aamer/duplicate-check")
async def aamer_duplicate_check(request: DuplicateCheckRequest, db: Session = Depends(get_db)):
    # Checks if a similar description exists for the same caller and is not closed
    duplicate_ticket = db.query(Ticket).filter(
        Ticket.caller_id == request.caller_id,
        Ticket.description.ilike(f"%{request.description}%"),
        Ticket.status != "Closed"
    ).first()
    
    if duplicate_ticket:
        return {"is_duplicate": True, "existing_ticket_id": duplicate_ticket.ticket_id, "status": duplicate_ticket.status}
    return {"is_duplicate": False}

# --- CRM Mocks ---
class CRMLogCallRequest(BaseModel):
    caller_id: str
    transcript: str
    sentiment: str
    summary: str
    language: str

@router.get("/crm/lookup/{phone_number}")
async def crm_lookup(phone_number: str):
    # Mocking CRM caller lookup
    if phone_number == "+966501234567": # Example known caller
        return {
            "caller_id": "USR-9921",
            "name": "Ahmed Al-Saud",
            "address": "Dhahran Camp, House 402",
            "phone_number": phone_number,
            "recent_tickets": []
        }
    return {
        "caller_id": f"GUEST-{uuid.uuid4().hex[:4].upper()}",
        "name": "Guest User",
        "address": "N/A",
        "phone_number": phone_number,
        "recent_tickets": []
    }

@router.post("/crm/log-call")
async def crm_log_call(request: CRMLogCallRequest, db: Session = Depends(get_db)):
    new_call_log = CallLog(
        caller_id=request.caller_id,
        transcript=request.transcript,
        sentiment=request.sentiment,
        summary=request.summary,
        language=request.language
    )
    db.add(new_call_log)
    db.commit()
    db.refresh(new_call_log)
    print(f"CRM: Logged call {new_call_log.id} for {request.caller_id} - Sentiment: {request.sentiment}")
    return {"status": "success", "message": "Call logged in CRM"}

@router.post("/crm/update-record")
async def crm_update_record(caller_id: str, data: dict):
    print(f"CRM: Updating record for {caller_id} with {data}")
    return {"status": "success", "message": "CRM record updated"}

# --- MyCommunity Mocks ---
@router.post("/mycommunity/notify")
async def mycommunity_notify(user_id: str, message: str):
    print(f"MyCommunity: Sending notification to {user_id}: {message}")
    return {"status": "sent", "platform": "MyCommunity App"}

@router.post("/mycommunity/update-status")
async def mycommunity_update_status(user_id: str, status_update: str):
    print(f"MyCommunity: Updating status for {user_id}: {status_update}")
    return {"status": "updated", "platform": "MyCommunity App"}

# --- Sisco Mocks ---
@router.post("/sisco/update")
async def sisco_update(data: dict):
    print(f"Sisco: Operational update received: {data}")
    return {"status": "synchronized", "system": "Sisco"}

# --- SMS Mock ---
class SMSRequest(BaseModel):
    to_number: str
    message: str

@router.post("/sms/send")
async def send_sms(request: SMSRequest):
    print(f"SMS: Sending to {request.to_number}: {request.message}")
    return {"status": "sent", "message": "SMS sent successfully"}
