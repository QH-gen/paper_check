# -*- coding: utf-8 -*-
"""文本预处理模块：负责文件读取、编码识别、HTML 标签清洗与正文提取。"""

import re


class TextLoadError(Exception):
    """文件读取或解码失败时抛出的异常。"""


# 匹配 HTML 中的 script/style 块（含标签本身），这类内容不属于正文
_SCRIPT_STYLE_PATTERN = re.compile(
    r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)
# 匹配其余所有 HTML 标签
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
# 匹配 HTML 实体（如 &nbsp; &amp; 等）
_HTML_ENTITY_PATTERN = re.compile(r"&[a-zA-Z]+;|&#\d+;")
# 匹配空白字符（含全角空格）
_WHITESPACE_PATTERN = re.compile(r"[\s　]+")


def read_file(file_path: str) -> str:
    """读取文本文件内容，自动尝试 UTF-8 与 GBK 编码。

    :param file_path: 文件绝对路径
    :return: 文件原始文本
    :raises TextLoadError: 文件不存在或编码无法识别
    """
    try:
        with open(file_path, "rb") as raw_file:
            raw_bytes = raw_file.read()
    except OSError as exc:
        raise TextLoadError("无法读取文件: %s (%s)" % (file_path, exc)) from exc

    for encoding in ("utf-8", "gbk"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise TextLoadError("文件编码无法识别（已尝试 UTF-8 / GBK）: %s" % file_path)


def clean_text(text: str) -> str:
    """清洗文本：去除 HTML 标签、HTML 实体和多余空白。

    :param text: 原始文本
    :return: 仅含正文内容的纯文本
    """
    text = _SCRIPT_STYLE_PATTERN.sub("", text)
    text = _HTML_TAG_PATTERN.sub("", text)
    text = _HTML_ENTITY_PATTERN.sub("", text)
    text = _WHITESPACE_PATTERN.sub("", text)
    return text.strip()


def load_text(file_path: str) -> str:
    """读取文件并完成清洗，返回可用于分词的纯文本。

    :param file_path: 文件绝对路径
    :return: 清洗后的文本
    :raises TextLoadError: 读取或解码失败
    """
    return clean_text(read_file(file_path))
