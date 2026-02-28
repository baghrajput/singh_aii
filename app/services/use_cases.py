from typing import Dict, Any
from app.services.nlp import nlp_service
from app.services.dispatcher import dispatcher_engine

class UseCaseHandler:
    """
    Step 9: All 11 Use Cases logic handler.
    Ensures specific flows for each scenario defined in the SoW.
    """
    async def handle_request(self, user_id: str, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # First, classify intent, urgency, and sentiment using NLP service
        classification = await nlp_service.classify_intent(text)
        issue_type = classification.get("issue_type")
        urgency = classification.get("urgency")
        sentiment = classification.get("sentiment")

        # 1. Emergency Maintenance (High priority, specific keywords)
        if urgency == "Emergency" or any(word in text_lower for word in ["fire", "flood", "gas leak", "explosion", "خطر", "حريق", "فيضان"]):
            return {"type": "Emergency", "action": "dispatch_immediately", "msg": f"This is an emergency. Dispatching immediate assistance for {issue_type}. Please stay safe.", "classification": classification}

        # 3. Check request status
        if any(word in text_lower for word in ["status", "check", "where is my request", "حالة طلبي", "وين طلبي"]):
            return {"type": "StatusQuery", "action": "query_aamer_status", "msg": "Checking the status of your request in our system. Please provide your ticket number if you have one.", "classification": classification}

        # 4. Reschedule appointment
        if any(word in text_lower for word in ["reschedule", "change time", "move appointment", "تغيير موعد", "إعادة جدولة"]):
            return {"type": "Reschedule", "action": "update_appointment", "msg": "I can help you reschedule your appointment. What is your preferred date and time?", "classification": classification}

        # 5. Satisfaction survey
        if any(word in text_lower for word in ["survey", "feedback", "how was", "استبيان", "تقييم"]):
            return {"type": "Survey", "action": "record_feedback", "msg": "Thank you for your feedback. Would you like to take a short survey now?", "classification": classification}

        # 6. Answer service questions (FAQ) / 11. FAQ and knowledge base queries
        if any(word in text_lower for word in ["how do i", "what is", "explain", "كيف", "ما هو", "اشرح"]):
            return {"type": "FAQ", "action": "kb_lookup", "msg": "I can answer your questions. What would you like to know?", "classification": classification}

        # 9. Voice appointment cancellation
        if any(word in text_lower for word in ["cancel", "revoke appointment", "إلغاء موعد", "إلغاء"]):
            return {"type": "Cancellation", "action": "cancel_ticket", "msg": "I can help you cancel your appointment. Please confirm your ticket number.", "classification": classification}

        # 7. Handle duplicate requests (Requires database lookup, mock for now)
        if any(word in text_lower for word in ["again", "same problem", "نفس المشكلة", "مرة أخرى"]):
            # In a real system, this would query the CRM/A'amer for recent tickets by user_id
            return {"type": "DuplicateCheck", "action": "check_duplicate", "msg": "It seems you've reported this issue recently. Are you experiencing the same problem?", "classification": classification}

        # 10. Recurring issue detection (Requires database lookup, mock for now)
        if any(word in text_lower for word in ["always happens", "recurring", "يتكرر", "دائما"]):
            # In a real system, this would query the CRM/A'amer for historical patterns
            return {"type": "RecurringIssue", "action": "check_recurring_issue", "msg": "I see this might be a recurring issue. We will investigate further.", "classification": classification}

        # 8. Multi-service request in one call (Complex, acknowledge and offer to handle sequentially)
        # This is difficult to fully automate without advanced multi-turn dialogue. For now, we acknowledge.
        if len(text.split(" and ")) > 1 and any(t in text_lower for t in ["plumbing", "electrical", "hvac"]):
             return {"type": "MultiService", "action": "multi_service_follow_up", "msg": "I understand you have multiple requests. Let's address them one by one, starting with your primary concern.", "classification": classification}

        # 2. Non-emergency maintenance (Default if no other specific use case is matched)
        # This will be handled by the dispatcher engine if urgency is Non-Emergency
        action_plan = await dispatcher_engine.process_action(classification)
        return {"type": "GeneralRequest", "action": action_plan["action"], "msg": action_plan["response_text"], "classification": classification}

use_case_handler = UseCaseHandler()
