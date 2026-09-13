# -*- coding: utf-8 -*-
"""论文查重程序入口。

用法：python main.py [原文文件] [抄袭版论文文件] [答案文件]

从命令行参数读入原文与抄袭版论文的绝对路径，
将两份文本的重复率（保留两位小数）写入答案文件。
"""

import sys

from similarity import SimilarityError, calculate_similarity
from text_processor import TextLoadError, load_text


def check_plagiarism(orig_path: str, plagiarized_path: str, answer_path: str) -> float:
    """查重主流程：读取两份论文，计算重复率并写入答案文件。

    :param orig_path: 原文文件路径
    :param plagiarized_path: 抄袭版论文文件路径
    :param answer_path: 答案文件路径
    :return: 重复率（0~1）
    :raises TextLoadError: 文件读取或解码失败
    :raises SimilarityError: 文本为空无法计算
    """
    orig_text = load_text(orig_path)
    plagiarized_text = load_text(plagiarized_path)

    similarity = calculate_similarity(orig_text, plagiarized_text)

    with open(answer_path, "w", encoding="utf-8") as answer_file:
        answer_file.write("%.2f" % similarity)
    return similarity


def main(argv) -> int:
    """程序入口：解析命令行参数并执行查重。

    :param argv: 命令行参数列表（含程序名）
    :return: 进程退出码，0 表示成功
    """
    if len(argv) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文文件] [答案文件]",
              file=sys.stderr)
        return 1

    orig_path, plagiarized_path, answer_path = argv[1], argv[2], argv[3]
    try:
        similarity = check_plagiarism(orig_path, plagiarized_path, answer_path)
    except TextLoadError as exc:
        print("文件读取错误: %s" % exc, file=sys.stderr)
        return 2
    except SimilarityError as exc:
        print("相似度计算错误: %s" % exc, file=sys.stderr)
        return 3

    print("重复率: %.2f" % similarity)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
