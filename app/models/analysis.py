"""
分析结果数据模型

定义API配置、JD匹配分析、简历优化、面试问题等所有数据结构。
"""

from typing import Optional
from pydantic import BaseModel, Field


# ==================== API 配置 ====================

class APIConfig(BaseModel):
    """用户自定义的API配置（从前端传入后端）"""
    provider: str = Field(default="deepseek", description="API提供商")
    api_key: str = Field(default="", description="API密钥")
    base_url: str = Field(default="https://api.deepseek.com/v1", description="API地址")
    model: str = Field(default="deepseek-chat", description="模型名称")


# ==================== JD 匹配评分 ====================

class MatchingScore(BaseModel):
    dimension: str = Field(..., description="评分维度")
    score: int = Field(..., ge=0, le=100, description="分数")
    detail: str = Field(default="", description="评分细节")


class MatchingResult(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    dimension_scores: list[MatchingScore] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    summary: str = Field(default="")


# ==================== 简历优化 ====================

class OptimizationResult(BaseModel):
    optimized_text: str = Field(default="")
    changes_summary: list[str] = Field(default_factory=list)
    word_polish: list[dict] = Field(default_factory=list)
    skill_additions: list[str] = Field(default_factory=list)
    weakness_fixes: list[str] = Field(default_factory=list)


# ==================== 面试 & 分析 ====================

class InterviewQuestion(BaseModel):
    question: str = Field(...)
    category: str = Field(default="技术")
    difficulty: str = Field(default="中等")
    suggested_answer: str = Field(default="")


class SkillGap(BaseModel):
    skill_name: str = Field(...)
    required_level: str = Field(default="")
    current_level: str = Field(default="")
    gap_severity: str = Field(default="中")
    improvement_plan: str = Field(default="")


class RiskPoint(BaseModel):
    risk: str = Field(...)
    severity: str = Field(default="中")
    suggestion: str = Field(default="")


# ==================== 综合 ====================

class ComprehensiveAnalysis(BaseModel):
    matching: Optional[MatchingResult] = None
    optimization: Optional[OptimizationResult] = None
    interview_questions: list[InterviewQuestion] = Field(default_factory=list)
    skill_gaps: list[SkillGap] = Field(default_factory=list)
    risk_points: list[RiskPoint] = Field(default_factory=list)


class AnalysisRequest(BaseModel):
    """分析请求 - 包含简历、JD、API配置"""
    resume_text: str = Field(..., min_length=10)
    jd_text: str = Field(..., min_length=10)
    api_config: APIConfig = Field(default_factory=APIConfig)


class AnalysisResponse(BaseModel):
    status: str = "success"
    data: Optional[ComprehensiveAnalysis] = None
    error: str = ""
