"""
LLM调用封装层

统一接口，支持任意兼容OpenAI Chat API格式的大模型服务。
用户传入API Key、端点地址、模型名称即可使用。
纯urllib实现，零外部SDK依赖。
"""

import json
import urllib.request
import urllib.error
from typing import Optional

from app.config import LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TIMEOUT


class LLMService:
    """
    通用大模型调用封装

    兼容任何实现了 /v1/chat/completions 接口的API服务。
    包括但不限于：OpenAI、DeepSeek、SiliconFlow、本地代理等。
    """

    def __init__(
        self,
        base_url: str = "https://api.deepseek.com/v1",
        api_key: str = "",
        model: str = "deepseek-chat",
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
        timeout: int = LLM_TIMEOUT,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def _build_chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """
        发送聊天请求

        Args:
            messages: OpenAI格式的消息列表
            temperature: 温控参数
            max_tokens: 最大Token数

        Returns:
            OpenAI格式响应字典

        Raises:
            ConnectionError: API服务器连接失败
            ValueError: API Key无效或余额不足
            RuntimeError: 模型返回错误
        """
        url = self._build_chat_url()
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 401:
                raise ValueError(f"API Key 无效，请检查后重试（{e.code}）")
            if e.code == 402:
                raise ValueError("API 余额不足，请充值后重试")
            if e.code == 429:
                raise RuntimeError("请求过于频繁，请稍后重试")
            raise RuntimeError(f"API返回错误 ({e.code}): {body[:200]}")
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"无法连接到 {self.base_url}，请检查API地址是否正确。"
                f"详细错误: {e.reason}"
            )
        except TimeoutError:
            raise TimeoutError(f"请求超时（{self.timeout}秒），请检查网络或模型负载")

    def chat_simple(self, system_prompt: str, user_prompt: str) -> str:
        """简化接口：传入system+user提示词，返回模型回复文本"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        result = self.chat(messages)
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"模型响应格式异常: {str(result)[:200]}") from e

    @classmethod
    def from_config(cls, config: dict) -> "LLMService":
        """从API配置字典创建实例"""
        return cls(
            base_url=config.get("base_url", "https://api.deepseek.com/v1"),
            api_key=config.get("api_key", ""),
            model=config.get("model", "deepseek-chat"),
        )
