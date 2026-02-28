import whisper
import torch
import os
from typing import Tuple

class ASRService:
    def __init__(self, model_name: str = "large-v3"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Load the specified Whisper model (defaulting to large-v3)
        self.model = whisper.load_model(model_name, device=self.device)
        print(f"Whisper model '{model_name}' loaded on {self.device}")

    async def transcribe(self, audio_path: str) -> Tuple[str, str]:
        """
        Transcribes audio to text and detects language.
        Returns a tuple of (transcribed_text, detected_language).
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        # Perform transcription and language detection
        result = self.model.transcribe(audio_path, task="transcribe")
        
        text = result.get("text", "").strip()
        language = result.get("language", "en") # Default to English if not detected
        
        return text, language

asr_service = ASRService()
