from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.api.v1.endpoints import mocks
from app.services.asr import asr_service
from app.services.nlp import nlp_service
from app.services.tts import tts_service
from app.services.dispatcher import dispatcher_engine
from app.services.use_cases import use_case_handler
from app.database import get_db, CallLog
from sqlalchemy.orm import Session
import shutil
import os
import uuid

api_router = APIRouter()
api_router.include_router(mocks.router, prefix="/mocks", tags=["mocks"])

@api_router.post("/call/process")
async def process_call_audio(file: UploadFile = File(...), phone_number: str = "+966501234567", db: Session = Depends(get_db)):
    """
    Step 7: PBX Call Handler.
    Receives audio, runs full pipeline, returns response.
    Includes identity verification, CRM logging, sentiment analysis, and call summary.
    """
    # Generate a unique filename for the temporary audio file
    unique_id = uuid.uuid4().hex
    temp_audio_path = f"temp_audio_{unique_id}_{file.filename}"
    
    # Initialize variables for logging
    transcript = ""
    detected_language = "en" # Default language
    classification = {}
    action_taken = ""
    text_response = ""
    sentiment = "Neutral"
    caller_info = {}
    call_summary = ""

    try:
        # 1. Save temporary audio
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Identity Verification (Mock CRM Lookup)
        caller_info = await mocks.crm_lookup(phone_number)
        caller_id = caller_info.get("caller_id", "UNKNOWN")

        # 3. ASR: Speech to Text and Language Detection
        transcript, detected_language = await asr_service.transcribe(temp_audio_path)
        
        # 4. Use Case Handler (which internally calls NLP and Dispatcher)
        use_case_result = await use_case_handler.handle_request(caller_id, transcript)
        
        classification = use_case_result.get("classification", {})
        action_taken = use_case_result.get("action", "unknown")
        text_response = use_case_result.get("msg", "I am sorry, I could not process your request.")
        sentiment = classification.get("sentiment", "Neutral")
        issue_type = classification.get("issue_type", "Other")

        # 5. 911 Transfer Logic
        if action_taken == "dispatch_immediately" and issue_type in ["Fire", "Gas"]:
            # Simulate 911 transfer
            await mocks.transfer_to_911(caller_id=caller_id, issue_type=issue_type, description=transcript)
            text_response = "Emergency detected. Transferring you to 911 immediately. Please hold."
            action_taken = "transferred_to_911"

        # 6. TTS: Text to Speech response in detected language
        audio_response_path = await tts_service.generate_speech(text_response, lang=detected_language) 

        # # 7. Generate Call Summary (simple for now, could be LLM-generated)
        # call_summary = f"Call from {caller_info.get(\'name\')} ({phone_number}). Issue: {issue_type}, Urgency: {classification.get(\'urgency\')}. Action: {action_taken}. Sentiment: {sentiment}."

        call_summary = "Call from " + str(caller_info.get("name")) + " (" + phone_number + "). Issue: " + str(issue_type) + ", Urgency: " + str(classification.get("urgency")) + ". Action: " + action_taken + ". Sentiment: " + sentiment + "."

        # 8. CRM Logging and CallLog storage
        await mocks.crm_log_call(mocks.CRMLogCallRequest(
            caller_id=caller_id,
            transcript=transcript,
            sentiment=sentiment,
            summary=call_summary,
            language=detected_language
        ), db)
        
        return {
            "caller_id": caller_id,
            "transcript": transcript,
            "detected_language": detected_language,
            "classification": classification,
            "action_taken": action_taken,
            "voice_response_url": audio_response_path,
            "text_response": text_response,
            "sentiment": sentiment,
            "call_summary": call_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call processing failed: {e}")
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
