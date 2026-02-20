from pathlib import Path
from typing import Optional
import asyncio
from threading import Thread
from queue import Queue


class WhisperClient:
    """本地 Whisper 客户端 (使用 faster-whisper)"""

    def __init__(self, model_size: str = "base", device: str = "cpu"):
        """
        初始化 Whisper 模型

        Args:
            model_size: 模型大小,可选: tiny, base, small, medium, large
            device: 运行设备,可选: cpu, cuda
        """
        self.model_size = model_size
        self.device = device
        self._model = None

    def _load_model(self):
        """延迟加载模型"""
        if self._model is None:
            from faster_whisper import WhisperModel
            print(f"Loading Whisper model ({self.model_size}) on {self.device}...")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8" if self.device == "cpu" else "float16"
            )
            print("Whisper model loaded successfully!")

    def _transcribe_sync(self, audio_path: str, language: str) -> str:
        """同步转写 (在线程中运行)"""
        self._load_model()

        segments, _ = self._model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True  # 启用语音活动检测
        )

        # 拼接所有文本片段
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)

        return "".join(text_parts).strip()

    async def transcribe(
        self,
        audio_file_path: str,
        language: str = "zh"
    ) -> str:
        """
        异步转写音频文件为文本

        Args:
            audio_file_path: 音频文件路径
            language: 语言代码 (zh=中文, en=英文)

        Returns:
            转写后的文本
        """
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # 在线程池中运行同步的转写函数
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._transcribe_sync,
            str(audio_path),
            language
        )

        return result