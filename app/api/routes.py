"""
FastAPI API路由

提供简历上传、JD分析、匹配评分、优化、综合分析等RESTful API。
所有分析请求携带用户自定义的API配置（key/base_url/model）。
"""

import json
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.config import OUTPUT_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from app.models.analysis import AnalysisRequest, AnalysisResponse, ComprehensiveAnalysis
from app.models.resume import ResumeUploadResponse
from app.services.resume_parser import resume_parser
from app.services.matching_service import matching_service
from app.services.optimizer import optimization_service, interview_analysis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["简历分析"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "AI智能简历优化系统", "version": "1.0.0"}


@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    temp_dir = OUTPUT_DIR / "_temp"
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / file.filename

    try:
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"文件大小超过限制（{MAX_UPLOAD_SIZE_MB}MB）")

        with open(temp_path, "wb") as f:
            f.write(content)

        raw_text = resume_parser.extract_text(temp_path)
        cleaned_text = resume_parser.clean_text(raw_text)
        is_valid, msg = resume_parser.validate_resume_text(cleaned_text)
        if not is_valid:
            raise HTTPException(status_code=400, detail=msg)

        return ResumeUploadResponse(
            filename=file.filename,
            content=cleaned_text,
            length=len(cleaned_text),
            status="success",
            message="简历解析成功",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历解析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.post("/analyze", response_model=AnalysisResponse)
async def full_analysis(request: AnalysisRequest):
    """
    完整综合分析（匹配评分 + 简历优化 + 面试预测 + 技能差距 + 避雷点）

    请求体中需包含 resume_text, jd_text, api_config:
    {
        "resume_text": "...",
        "jd_text": "...",
        "api_config": {
            "provider": "deepseek",
            "api_key": "sk-xxx",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat"
        }
    }
    """
    resume_text = request.resume_text.strip()
    jd_text = request.jd_text.strip()
    api_config = request.api_config

    if not api_config or not api_config.api_key:
        return AnalysisResponse(
            status="error",
            error="请先填写 API Key 后再进行分析",
        )

    if len(resume_text) < 20:
        raise HTTPException(status_code=400, detail="简历文本过短")
    if len(jd_text) < 20:
        raise HTTPException(status_code=400, detail="JD文本过短")

    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            f1 = pool.submit(matching_service.analyze, resume_text, jd_text, api_config)
            f2 = pool.submit(optimization_service.optimize, resume_text, jd_text, api_config)
            f3 = pool.submit(interview_analysis_service.analyze, resume_text, jd_text, api_config)

            match_result = f1.result()
            optimize_result = f2.result()
            interview_result = f3.result()

        comprehensive = ComprehensiveAnalysis(
            matching=match_result,
            optimization=optimize_result,
            interview_questions=interview_result.get("interview_questions", []),
            skill_gaps=interview_result.get("skill_gaps", []),
            risk_points=interview_result.get("risk_points", []),
        )
        return AnalysisResponse(status="success", data=comprehensive)

    except ValueError as e:
        # API Key无效、余额不足等用户可处理的问题
        return AnalysisResponse(status="error", error=str(e))
    except ConnectionError as e:
        return AnalysisResponse(status="error", error=str(e))
    except Exception as e:
        logger.error(f"综合分析失败: {e}", exc_info=True)
        return AnalysisResponse(
            status="error",
            error=f"分析过程出错: {str(e)[:200]}",
        )
