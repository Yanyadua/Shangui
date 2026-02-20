import httpx
from pathlib import Path
from typing import Optional
from app.config.settings import get_config


class WhisperClient:
    """Whisper API 客户端 (使用 OpenAI Whisper API)"""

    def __init__(self):
        config = get_config()
        self.api_key = config.api_keys.whisper
        self.base_url = "https://api.openai.com/v1"

    async def transcribe(
        self,
        audio_file_path: str,
        language: str = "zh"
    ) -> str:
        """转写音频文件为文本"""

        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as audio_file:
                files = {
                    "file": (audio_path.name, audio_file, "audio/mpeg")
                }
                data = {
                    "model": "whisper-1",
                    "language": language
                }

                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    files=files,
                    data=data
                )
                response.raise_for_status()
                result = response.json()
                return result["text"]