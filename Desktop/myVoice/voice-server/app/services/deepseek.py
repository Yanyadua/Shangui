import httpx
import json
import asyncio
from typing import Dict, Optional
from app.config.settings import get_config


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self):
        config = get_config()
        self.api_key = config.api_keys.deepseek
        self.base_url = "https://api.deepseek.com"
        self.model = "deepseek-chat"

    async def chat(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2
    ) -> str:
        """发送聊天请求并返回响应文本"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def chat_with_json(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """发送聊天请求并解析 JSON 响应"""

        response_text = await self.chat(user_prompt, system_prompt)

        # 提取 JSON 代码块
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)