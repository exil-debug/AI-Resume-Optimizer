"""
Streamlit 前端工具函数

封装API调用、颜色主题等通用工具。
所有后端请求通过此模块统一发送。
"""

import json
import urllib.request
import urllib.error
from typing import Optional

API_BASE_URL = "http://localhost:8765/api"


def api_health_check() -> bool:
    try:
        req = urllib.request.Request(f"{API_BASE_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def analyze_resume(
    resume_text: str,
    jd_text: str,
    api_key: str = "",
    base_url: str = "https://api.deepseek.com/v1",
    model: str = "deepseek-chat",
) -> dict:
    """
    提交简历+JD+API配置进行完整分析。

    Args:
        resume_text: 简历文本
        jd_text: 岗位JD文本
        api_key: API密钥
        base_url: API端点地址
        model: 模型名称

    Returns:
        分析结果字典
    """
    payload = json.dumps(
        {
            "resume_text": resume_text,
            "jd_text": jd_text,
            "api_config": {
                "provider": "custom",
                "api_key": api_key,
                "base_url": base_url,
                "model": model,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")

    req = urllib.request.Request(
        url=f"{API_BASE_URL}/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"status": "error", "error": f"HTTP {e.code}: {body[:300]}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ---------- 颜色工具 ----------

SCORE_COLORS = {"high": "#10b981", "medium": "#f59e0b", "low": "#ef4444"}


def get_score_color(score: int) -> str:
    if score >= 80:
        return SCORE_COLORS["high"]
    elif score >= 60:
        return SCORE_COLORS["medium"]
    else:
        return SCORE_COLORS["low"]


def get_score_label(score: int) -> str:
    if score >= 80:
        return "高度匹配"
    elif score >= 60:
        return "部分匹配"
    elif score >= 40:
        return "低度匹配"
    else:
        return "不匹配"


def get_severity_color(severity: str) -> str:
    s = severity.strip().lower()
    if s in ("高", "high"):
        return "#ef4444"
    elif s in ("中", "medium"):
        return "#f59e0b"
    else:
        return "#6b7280"
