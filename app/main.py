"""
FastAPI 主入口

启动AI智能简历优化系统的后端服务。
"""

import logging
import sys
from pathlib import Path

# 将项目根目录加入系统路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import SERVICE_HOST, SERVICE_PORT

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# FastAPI 应用
app = FastAPI(
    title="AI智能简历优化系统",
    description="基于DeepSeek V4（本地CCswitch代理）的简历智能优化与JD匹配系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - 允许Streamlit前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """服务启动时校验CCswitch连接"""
    logger.info("=" * 50)
    logger.info("AI智能简历优化系统 v1.0.0 启动中...")
    logger.info(f"CCswitch代理地址: {SERVICE_HOST}:{SERVICE_PORT}")
    logger.info("=" * 50)


if __name__ == "__main__":
    logger.info(f"启动后端服务: http://{SERVICE_HOST}:{SERVICE_PORT}")
    uvicorn.run(
        "app.main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=False,
        log_level="info",
    )
