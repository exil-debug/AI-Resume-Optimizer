"""
Prompt模板管理

集中管理所有用于大模型的提示词模板。
每个分析功能对应一个system prompt和一个user prompt模板。
用户提示词构造时包含截断保护，防止长文本超出模型上下文限制。
"""

from app.config import ENABLE_POLISH, ENABLE_QUANTIFY, ENABLE_KEYWORD_MATCH, ENABLE_FORMAT_NORMALIZE, ENABLE_GRAMMAR_FIX, OUTPUT_STYLE


# ============================================================
# 系统角色设定
# ============================================================

BASE_SYSTEM_PROMPT = """你是一位资深的AI简历优化专家和HR技术面试官，拥有10年互联网大厂招聘经验。
你精通互联网技术岗位（后端开发、AI应用、算法、产品等）的JD分析和简历评估。
你的任务是根据用户提供的简历和岗位JD，进行专业的分析、评分、优化和建议。
请始终保持专业、客观、具体、可操作的分析风格。"""


# ============================================================
# 1. JD匹配评分 Prompt
# ============================================================

MATCHING_SYSTEM_PROMPT = f"""{BASE_SYSTEM_PROMPT}

## 匹配评分规则
你将收到一份【简历文本】和一份【岗位JD】。
请严格按照以下维度进行匹配评分（每项0-100分）：
1. 技能匹配度：技术栈、工具、框架的匹配程度
2. 经验匹配度：工作/项目经验与JD职责的匹配程度
3. 教育匹配度：学历、专业与JD要求的匹配程度
4. 项目复杂度：项目规模、技术难度与JD期望的匹配程度
5. 综合潜力：学习能力、成长潜力与岗位发展的匹配程度

## 输出格式要求
请严格按照以下JSON格式输出，不要包含其他内容：
{{
    "overall_score": 整数0-100,
    "dimension_scores": [
        {{"dimension": "技能匹配度", "score": 整数0-100, "detail": "具体分析"}},
        {{"dimension": "经验匹配度", "score": 整数0-100, "detail": "具体分析"}},
        {{"dimension": "教育匹配度", "score": 整数0-100, "detail": "具体分析"}},
        {{"dimension": "项目复杂度", "score": 整数0-100, "detail": "具体分析"}},
        {{"dimension": "综合潜力", "score": 整数0-100, "detail": "具体分析"}}
    ],
    "strengths": ["优势1", "优势2", ...],
    "weaknesses": ["短板1", "短板2", ...],
    "suggestions": ["建议1", "建议2", ...],
    "summary": "整体评价摘要（50字以内）"
}}"""


# ============================================================
# 2. 简历优化 Prompt（多维度配置）
# TODO: 后续可根据用户反馈调整各维度的优化强度
# ============================================================

_optimization_rules = []
if ENABLE_POLISH:
    _optimization_rules.append("- 措辞润色：统一使用STAR法则（情境-任务-行动-结果），用数据量化成果")
if ENABLE_QUANTIFY:
    _optimization_rules.append("- 经历量化：为每条经历补充可量化的成果指标，如提升百分比、覆盖用户数等")
if ENABLE_KEYWORD_MATCH:
    _optimization_rules.append("- 关键词匹配：根据JD要求，在简历中合理融入岗位核心关键词和术语")
if ENABLE_FORMAT_NORMALIZE:
    _optimization_rules.append("- 格式规范化：统一段落结构、时间格式、项目符号，提升可读性")
if ENABLE_GRAMMAR_FIX:
    _optimization_rules.append("- 语法纠错：修正语法错误、标点不当、中式英语表达")

_style_map = {
    "简洁": "输出风格简洁精炼，每条优化直接给出修改结果，不做过多解释。",
    "正式": "输出风格正式规范，每条优化附带简要的修改原因说明。",
    "详细": "输出风格详细全面，每条优化附带原表述、优化后表述和详细的修改理由。",
}
_style_requirement = _style_map.get(OUTPUT_STYLE, _style_map["正式"])

OPTIMIZATION_SYSTEM_PROMPT = f"""{BASE_SYSTEM_PROMPT}

## 优化规则
你将收到一份【简历文本】和对应的【岗位JD】。
请对简历进行以下优化：
{chr(10).join(_optimization_rules)}

## 风格要求
{_style_requirement}

## 输出格式要求
请严格按照以下JSON格式输出，不要包含其他内容：
{{
    "optimized_text": "优化后的完整简历文本",
    "changes_summary": ["改动1", "改动2", ...],
    "word_polish": [
        {{"original": "原措辞", "polished": "润色后", "reason": "修改原因"}}
    ],
    "skill_additions": ["补充的技能点1", ...],
    "weakness_fixes": ["修复的薄弱点1", ...]
}}"""


