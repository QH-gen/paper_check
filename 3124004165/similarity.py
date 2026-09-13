# -*- coding: utf-8 -*-
"""相似度计算模块：分词、词频统计与余弦相似度。"""

import math
from collections import Counter

import jieba


class SimilarityError(Exception):
    """文本无法计算相似度（如为空）时抛出的异常。"""


def tokenize(text: str) -> list:
    """对文本分词，只保留含中文、字母或数字的词元。

    :param text: 清洗后的纯文本
    :return: 词元列表
    """
    tokens = jieba.lcut(text)
    return [
        token for token in tokens
        if any(ch.isalnum() for ch in token)
    ]


def build_word_frequency(tokens: list) -> Counter:
    """统计词元频率，得到词频向量。

    :param tokens: 词元列表
    :return: 以词为键、频次为值的 Counter
    """
    return Counter(tokens)


def cosine_similarity(freq_a: Counter, freq_b: Counter) -> float:
    """计算两个词频向量的余弦相似度。

    公式：sim(A, B) = (A · B) / (|A| * |B|)

    :param freq_a: 文本 A 的词频向量
    :param freq_b: 文本 B 的词频向量
    :return: 相似度，取值范围 [0, 1]
    :raises SimilarityError: 任一向量为空
    """
    if not freq_a or not freq_b:
        raise SimilarityError("文本为空，无法计算相似度")

    # 分子：两向量共同词的频次乘积之和
    dot_product = sum(
        count * freq_b[word]
        for word, count in freq_a.items()
        if word in freq_b
    )
    # 分母：两个向量模长的乘积
    norm_a = math.sqrt(sum(count ** 2 for count in freq_a.values()))
    norm_b = math.sqrt(sum(count ** 2 for count in freq_b.values()))

    return dot_product / (norm_a * norm_b)


def calculate_similarity(text_a: str, text_b: str) -> float:
    """计算两段文本的重复率（0~1 之间的浮点数）。

    :param text_a: 原文文本
    :param text_b: 抄袭版文本
    :return: 重复率
    :raises SimilarityError: 任一文本清洗后为空
    """
    freq_a = build_word_frequency(tokenize(text_a))
    freq_b = build_word_frequency(tokenize(text_b))
    return cosine_similarity(freq_a, freq_b)
