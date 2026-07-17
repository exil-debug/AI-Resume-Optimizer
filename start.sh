#!/bin/bash
# AI智能简历优化系统 - Linux/Mac 启动脚本

echo "============================================"
echo "  AI智能简历优化系统 - 启动脚本"
echo "============================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[信息] 创建Python虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境并安装依赖
echo "[信息] 激活虚拟环境并安装依赖..."
source venv/bin/activate

echo "[信息] 安装/更新依赖..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "[信息] 启动后端服务 (FastAPI) ..."
cd "$(dirname "$0")"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload &
BACKEND_PID=$!

echo "[信息] 等待后端启动..."
sleep 3

echo "[信息] 启动前端服务 (Streamlit) ..."
streamlit run frontend/streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "============================================"
echo "  系统启动完成！"
echo ""
echo "  后端地址: http://localhost:8765"
echo "  API文档:  http://localhost:8765/docs"
echo "  前端地址: http://localhost:8501"
echo "============================================"
echo ""
echo "按 Ctrl+C 停止所有服务..."

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
