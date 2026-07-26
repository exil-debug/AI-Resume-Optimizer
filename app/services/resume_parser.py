"""
简历解析服务

支持PDF和TXT格式简历的解析与文本提取。
PDF解析基于PyPDF2，TXT直接读取。
新增结构化提取功能，保留简历层级与分段信息后再传入模型。
"""

import re
from pathlib import Path
from typing import Optional

from app.models.resume import ResumeData, ResumeUploadResponse


# ---------- 解析器配置 ----------
_SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


class ResumeParser:
    """
    简历解析器

    支持上传PDF/TXT简历文件并提取文本内容。
    PDF解析使用PyPDF2，TXT直接读取。
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str | Path) -> str:
        """
        从PDF文件中提取文本内容。

        Args:
            file_path: PDF文件路径

        Returns:
            提取出的纯文本内容
        """
        import PyPDF2

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")

        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) == 0:
                raise ValueError("PDF文件为空，无法解析")
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"[第{page_num}页]\n{page_text.strip()}")

        return "\n\n".join(text_parts) if text_parts else ""

    @staticmethod
    def extract_text_from_txt(file_path: str | Path) -> str:
        """
        从TXT文件中提取文本内容。

        Args:
            file_path: TXT文件路径

        Returns:
            文件文本内容
        """
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()

    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        """
        通用文本提取：自动识别文件格式并提取内容。

        Args:
            file_path: 文件路径 (PDF或TXT)

        Returns:
            提取的纯文本
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return ResumeParser.extract_text_from_pdf(file_path)
        elif ext == ".txt":
            return ResumeParser.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}，支持: {_SUPPORTED_EXTENSIONS}")

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        清洗简历文本：去除多余空白、乱码字符等。

        Args:
            raw_text: 原始文本

        Returns:
            清洗后的文本
        """
        # 替换多种换行符为统一格式
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # 去除多余空白行（最多保留一个空行）
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 去除每行首尾空格
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        # 去除不可见控制字符
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

        return text.strip()

    @staticmethod
    def structure_text(raw_text: str) -> str:
        """
        将简历文本按段落/标题拆分为结构化格式。

        保留层级关系，添加小节标签，便于大模型理解简历结构。
        对后续优化环节的格式还原度有明显提升。

        Returns:
            带结构化标记的文本
        """
        text = ResumeParser.clean_text(raw_text)
        lines = text.split("\n")
        structured = []
        section_labels = ["教育背景", "教育经历", "工作经历", "实习经历",
                          "项目经历", "项目经验", "技能", "专业技能",
                          "个人简介", "自我评价", "自我介绍", "证书",
                          "获奖", "荣誉", "语言", "兴趣爱好"]

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                structured.append("")
                continue
            # 识别可能的小标题行并添加标记
            matched = any(s in line_stripped for s in section_labels)
            if matched and (len(line_stripped) < 30 or line_stripped.endswith("：") or line_stripped.endswith(":")):
                structured.append(f"【{line_stripped}】")
            else:
                structured.append(f"  {line_stripped}")

        return "\n".join(structured)

    @staticmethod
    def validate_resume_text(text: str) -> tuple[bool, str]:
        """
        验证简历文本是否有效。

        Args:
            text: 简历文本

        Returns:
            (是否有效, 提示消息)
        """
        if not text or not text.strip():
            return False, "简历内容为空，请确认上传了正确的简历文件。"
        if len(text.strip()) < 20:
            return False, "简历内容过短（不足20字符），请确认上传了完整的简历文件。"
        if len(text) > 15000:
            return False, "简历内容过长（超过15000字符），请精简后重试。"
        return True, ""


# 全局单例
resume_parser = ResumeParser()