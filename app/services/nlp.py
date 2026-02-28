from typing import Dict, Any
import json
import ollama
from app.core.config import settings


class NLPService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.LLM_MODEL_NAME

    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classifies issue type, urgency, and sentiment using Llama 3/Jais via Ollama.
        Uses keyword logic as a fallback if Ollama fails.
        """

        prompt = f"""
Analyze the following resident request for Saudi Aramco Community Services.
The request is: "{text}"

Perform the following analysis:
1. Identify the primary Issue Type: Appliance, Plumbing, Electrical, HVAC, Pest Control, or Other.
2. Determine the Urgency: Emergency, Urgent, or Non-Emergency.
3. Determine the Sentiment: Positive, Neutral, or Negative.

Return ONLY a JSON object in this format:
{{"issue_type": "...", "urgency": "...", "sentiment": "..."}}
"""

        try:
            # 🔹 Real Ollama API Call
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                format="json"
            )

            # Ollama returns response inside 'response' key as string
            if "response" in response:
                return json.loads(response["response"])
            else:
                raise ValueError("Invalid response from Ollama")

        except Exception as e:
            print(f"Ollama/LLM call failed: {e}. Falling back to keyword logic.")

            # 🔹 Fallback Keyword Logic
            text_lower = text.lower()

            issue = "Other"
            urgency = "Non-Emergency"
            sentiment = "Neutral"

            # Issue Detection
            if any(word in text_lower for word in ["تسريب", "ماء", "سباكة", "plumbing", "leak", "water"]):
                issue = "Plumbing"
            elif any(word in text_lower for word in ["كهرباء", "انقطاع", "electrical", "power", "light"]):
                issue = "Electrical"
            elif any(word in text_lower for word in ["تكييف", "حار", "hvac", "ac", "cooling"]):
                issue = "HVAC"
            elif any(word in text_lower for word in ["ثلاجة", "فرن", "appliance", "fridge", "oven"]):
                issue = "Appliance"
            elif any(word in text_lower for word in ["حشرات", "pest", "bug"]):
                issue = "Pest Control"

            # Urgency Detection
            if any(word in text_lower for word in ["حريق", "طوارئ", "خطر", "emergency", "fire", "danger"]):
                urgency = "Emergency"
            elif any(word in text_lower for word in ["عاجل", "urgent", "asap", "quickly"]):
                urgency = "Urgent"

            # Sentiment Detection
            if any(word in text_lower for word in ["غاضب", "سيئ", "terrible", "angry", "bad"]):
                sentiment = "Negative"
            elif any(word in text_lower for word in ["شكرا", "ممتاز", "thank you", "great", "good"]):
                sentiment = "Positive"

            return {
                "issue_type": issue,
                "urgency": urgency,
                "sentiment": sentiment
            }


# Service Instance
nlp_service = NLPService()
