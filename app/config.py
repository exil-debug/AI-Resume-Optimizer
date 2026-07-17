"""
AI智能简历优化系统 - 配置层

集中管理API配置项。用户可在前端界面动态输入API Key等信息。
"""

import os
from pathlib import Path


# ---------- 项目路径 ----------
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------- 预设API提供商 ----------
API_PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["Pro/DeepSeek-V2", "deepseek-ai/DeepSeek-V2.5"],
        "default_model": "Pro/DeepSeek-V2",
    },
    "custom": {
        "name": "自定义",
        "base_url": "",
        "models": [],
        "default_model": "",
    },
}

# ---------- LLM请求参数默认值 ----------
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 4096
LLM_TIMEOUT = 120


# ---------- FastAPI 服务配置 ----------
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8765"))


# ---------- 文件限制 ----------
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_RESUME_LENGTH = 15000
MAX_JD_LENGTH = 8000
