"""
简历数据模型

定义简历解析后的结构化数据类，包括基本信息、教育背景、
技能、项目经历、工作经历等。
"""

from typing import Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """教育背景"""
    school: str = Field(default="", description="学校名称")
    major: str = Field(default="", description="专业")
    degree: str = Field(default="", description="学历")
    period: str = Field(default="", description="时间段")


class Project(BaseModel):
    """项目经历"""
    name: str = Field(default="", description="项目名称")
    role: str = Field(default="", description="担任角色")
    tech_stack: str = Field(default="", description="技术栈")
    description: str = Field(default="", description="项目描述")
    highlights: str = Field(default="", description="项目亮点/成果")


class WorkExperience(BaseModel):
    """工作/实习经历"""
    company: str = Field(default="", description="公司名称")
    position: str = Field(default="", description="职位")
    period: str = Field(default="", description="时间段")
    responsibilities: str = Field(default="", description="工作职责")
    achievements: str = Field(default="", description="工作成果")


class ResumeData(BaseModel):
    """完整的简历解析数据"""
    raw_text: str = Field(default="", description="原始文本")
    name: str = Field(default="", description="姓名")
    phone: str = Field(default="", description="电话")
    email: str = Field(default="", description="邮箱")
    education: list[Education] = Field(default_factory=list, description="教育背景")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    projects: list[Project] = Field(default_factory=list, description="项目经历")
    work_experience: list[WorkExperience] = Field(default_factory=list, description="工作/实习经历")
    self_intro: str = Field(default="", description="个人简介")
    parsed: bool = Field(default=False, description="是否已解析")


class ResumeUploadResponse(BaseModel):
    """简历上传响应"""
    filename: str
    content: str
    length: int
    status: str = "success"
    message: str = ""
