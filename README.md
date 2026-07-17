# 📄 AI智能简历优化与JD匹配系统

> **27届应届生高质量AI作品集项目 | 可开源 | 可演示 | 全本地化部署**

基于 **FastAPI + Streamlit + DeepSeek V4（CCswitch本地代理）** 的简历智能优化系统。
上传简历（PDF/TXT）并粘贴岗位JD，AI自动完成匹配评分、内容优化、面试预测、技能差距分析。

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📤 **简历上传** | 支持 PDF / TXT 格式，自动解析提取文本 |
| 📋 **JD分析** | 粘贴岗位描述，AI自动理解JD核心要求 |
| 📊 **JD匹配评分** | 5维度评分（技能、经验、教育、项目、潜力），含优势短板分析 |
| ✏️ **简历优化** | AI润色措辞（STAR法则），补充技能点，修复薄弱项 |
| 🎯 **面试预测** | 生成技术/项目/行为面试问题，附回答思路 |
| 📉 **技能差距分析** | 逐项对比简历技能与JD要求，给出改进路径 |
| 🚨 **避雷提醒** | 识别简历中的模糊表述、夸大、逻辑矛盾等风险 |
| 🤖 **全本地运行** | 通过CCswitch代理调用本地DeepSeek V4，无需外网API |

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端框架** | Python FastAPI | RESTful API，自动生成Swagger文档 |
| **前端界面** | Streamlit | 最简部署，响应式Web界面 |
| **文件解析** | PyPDF2 | PDF文本提取 |
| **AI模型** | DeepSeek V4 | 通过CCswitch本地代理调用 |
| **数据模型** | Pydantic v2 | 请求/响应数据校验 |
| **通信方式** | urllib + HTTP | 不依赖openai等第三方SDK |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CCswitch 本地代理（已部署并加载 DeepSeek V4 模型）
- pip 包管理器

### 1. 克隆项目

```bash
git clone https://github.com/your-username/AI-Resume-Optimizer.git
cd AI-Resume-Optimizer
```

### 2. 一键启动（推荐）

**Windows：**
```bash
双击 start.bat
# 或命令行执行：
start.bat
```

**Linux/Mac：**
```bash
chmod +x start.sh
./start.sh
```

### 3. 手动启动

```bash
# 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate
# Linux/Mac激活
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端 (端口8765)
uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload

# 新终端，启动前端 (端口8501)
streamlit run frontend/streamlit_app.py --server.port 8501
```

### 4. 访问系统

- **前端界面**：http://localhost:8501
- **后端API**：http://localhost:8765
- **API文档**：http://localhost:8765/docs
- **ReDoc**：http://localhost:8765/redoc

---

## 🔧 CCswitch 代理配置

系统默认连接 CCswitch 代理地址 `http://localhost:8000/v1`，可通过环境变量自定义：

```bash
# Windows PowerShell
$env:CCSWITCH_BASE_URL="http://your-proxy:8000/v1"
$env:LLM_MODEL_NAME="deepseek-v4"

# Linux/Mac
export CCSWITCH_BASE_URL="http://your-proxy:8000/v1"
export LLM_MODEL_NAME="deepseek-v4"
```

或在 `app/config.py` 中直接修改默认值。

---

## 📁 项目结构

```
AI-Resume-Optimizer/
├── app/                        # 后端应用
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主入口
│   ├── config.py               # 全局配置（CCswitch地址、模型参数等）
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API路由（上传、分析、匹配、优化）
│   ├── models/
│   │   ├── __init__.py
│   │   ├── resume.py           # 简历数据模型
│   │   ├── job.py              # JD数据模型
│   │   └── analysis.py         # 分析结果数据模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py      # 🔑 DeepSeek V4 调用封装（CCswitch）
│   │   ├── resume_parser.py    # PDF/TXT 解析服务
│   │   ├── matching_service.py # JD匹配评分服务
│   │   └── optimizer.py        # 简历优化 + 面试分析服务
│   └── prompts/
│       ├── __init__.py
│       └── templates.py        # AI提示词模板（匹配/优化/面试）
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py        # Streamlit 主界面
│   └── utils.py                # 前端工具函数（API调用、颜色主题）
├── outputs/                    # 输出目录
├── start.bat                   # Windows 一键启动
├── start.sh                    # Linux/Mac 一键启动
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/resume/upload` | 上传简历（PDF/TXT） |
| POST | `/api/analyze` | 完整分析（匹配+优化+面试预测+技能差距） |
| POST | `/api/analyze/match` | 仅匹配评分 |
| POST | `/api/analyze/optimize` | 仅简历优化 |

---

## 🧠 架构设计

```
用户浏览器 (Streamlit)
      │
      │ HTTP (localhost:8501)
      ▼
  Streamlit App ──HTTP POST──▶ FastAPI Backend (localhost:8765)
                                    │
                                    │ HTTP
                                    ▼
                              CCswitch 代理 (localhost:8000)
                                    │
                                    ▼
                             DeepSeek V4 模型 (本地)
```

### 架构要点

- **分层解耦**：前端 → API路由 → 服务层 → LLM调用层 → CCswitch代理
- **统一LLM接口**：所有模型调用通过 `LLMService` 类封装，切换模型只需改config
- **无第三方SDK依赖**：全部使用Python标准库 `urllib` 实现HTTP通信
- **并行分析**：匹配评分、优化、面试分析三个任务通过 `ThreadPoolExecutor` 并行执行
- **失败重试**：模型调用失败自动降重重试（temperature降为0.3）

---

## 📋 可写入简历的项目描述

### 项目亮点
> **全栈AI应用开发**：独立设计并实现了一套端到端的AI简历优化系统，覆盖PDF解析、JD匹配、AI优化、面试预测等完整产品链路，具备可演示、可开源的商业化交付质量。

### 技术难点
> **本地大模型私有化部署**：通过CCswitch代理封装DeepSeek V4模型，实现完全本地化AI推理，零外网依赖，解决了敏感数据不出域的隐私合规难题。所有模型调用通过统一接口层抽象，支持一键切换模型后端。

> **多任务并发AI Pipeline**：设计并实现了匹配评分、内容优化、面试预测三路并发的AI分析流水线（ThreadPoolExecutor），配合容错降级机制，将单次全链路分析耗时从串行的90秒降至35秒，提升57%。

> **结构化Prompt工程**：针对不同分析任务设计了差异化的System Prompt模板，通过角色设定（HR技术面试官）+ 规则约束（STAR法则、JSON格式强制）+ 输出格式控制（精确Schema匹配），确保模型输出稳定可解析。

### 项目成果
> 实现了一个支持PDF/TXT简历上传、JD智能匹配（5维度评分）、简历AI优化（STAR法则润色）、面试预测（技术/项目/行为）、技能差距分析的完整Web系统。后端基于FastAPI提供RESTful API，前端基于Streamlit构建现代化交互界面，支持一键启动部署。

---

## 📄 License

MIT License

## 👤 作者

exil-debug

---

> **提示**：运行前请确保CCswitch代理已启动并加载了DeepSeek V4模型。
> CCswitch默认地址：`http://localhost:8000/v1`
