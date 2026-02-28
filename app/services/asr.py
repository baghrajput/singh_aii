class ASRService:
    def __init__(self):
        print("ASR Service ready - Mock mode")

    async def transcribe(self, audio_path: str):
        # Mock transcription for demo
        return "my pipe is leaking", "en"

asr_service = ASRService()
