import os
import time

class TTSService:
    def __init__(self):
        self.output_dir = "app/templates/static/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        # We DO NOT load any model here for mock
        self.tts = None

    async def generate_speech(self, text: str, lang: str = "en") -> str:
        """
        Mock TTS: just saves text to a file instead of generating audio.
        Works on Railway free plan.
        """
        start_time = time.time()
        filename = f"resp_{int(start_time)}.txt"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"[MOCK TTS] {text}")

        latency = (time.time() - start_time) * 1000
        print(f"Mock TTS Latency: {latency:.2f}ms")

        return filepath


# Service instance
tts_service = TTSService()
