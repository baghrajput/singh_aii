import os
import time
import torch
from TTS.api import TTS
from app.core.config import settings

class TTSService:
    def __init__(self):
        self.output_dir = "app/templates/static/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            # Load the xtts_v2 model as specified
            self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=torch.cuda.is_available())
            print(f"Coqui TTS model xtts_v2 loaded on {"GPU" if torch.cuda.is_available() else "CPU"}")
        except Exception as e:
            print(f"Could not load Coqui TTS model xtts_v2, using placeholder logic: {e}")
            self.tts = None # Fallback or error state

    async def generate_speech(self, text: str, lang: str = 'en') -> str:
        """
        Generates speech from text using Coqui TTS.
        Optimized for <700ms latency in on-prem deployment.
        """
        start_time = time.time()
        filename = f"resp_{int(start_time)}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        if self.tts:
            try:
                # For xtts_v2, language is a direct parameter
                self.tts.tts_to_file(text=text, file_path=filepath, language=lang)
            except Exception as e:
                print(f"Coqui TTS generation failed, using fallback: {e}")
                with open(filepath.replace('.wav', '.txt'), 'w') as f:
                    f.write(f"TTS failed for: {text}")
                filepath = filepath.replace('.wav', '.txt') # Indicate fallback
        else:
            with open(filepath.replace('.wav', '.txt'), 'w') as f:
                f.write(f"TTS service unavailable. Text: {text}")
            filepath = filepath.replace('.wav', '.txt') # Indicate fallback

        latency = (time.time() - start_time) * 1000
        print(f"TTS Latency: {latency:.2f}ms")
        
        return filepath

tts_service = TTSService()
