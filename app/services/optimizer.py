"""
简历优化 + 面试分析服务

动态接收API配置，调用大模型完成简历优化、面试预测、技能差距分析。
"""

import json
import re
from typing import Optional

from app.models.analysis import OptimizationResult, APIConfig
from app.prompts.templates import (
    OPTIMIZATION_SYSTEM_PROMPT,
    build_optimization_user_prompt,
    INTERVIEW_ANALYSIS_SYSTEM_PROMPT,
    build_interview_user_prompt,
)
from app.services.llm_service import LLMService


class OptimizationService:
    """简历优化服务"""

    def optimize(
        self,
        resume_text: str,
        jd_text: str,
        api_config: Optional[APIConfig] = None,
    ) -> OptimizationResult:
        llm = self._build_llm(api_config)
        prompt = build_optimization_user_prompt(resume_text, jd_text)
        try:
            raw = llm.chat_simple(OPTIMIZATION_SYSTEM_PROMPT, prompt)
            data = self._parse_json(raw)
        except Exception:
            fb = LLMService(base_url=llm.base_url, api_key=llm.api_key, model=llm.model, temperature=0.3)
            raw = fb.chat_simple(OPTIMIZATION_SYSTEM_PROMPT, prompt)
            data = self._parse_json(raw)

        return OptimizationResult(
            optimized_text=data.get("optimized_text", ""),
            changes_summary=data.get("changes_summary", []),
            word_polish=data.get("word_polish", []),
            skill_additions=data.get("skill_additions", []),
            weakness_fixes=data.get("weakness_fixes", []),
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


optimization_service = OptimizationService()


class InterviewAnalysisService:
    """面试分析（避雷点+面试问题+技能差距）"""

    def analyze(
        self,
        resume_text: str,
        jd_text: str,
        api_config: Optional[APIConfig] = None,
    ) -> dict:
        llm = self._build_llm(api_config)
        prompt = build_interview_user_prompt(resume_text, jd_text)
        try:
            raw = llm.chat_simple(INTERVIEW_ANALYSIS_SYSTEM_PROMPT, prompt)
            data = self._parse_json(raw)
        except Exception:
            fb = LLMService(base_url=llm.base_url, api_key=llm.api_key, model=llm.model, temperature=0.3)
            raw = fb.chat_simple(INTERVIEW_ANALYSIS_SYSTEM_PROMPT, prompt)
            data = self._parse_json(raw)

        return {
            "risk_points": data.get("risk_points", []),
            "interview_questions": data.get("interview_questions", []),
            "skill_gaps": data.get("skill_gaps", []),
        }

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


interview_analysis_service = InterviewAnalysisService()
