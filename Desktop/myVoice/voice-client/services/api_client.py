import requests
from pathlib import Path
from typing import Dict, Any


class APIClient:
    """服务器 API 客户端"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def process_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """上传音频文件并获取处理结果"""

        file_path = Path(audio_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        with open(file_path, "rb") as audio_file:
            files = {"audio_file": (file_path.name, audio_file, "audio/mpeg")}
            response = requests.post(
                f"{self.api_base}/process",
                files=files,
                timeout=300  # 5分钟超时
            )
            response.raise_for_status()
            return response.json()

    def get_records(self, date_filter: str = None) -> list:
        """获取历史记录"""
        params = {"date": date_filter} if date_filter else {}
        response = requests.get(
            f"{self.api_base}/records",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = requests.get(f"{self.api_base}/health", timeout=5)
        response.raise_for_status()
        return response.json()