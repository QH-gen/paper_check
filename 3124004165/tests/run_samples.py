# -*- coding: utf-8 -*-
"""样例验证脚本：对测试文本目录下的所有抄袭版样例批量运行查重并计时。

用法：python tests/run_samples.py [测试文本目录]（默认为 ../测试文本）
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import check_plagiarism


def main():
    sample_dir = sys.argv[1] if len(sys.argv) > 1 else "../测试文本"
    orig_path = os.path.join(sample_dir, "orig.txt")
    if not os.path.exists(orig_path):
        print("未找到原文文件: %s" % orig_path, file=sys.stderr)
        return 1

    answer_dir = os.path.join(os.path.dirname(__file__), "answers")
    os.makedirs(answer_dir, exist_ok=True)

    total_start = time.time()
    for name in sorted(os.listdir(sample_dir)):
        if not (name.startswith("orig_") and name.endswith(".txt")):
            continue
        answer_path = os.path.join(answer_dir, "ans_%s" % name)
        start = time.time()
        similarity = check_plagiarism(
            orig_path, os.path.join(sample_dir, name), answer_path
        )
        elapsed = time.time() - start
        print("%-25s 重复率 %.2f  耗时 %.2fs" % (name, similarity, elapsed))

    print("总耗时 %.2fs" % (time.time() - total_start))
    return 0


if __name__ == "__main__":
    sys.exit(main())