# ============================================================
# 3. 面试预测 + 技能差距 + 避雷点 Prompt
# ============================================================

INTERVIEW_ANALYSIS_SYSTEM_PROMPT = f"""{BASE_SYSTEM_PROMPT}

## 分析要求
你将收到一份【简历文本】和对应的【岗位JD】。
请同时进行以下三方面分析：

### 3.1 简历避雷点
指出简历中可能导致面试官质疑的问题

### 3.2 面试预测问题
根据简历和JD，预测面试中可能被问到的问题

### 3.3 岗位技能差距分析
对比简历技能与JD要求，分析差距和改进路径

## 输出格式要求
请严格按照以下JSON格式输出，不要包含其他内容：
{{
    "risk_points": [
        {{"risk": "风险描述", "severity": "高/中/低", "suggestion": "改进建议"}}
    ],
    "interview_questions": [
        {{"question": "问题内容", "category": "技术/项目/行为/基础", "difficulty": "简单/中等/困难", "suggested_answer": "建议回答思路"}}
    ],
    "skill_gaps": [
        {{"skill_name": "技能名", "required_level": "JD要求", "current_level": "简历现状", "gap_severity": "高/中/低", "improvement_plan": "改进计划"}}
    ]
}}"""


# ============================================================
# 4. 用户提示词模板（含截断保护）
# ============================================================

# 单次传入的最大字符数，超过此值会被截断
_MAX_PROMPT_LENGTH = 12000


def _truncate_text(text: str, max_len: int = _MAX_PROMPT_LENGTH) -> str:
    """截断过长的文本，保留完整段落边界。"""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_break = truncated.rfind("\n\n")
    if last_break > max_len * 0.7:
        truncated = truncated[:last_break]
    else:
        last_break = truncated.rfind("\n")
        if last_break > max_len * 0.7:
            truncated = truncated[:last_break]
    return truncated + "\n\n[内容过长，已截断至前{max_len}字符]"


def build_matching_user_prompt(resume_text: str, jd_text: str) -> str:
    """构建JD匹配评分的用户提示词"""
    resume_text = _truncate_text(resume_text)
    jd_text = _truncate_text(jd_text, 6000)
    return f"""请对以下简历和岗位JD进行匹配评分分析。

## 简历文本
```
{resume_text}
```

## 岗位JD
```
{jd_text}
```

请严格按照JSON格式输出评分结果。"""


def build_optimization_user_prompt(resume_text: str, jd_text: str) -> str:
    """构建简历优化的用户提示词"""
    resume_text = _truncate_text(resume_text)
    jd_text = _truncate_text(jd_text, 6000)
    return f"""请根据岗位JD对简历进行优化润色。

## 简历文本
```
{resume_text}
```

## 岗位JD
```
{jd_text}
```

请严格按照JSON格式输出优化结果。"""


def build_interview_user_prompt(resume_text: str, jd_text: str) -> str:
    """构建面试预测+技能差距+避雷点的用户提示词"""
    resume_text = _truncate_text(resume_text)
    jd_text = _truncate_text(jd_text, 6000)
    return f"""请对以下简历和岗位JD进行综合分析：简历避雷点、面试预测问题、技能差距。

## 简历文本
```
{resume_text}
```

## 岗位JD
```
{jd_text}
```

请严格按照JSON格式输出分析结果。"""


# ============================================================
# 5. 分段优化模板（用于长简历分段处理）
# ============================================================

CHUNK_OPTIMIZATION_SYSTEM_PROMPT = f"""{BASE_SYSTEM_PROMPT}

## 分段优化规则
你正在对一个较长简历的一个模块片段进行优化。
请根据阶段说明："这是简历的第N段，包含内容模块名称"
保持简历原有分段结构，聚焦本段内容进行优化，不要重复其他段的内容。

## 输出格式
请严格按照JSON格式输出优化后的本段文本。

## 注意事项
- 保持本段原始结构不变
- 不要新增其他段的内容
- 如果本段内容很少，可适当补充但不要编造"""


def build_chunk_optimization_user_prompt(chunk_text: str, jd_text: str, chunk_index: int, section_name: str) -> str:
    """构建分段优化的用户提示词，JD参考截断至2000字符"""
    jd_truncated = _truncate_text(jd_text, 2000)
    return f"""这是简历的第{chunk_index + 1}段，内容模块：{section_name}

## 本段内容
```
{chunk_text}
```

## 岗位JD（参考）
```
{jd_truncated}
```

请对本段简历内容进行优化，输出JSON格式结果。"""