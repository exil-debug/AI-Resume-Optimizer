"""
简历优化 + 面试分析服务

动态接收API配置，调用大模型完成简历优化、面试预测、技能差距分析。
新增分段优化支持，长简历按模块分段处理后合并输出。
补充边界保护：空文本、单段超长等极端情况的降级逻辑。
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
    CHUNK_OPTIMIZATION_SYSTEM_PROMPT,
    build_chunk_optimization_user_prompt,
)
from app.services.llm_service import LLMService
from app.config import CHUNK_MAX_LENGTH, CHUNK_MAX_TOKENS


class OptimizationService:
    """简历优化服务"""

    def optimize(
        self,
        resume_text: str,
        jd_text: str,
        api_config: Optional[APIConfig] = None,
    ) -> OptimizationResult:
        # 空文本直接返回
        if not resume_text or not resume_text.strip():
            return OptimizationResult(
                optimized_text="",
                changes_summary=[],
                word_polish=[],
                skill_additions=[],
                weakness_fixes=[],
            )

        llm = self._build_llm(api_config)

        # 长简历自动分段处理，避免超出上下文限制
        if len(resume_text) > CHUNK_MAX_LENGTH:
            return self._optimize_in_chunks(resume_text, jd_text, llm)

        prompt = build_optimization_user_prompt(resume_text, jd_text)
        try:
            raw = llm.chat_simple(OPTIMIZATION_SYSTEM_PROMPT, prompt)
            data = self._parse_json(raw)
        except Exception:
            # 降级重试：降低temperature提升稳定性
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
    def _optimize_in_chunks(
        resume_text: str, jd_text: str, llm: LLMService
    ) -> OptimizationResult:
        """
        分段优化长简历。

        按段落边界将简历切块，每个chunk单独优化后合并。
        避免长文本超出上下文限制导致内容丢失。
        单段优化失败时保留原文段，不阻塞整个流程。
        """
        chunks = OptimizationService._split_into_chunks(resume_text, CHUNK_MAX_LENGTH)
        if not chunks:
            return OptimizationResult(optimized_text=resume_text, changes_summary=[])

        optimized_parts = []
        all_changes = []
        all_polish = []
        all_skills = []
        all_fixes = []

        for i, chunk in enumerate(chunks):
            section_name = f"段落{i + 1}"
            first_line = chunk.strip().split("\n")[0][:30]
            if first_line:
                section_name = first_line

            # 单段过长时的二次切分保护
            if len(chunk) > CHUNK_MAX_LENGTH * 2:
                sub_chunks = OptimizationService._split_into_chunks(chunk, CHUNK_MAX_LENGTH)
                for j, sub_chunk in enumerate(sub_chunks):
                    result = OptimizationService._process_single_chunk(sub_chunk, jd_text, llm, i, f"{section_name}({j+1}/{len(sub_chunks)})")
                    optimized_parts.append(result[0])
                    all_changes.extend(result[1])
                    all_polish.extend(result[2])
                    all_skills.extend(result[3])
                    all_fixes.extend(result[4])
            else:
                result = OptimizationService._process_single_chunk(chunk, jd_text, llm, i, section_name)
                optimized_parts.append(result[0])
                all_changes.extend(result[1])
                all_polish.extend(result[2])
                all_skills.extend(result[3])
                all_fixes.extend(result[4])

        return OptimizationResult(
            optimized_text="\n\n".join(optimized_parts),
            changes_summary=all_changes,
            word_polish=all_polish,
            skill_additions=all_skills,
            weakness_fixes=all_fixes,
        )

    @staticmethod
    def _process_single_chunk(chunk, jd_text, llm, chunk_index, section_name):
        """处理单个段的优化，失败时返回原文本。"""
        prompt = build_chunk_optimization_user_prompt(chunk, jd_text, chunk_index, section_name)
        try:
            raw = llm.chat_simple(CHUNK_OPTIMIZATION_SYSTEM_PROMPT, prompt)
            data = OptimizationService._parse_json(raw)
            return (
                data.get("optimized_text", chunk),
                data.get("changes_summary", []),
                data.get("word_polish", []),
                data.get("skill_additions", []),
                data.get("weakness_fixes", []),
            )
        except Exception:
            return (chunk, [f"第{chunk_index + 1}段优化失败，已保留原文"], [], [], [])

    @staticmethod
    def _split_into_chunks(text: str, max_length: int) -> list[str]:
        """
        按段落边界切分文本。
        优先在段落边界处切分，避免切在句子中间。
        """
        if not text:
            return []
        paragraphs = text.split("\n\n")
        chunks = []
        current = []

        for para in paragraphs:
            para_len = len(para)
            current_len = sum(len(p) for p in current) + max(0, len(current) - 1) * 2  # 加上\n\n
            if current_len + para_len + 2 > max_length and current:
                chunks.append("\n\n".join(current))
                current = [para]
            else:
                current.append(para)

        if current:
            chunks.append("\n\n".join(current))

        return chunks if chunks else [text]

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
        if not resume_text or not resume_text.strip():
            return {"risk_points": [], "interview_questions": [], "skill_gaps": []}

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