"""
Streamlit 前端主页面 - API接入版

AI智能简历优化系统
功能：用户输入API Key → 调用大模型 → 简历JD分析
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from frontend.utils import (
    API_BASE_URL,
    api_health_check,
    analyze_resume,
    get_score_color,
    get_score_label,
    get_severity_color,
)

st.set_page_config(page_title="AI智能简历优化系统", page_icon="📄", layout="wide", initial_sidebar_state="expanded")


# ==================== 预设API提供商 ====================
API_PROVIDERS = {
    "deepseek": {"name": "DeepSeek", "url": "https://api.deepseek.com/v1", "models": ["deepseek-chat", "deepseek-reasoner"], "default_model": "deepseek-chat"},
    "openai": {"name": "OpenAI", "url": "https://api.openai.com/v1", "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], "default_model": "gpt-4o-mini"},
    "siliconflow": {"name": "SiliconFlow", "url": "https://api.siliconflow.cn/v1", "models": ["Pro/DeepSeek-V2", "deepseek-ai/DeepSeek-V2.5", "Qwen/Qwen2.5-7B-Instruct"], "default_model": "Pro/DeepSeek-V2"},
    "custom": {"name": "自定义", "url": "", "models": [], "default_model": ""},
}


# ==================== CSS ====================
st.markdown("""
<style>
.main-header { text-align:center; padding:1.5rem 0 1rem; background:linear-gradient(135deg,#1e3a5f 0%,#2d6a9f 100%); border-radius:12px; margin-bottom:1.5rem; }
.main-header h1 { color:white !important; font-size:2rem; margin-bottom:0.3rem; font-weight:700; }
.main-header p { color:rgba(255,255,255,0.85); font-size:0.95rem; margin-top:0; }
.section-title { font-size:1.2rem; font-weight:600; margin-bottom:0.5rem; padding-bottom:0.3rem; border-bottom:2px solid #e5e7eb; }
.score-card { background:white; border-radius:10px; padding:1.2rem; box-shadow:0 1px 3px rgba(0,0,0,0.1); text-align:center; margin-bottom:1rem; }
.score-value { font-size:2.5rem; font-weight:700; margin:0.3rem 0; }
.score-label { font-size:0.85rem; color:#6b7280; }
.dimension-item { display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0; border-bottom:1px solid #f3f4f6; }
.dimension-name { font-size:0.9rem; flex:1; }
.dimension-bar { flex:2; height:8px; background:#e5e7eb; border-radius:4px; margin:0 1rem; overflow:hidden; }
.dimension-fill { height:100%; border-radius:4px; transition:width 0.5s ease; }
.dimension-score { font-size:0.9rem; font-weight:600; min-width:2.2rem; text-align:right; }
.strength-badge { display:inline-block; background:#d1fae5; color:#065f46; padding:0.2rem 0.6rem; border-radius:6px; font-size:0.8rem; margin:0.15rem; }
.weakness-badge { display:inline-block; background:#fee2e2; color:#991b1b; padding:0.2rem 0.6rem; border-radius:6px; font-size:0.8rem; margin:0.15rem; }
.risk-tag { display:inline-block; padding:0.15rem 0.5rem; border-radius:4px; font-size:0.75rem; font-weight:600; color:white; }
.tag-high { background:#ef4444; }
.tag-medium { background:#f59e0b; }
.tag-low { background:#6b7280; }
.optimize-diff { background:#f0fdf4; border-left:3px solid #22c55e; padding:0.5rem 0.8rem; margin:0.3rem 0; border-radius:0 6px 6px 0; font-size:0.85rem; }
.qa-box { background:#f9fafb; border-radius:8px; padding:1rem; margin:0.5rem 0; border:1px solid #e5e7eb; }
.qa-question { font-weight:600; color:#1e3a5f; margin-bottom:0.3rem; }
.qa-answer { color:#374151; font-size:0.9rem; }
.gap-item { background:white; border-radius:8px; padding:0.8rem; margin:0.5rem 0; border:1px solid #e5e7eb; }
.api-box { background:#f0f7ff; border:1px solid #bfdbfe; border-radius:8px; padding:0.8rem 1rem; margin:0.5rem 0; }
.stButton>button { background:#1e3a5f; color:white; border:none; border-radius:8px; padding:0.4rem 1.2rem; font-weight:500; }
.stButton>button:hover { background:#2d6a9f; }
.footer { text-align:center; color:#9ca3af; font-size:0.8rem; padding:2rem 0 1rem; border-top:1px solid #e5e7eb; margin-top:3rem; }
</style>
""", unsafe_allow_html=True)


# ==================== 侧边栏 ====================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🔑 API设置")
        with st.container():
            st.markdown('<div class="api-box">', unsafe_allow_html=True)

            # 提供商选择
            provider_key = st.selectbox(
                "API提供商",
                options=list(API_PROVIDERS.keys()),
                format_func=lambda k: API_PROVIDERS[k]["name"],
                index=0,
                key="provider_select",
                help="选择想要使用的AI模型服务商",
            )

            provider = API_PROVIDERS[provider_key]

            # API Key
            api_key = st.text_input(
                "API Key",
                type="password",
                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                key="api_key_input",
                help="输入你的API密钥，不会存储在服务器上",
            )

            # API地址
            if provider_key == "custom":
                base_url = st.text_input(
                    "API地址",
                    placeholder="https://your-api.com/v1",
                    key="base_url_input",
                )
            else:
                base_url = provider["url"]
                st.text_input("API地址", value=base_url, disabled=True, key="base_url_display")

            # 模型名称
            if provider_key == "custom":
                model = st.text_input("模型名称", placeholder="如: gpt-4o-mini, deepseek-chat", key="model_input")
            else:
                model = st.selectbox("模型", options=provider["models"], key="model_select")

            st.markdown('</div>', unsafe_allow_html=True)

        # 保存到session
        st.session_state.api_key = api_key
        st.session_state.base_url = base_url
        st.session_state.model_name = model

        st.divider()

        # ====== 后端状态 ======
        backend_ok = api_health_check()
        status_color = "#10b981" if backend_ok else "#ef4444"
        st.markdown(f'<span style="color:{status_color};font-size:0.85rem;">{"●" if backend_ok else "○"} 后端服务{"已连接" if backend_ok else "未连接"}</span>', unsafe_allow_html=True)

        st.divider()

        # ====== 简历上传 ======
        st.markdown("### 📄 上传简历")
        uploaded_file = st.file_uploader("支持 PDF / TXT", type=["pdf", "txt"], label_visibility="collapsed")

        if uploaded_file is not None:
            from frontend.utils import API_BASE_URL as API_URL
            import urllib.request, io, uuid, json

            boundary = uuid.uuid4().hex
            body = io.BytesIO()
            body.write(f"--{boundary}\r\n".encode())
            body.write(f'Content-Disposition: form-data; name="file"; filename="{uploaded_file.name}"\r\n'.encode())
            body.write(b"Content-Type: application/octet-stream\r\n\r\n")
            body.write(uploaded_file.getvalue())
            body.write(f"\r\n--{boundary}--\r\n".encode())

            req = urllib.request.Request(
                url=f"{API_URL}/resume/upload",
                data=body.getvalue(),
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                if result.get("status") == "success":
                    st.session_state.resume_text = result.get("content", "")
                    st.session_state.resume_filename = uploaded_file.name
                    st.success(f"✅ 解析成功（{result.get('length', 0)}字符）")
                else:
                    st.error(f"❌ {result.get('message', '解析失败')}")
                    st.session_state.resume_text = ""
            except Exception as e:
                st.error(f"❌ 上传失败: {str(e)[:80]}")
        else:
            manual = st.text_area("或粘贴简历文本", placeholder="粘贴简历内容...", height=150, label_visibility="collapsed")
            if manual.strip():
                st.session_state.resume_text = manual.strip()
                st.session_state.resume_filename = "手动输入"

        st.divider()

        # ====== JD输入 ======
        st.markdown("### 📋 粘贴岗位JD")
        jd_text = st.text_area("JD", placeholder="粘贴岗位JD...\n\n岗位：...\n职责：...\n要求：...", height=200, label_visibility="collapsed")
        if jd_text.strip():
            st.session_state.jd_text = jd_text.strip()

        st.divider()

        # ====== 分析按钮 ======
        has_resume = bool(st.session_state.get("resume_text", ""))
        has_jd = bool(st.session_state.get("jd_text", ""))
        has_key = bool(st.session_state.get("api_key", ""))

        if not has_key:
            st.info("请先在「API设置」中输入 API Key")
        elif has_resume and has_jd:
            btn = st.button("🚀 开始完整分析", use_container_width=True, type="primary")
            if btn:
                run_full_analysis()
        else:
            st.info("请上传简历并粘贴JD后开始分析")

        if st.session_state.get("resume_text"):
            st.caption(f"📄 {st.session_state.resume_filename} ({len(st.session_state.resume_text)}字符)")
        if st.session_state.get("jd_text"):
            st.caption(f"📋 JD已加载 ({len(st.session_state.jd_text)}字符)")


# ==================== 主界面 ====================
def render_main_content():
    st.markdown("""
    <div class="main-header">
        <h1>📄 AI智能简历优化系统</h1>
        <p>接入大模型API · 简历JD匹配 · AI优化 · 面试预测</p>
    </div>
    """, unsafe_allow_html=True)

    analysis = st.session_state.get("analysis_result")
    if not analysis or analysis.get("status") != "success":
        render_welcome()
        return

    data = analysis.get("data", {})
    matching = data.get("matching") or {}
    overall = matching.get("overall_score", 0)
    score_color = get_score_color(overall)

    # 顶部概览
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
    with c1:
        st.markdown(f'<div class="score-card"><div class="score-label">综合匹配度</div><div class="score-value" style="color:{score_color}">{overall}</div><div style="color:{score_color};font-weight:500;">{get_score_label(overall)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="score-card"><div class="score-label">优势项</div><div class="score-value" style="color:#10b981">{len(matching.get("strengths",[]))}</div><div style="font-size:0.85rem;color:#6b7280;">项</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="score-card"><div class="score-label">待改进</div><div class="score-value" style="color:#f59e0b">{len(matching.get("weaknesses",[]))}</div><div style="font-size:0.85rem;color:#6b7280;">项</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="score-card"><div class="score-label">面试预测</div><div class="score-value" style="color:#3b82f6">{len(data.get("interview_questions",[]))}</div><div style="font-size:0.85rem;color:#6b7280;">个问题</div></div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📊 JD匹配评分", "✏️ 简历优化", "🎯 面试预测 & 分析"])

    with t1:
        render_matching(matching)
    with t2:
        render_optimize(data.get("optimization", {}))
    with t3:
        render_interview(data)


# ==================== Tab 内容 ====================

def render_matching(matching: dict):
    if not matching:
        st.info("暂无匹配评分数据"); return
    st.markdown('<div class="section-title">📈 各维度评分</div>', unsafe_allow_html=True)
    dims = matching.get("dimension_scores", [])
    dc1, dc2 = st.columns(2)
    for i, d in enumerate(dims):
        col = dc1 if i % 2 == 0 else dc2
        s = d.get("score", 0)
        c = get_score_color(s)
        with col:
            st.markdown(f'<div class="dimension-item"><span class="dimension-name">{d.get("dimension","")}</span><div class="dimension-bar"><div class="dimension-fill" style="width:{s}%;background:{c};"></div></div><span class="dimension-score" style="color:{c}">{s}</span></div>', unsafe_allow_html=True)
            st.caption(d.get("detail", ""))

    cs, cw = st.columns(2)
    with cs:
        st.markdown('<div class="section-title">✅ 简历优势</div>', unsafe_allow_html=True)
        for s in matching.get("strengths", []):
            st.markdown(f'<span class="strength-badge">✓ {s}</span>', unsafe_allow_html=True)
            st.write("")
    with cw:
        st.markdown('<div class="section-title">⚠️ 待改进项</div>', unsafe_allow_html=True)
        for w in matching.get("weaknesses", []):
            st.markdown(f'<span class="weakness-badge">△ {w}</span>', unsafe_allow_html=True)
            st.write("")

    st.divider()
    st.markdown('<div class="section-title">💡 改进建议</div>', unsafe_allow_html=True)
    for i, s in enumerate(matching.get("suggestions", []), 1):
        st.markdown(f"**{i}.** {s}")
    if matching.get("summary"):
        st.divider()
        st.info(matching["summary"])


def render_optimize(opt: dict):
    if not opt:
        st.info("暂无优化数据"); return
    st.markdown('<div class="section-title">📄 优化后简历</div>', unsafe_allow_html=True)
    t = opt.get("optimized_text", "")
    if t:
        with st.expander("查看优化后的完整简历", expanded=True):
            st.text_area("优化结果", value=t, height=400, label_visibility="collapsed")
            st.download_button("📥 下载优化简历", data=t, file_name="优化简历.txt", mime="text/plain")
    st.divider()
    st.markdown('<div class="section-title">📋 主要改动</div>', unsafe_allow_html=True)
    for c in opt.get("changes_summary", []):
        st.markdown(f"• {c}")
    st.divider()
    st.markdown('<div class="section-title">🔤 措辞润色明细</div>', unsafe_allow_html=True)
    for p in opt.get("word_polish", []):
        st.markdown(f'<div class="optimize-diff"><div><b>原措辞：</b>{p.get("original","")}</div><div><b>润色后：</b>{p.get("polished","")}</div><div style="color:#6b7280;font-size:0.8rem;">原因：{p.get("reason","")}</div></div>', unsafe_allow_html=True)
    cs, cf = st.columns(2)
    with cs:
        st.markdown('<div class="section-title">➕ 补充技能点</div>', unsafe_allow_html=True)
        for s in opt.get("skill_additions", []):
            st.markdown(f"• {s}")
    with cf:
        st.markdown('<div class="section-title">🔧 薄弱点修复</div>', unsafe_allow_html=True)
        for f in opt.get("weakness_fixes", []):
            st.markdown(f"• {f}")


def render_interview(data: dict):
    st.markdown('<div class="section-title">🚨 简历避雷点</div>', unsafe_allow_html=True)
    for rp in data.get("risk_points", []):
        sev = rp.get("severity", "中")
        col = get_severity_color(sev)
        st.markdown(f'<div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:0.8rem;margin:0.5rem 0;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;"><span style="font-weight:600;">{rp.get("risk","")}</span><span class="risk-tag" style="background:{col};">{sev}</span></div><div style="color:#6b7280;font-size:0.85rem;">💡 {rp.get("suggestion","")}</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-title">🎯 面试预测问题</div>', unsafe_allow_html=True)
    for q in data.get("interview_questions", []):
        st.markdown(f'<div class="qa-box"><div class="qa-question">❓ {q.get("question","")} <span style="font-size:0.75rem;color:#6b7280;font-weight:normal;">[{q.get("category","技术")}] · {q.get("difficulty","中等")}</span></div><div class="qa-answer"><b>建议回答思路：</b>{q.get("suggested_answer","")}</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="section-title">📊 岗位技能差距分析</div>', unsafe_allow_html=True)
    for g in data.get("skill_gaps", []):
        sev = g.get("gap_severity", "中")
        col = get_severity_color(sev)
        st.markdown(f'<div class="gap-item"><div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-weight:600;">{g.get("skill_name","")}</span><span class="risk-tag" style="background:{col};">差距{sev}</span></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;font-size:0.85rem;"><div><b>JD要求：</b>{g.get("required_level","")}</div><div><b>简历现状：</b>{g.get("current_level","")}</div></div><div style="margin-top:0.5rem;font-size:0.85rem;color:#065f46;background:#d1fae5;padding:0.3rem 0.6rem;border-radius:4px;">📈 <b>改进计划：</b>{g.get("improvement_plan","")}</div></div>', unsafe_allow_html=True)


# ==================== 欢迎页 ====================
def render_welcome():
    st.markdown("""
    ### 👋 欢迎使用AI智能简历优化系统

    **三步完成简历优化：**

    1️⃣ **设置API** — 左侧「API设置」中输入你的 API Key（支持 DeepSeek / OpenAI / 自定义）

    2️⃣ **上传简历 + 粘贴JD** — 上传PDF/TXT简历，粘贴目标岗位描述

    3️⃣ **开始分析** — AI自动完成匹配评分、简历优化、面试预测、技能差距分析

    > 💡 **系统特点**：用户自备API Key即可使用 · 支持所有兼容OpenAI接口的大模型 · 纯本地运行 · 敏感数据不出服务器

    ### 🔧 支持的API提供商
    | 提供商 | API地址 | 推荐模型 |
    |--------|---------|---------|
    | DeepSeek | api.deepseek.com | deepseek-chat |
    | OpenAI | api.openai.com | gpt-4o-mini |
    | SiliconFlow | api.siliconflow.cn | Pro/DeepSeek-V2 |
    | 自定义 | 任意兼容OpenAI的接口 | 任意模型 |
    """)

    st.divider()
    st.markdown("**项目信息**：AI智能简历优化与JD匹配系统 · FastAPI + Streamlit · 用户自备API Key")


# ==================== 分析主逻辑 ====================
def run_full_analysis():
    resume_text = st.session_state.get("resume_text", "")
    jd_text = st.session_state.get("jd_text", "")
    api_key = st.session_state.get("api_key", "")
    base_url = st.session_state.get("base_url", "https://api.deepseek.com/v1")
    model = st.session_state.get("model_name", "deepseek-chat")

    if not api_key:
        st.sidebar.error("请先输入 API Key")
        return
    if not resume_text or not jd_text:
        st.sidebar.error("请确保简历和JD都已填写")
        return

    with st.spinner("🔍 AI正在分析中（约30-120秒，取决于模型速度）..."):
        result = analyze_resume(resume_text, jd_text, api_key, base_url, model)

    if result.get("status") == "success":
        st.session_state.analysis_result = result
        st.sidebar.success("✅ 分析完成！")
        st.rerun()
    else:
        error_msg = result.get("error", "未知错误")
        st.session_state.analysis_result = None
        st.sidebar.error(f"❌ {error_msg}")


# ==================== 入口 ====================
def main():
    for k in ["resume_text", "jd_text", "analysis_result", "api_key", "base_url", "model_name"]:
        if k not in st.session_state:
            if k in ("resume_text", "jd_text", "api_key", "base_url", "model_name"):
                st.session_state[k] = "" if k != "base_url" else "https://api.deepseek.com/v1"
            else:
                st.session_state[k] = None

    render_sidebar()
    render_main_content()
    st.markdown('<div class="footer">AI智能简历优化系统 v1.0.0 | 用户自备API Key</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
