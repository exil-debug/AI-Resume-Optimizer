"""
岗位JD数据模型

定义岗位描述（JD）相关的数据结构。
"""

from typing import Optional
from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    """岗位描述数据"""
    raw_text: str = Field(default="", description="原始JD文本")
    title: str = Field(default="", description="岗位名称")
    company: str = Field(default="", description="公司名称")
    required_skills: list[str] = Field(default_factory=list, description="硬性技能要求")
    soft_skills: list[str] = Field(default_factory=list, description="软性要求")
    responsibilities: list[str] = Field(default_factory=list, description="岗位职责")
    qualifications: list[str] = Field(default_factory=list, description="任职资格")
    preferred: list[str] = Field(default_factory=list, description="加分项")
    parsed: bool = Field(default=False, description="是否已解析")


class JobInput(BaseModel):
    """用户输入的JD（原始文本）"""
    content: str = Field(..., min_length=10, max_length=8000, description="JD文本")


class JobInputResponse(BaseModel):
    """JD输入响应"""
    content: str
    length: int
    status: str = "success"
