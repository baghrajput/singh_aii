from typing import Dict, Any
import requests
from app.core.config import settings

class DispatcherEngine:
    async def process_action(self, caller_id: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decides exact action based on intent and urgency.
        Includes 911 transfer, SMS triggers, and bilingual responses.
        """
        urgency = classification.get("urgency")
        issue_type = classification.get("issue_type")
        
        # 1. Emergency Case: 911 Transfer for Fire or Gas
        if urgency == "Emergency" and issue_type in ["Fire", "Gas"]:
            # Trigger emergency 911 transfer via mock endpoint
            try:
                requests.post(f"{settings.CRM_API_URL.replace('/crm', '/emergency')}/transfer-911", 
                              json={"caller_id": caller_id, "issue_type": issue_type, "description": "Emergency detected via voice"})
            except:
                pass
                
            return {
                "action": "dispatch_immediately",
                "response_text_en": "Emergency detected. Transferring you to 911 immediately. Please hold.",
                "response_text_ar": "تم اكتشاف حالة طوارئ. جاري تحويلك إلى 911 فوراً. يرجى الانتظار."
            }

        # 2. Urgent Case: Human Escalation
        elif urgency == "Urgent":
            return {
                "action": "escalate_to_human",
                "response_text_en": "Your request is urgent. Connecting you to a supervisor.",
                "response_text_ar": "طلبك عاجل. جاري توصيلك بالمشرف."
            }

        # 3. Non-Emergency: Schedule Appointment
        else:
            # Trigger SMS confirmation (mock)
            try:
                requests.post(f"{settings.CRM_API_URL.replace('/crm', '/sms')}/send", 
                              json={"to_number": caller_id, "message": "Your appointment has been scheduled."})
            except:
                pass
                
            return {
                "action": "schedule_appointment",
                "response_text_en": "I have scheduled an appointment for you. You will receive an SMS confirmation.",
                "response_text_ar": "لقد قمت بجدولة موعد لك. ستصلك رسالة تأكيد عبر الجوال."
            }

dispatcher_engine = DispatcherEngine()
