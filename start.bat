@echo off
chcp 65001 >nul
title AI智能简历优化系统
echo ============================================
echo   AI智能简历优化系统 - 启动脚本
echo ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

if not exist "venv\" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q

set STREAMLIT_CONSUMER_EMAIL=
set STREAMLIT_SERVER_HEADLESS=true

echo.
echo [信息] 启动后端 (FastAPI :8765) ...
start "AI-Resume-Backend" cmd /c "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8765"
timeout /t 3 /nobreak >nul

echo [信息] 启动前端 (Streamlit :8501) ...
start "AI-Resume-Frontend" cmd /c "set STREAMLIT_CONSUMER_EMAIL= && set STREAMLIT_SERVER_HEADLESS=true && call venv\Scripts\activate.bat && streamlit run frontend/streamlit_app.py --server.port 8501 --server.headless true"

echo.
echo ============================================
echo   启动完成！
echo   前端: http://localhost:8501
echo   后端: http://localhost:8765
echo   使用前请在页面左侧输入你的 API Key
echo ============================================
echo.
echo 按任意键打开前端...
pause >nul
start http://localhost:8501
pause >nul
