"""
JD匹配服务

调用大模型对简历与JD进行匹配度分析。
动态接收API配置（key/base_url/model），不依赖固定配置。
"""

import json
import re
from typing import Optional

from app.models.analysis import MatchingResult, MatchingScore, APIConfig
from app.prompts.templates import MATCHING_SYSTEM_PROMPT, build_matching_user_prompt
from app.services.llm_service import LLMService


class MatchingService:
    """JD匹配评分服务"""

    def analyze(
        self,
        resume_text: str,
        jd_text: str,
        api_config: Optional[APIConfig] = None,
    ) -> MatchingResult:
        """
        分析简历与JD匹配度

        Args:
            resume_text: 简历文本
            jd_text: 岗位JD文本
            api_config: API配置（key/base_url/model），None则尝试默认配置

        Returns:
            MatchingResult
        """
        llm = self._build_llm(api_config)
        user_prompt = build_matching_user_prompt(resume_text, jd_text)

        try:
            raw = llm.chat_simple(MATCHING_SYSTEM_PROMPT, user_prompt)
            data = self._parse_json(raw)
        except Exception:
            # 降级重试
            fallback = LLMService(
                base_url=llm.base_url, api_key=llm.api_key, model=llm.model, temperature=0.3
            )
            raw = fallback.chat_simple(MATCHING_SYSTEM_PROMPT, user_prompt)
            data = self._parse_json(raw)

        dims = [MatchingScore(**d) for d in data.get("dimension_scores", [])]
        return MatchingResult(
            overall_score=data.get("overall_score", 0),
            dimension_scores=dims,
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            suggestions=data.get("suggestions", []),
            summary=data.get("summary", ""),
        )

    @staticmethod
    def _build_llm(api_config: Optional[APIConfig]) -> LLMService:
        if api_config and api_config.api_key:
            return LLMService(
                base_url=api_config.base_url,
                api_key=api_config.api_key,
                model=api_config.model,
            )
        return LLMService()

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if m:
            text = m.group(1).strip()
        s = text.find("{")
        e = text.rfind("}")
        if s != -1 and e != -1:
            text = text[s : e + 1]
        return json.loads(text)


matching_service = MatchingService()
