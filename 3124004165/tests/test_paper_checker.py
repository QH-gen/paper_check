# -*- coding: utf-8 -*-
"""论文查重程序单元测试。

覆盖模块：
- text_processor: 文件读取（UTF-8/GBK）、编码异常、HTML 清洗、空文件
- similarity: 分词、词频统计、余弦相似度（相同/无关/空文本）
- main: 命令行集成测试（正常流程、参数错误、文件缺失）
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from similarity import (SimilarityError, build_word_frequency, calculate_similarity,
                        cosine_similarity, tokenize)
from text_processor import TextLoadError, clean_text, load_text, read_file

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TextProcessorTest(unittest.TestCase):
    """text_processor 模块测试。"""

    def setUp(self):
        # 每个用例独立的临时目录，用于存放动态生成的测试文件
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write(self, name, content, encoding="utf-8"):
        path = os.path.join(self.temp_dir, name)
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(path, mode, **({} if isinstance(content, bytes)
                                 else {"encoding": encoding})) as f:
            f.write(content)
        return path

    def test_read_utf8_file(self):
        """用例1: 正常读取 UTF-8 编码文件。"""
        path = os.path.join(DATA_DIR, "utf8_sample.txt")
        text = read_file(path)
        self.assertIn("活着前言", text)

    def test_read_gbk_file(self):
        """用例2: 自动识别并读取 GBK 编码文件。"""
        path = self._write("gbk.txt", "计算机科学与技术专业", encoding="gbk")
        text = read_file(path)
        self.assertEqual(text, "计算机科学与技术专业")

    def test_read_nonexistent_file(self):
        """用例3: 文件不存在时抛出 TextLoadError。"""
        with self.assertRaises(TextLoadError):
            read_file(os.path.join(self.temp_dir, "no_such_file.txt"))

    def test_read_undecodable_file(self):
        """用例4: 内容既非 UTF-8 也非 GBK 时抛出 TextLoadError。"""
        path = self._write("bad.bin", bytes([0xff, 0xfe, 0x81, 0x02, 0x99]))
        with self.assertRaises(TextLoadError):
            read_file(path)

    def test_clean_html_tags(self):
        """用例5: 清除 HTML 标签、script/style 块、实体与空白。"""
        raw = ("<html><head><style>body{color:red}</style>"
               "<script>var a=1;</script></head>"
               "<body><p>活着&nbsp;前言</p><br/></body></html>")
        self.assertEqual(clean_text(raw), "活着前言")

    def test_load_empty_file(self):
        """用例6: 空文件清洗后得到空字符串（由相似度模块负责报错）。"""
        path = self._write("empty.txt", "")
        self.assertEqual(load_text(path), "")


class SimilarityTest(unittest.TestCase):
    """similarity 模块测试。"""

    def test_tokenize_filters_punctuation(self):
        """用例7: 分词结果不包含纯标点词元。"""
        tokens = tokenize("今天是星期天，天气晴！真的吗？")
        self.assertTrue(tokens)
        self.assertTrue(all(any(ch.isalnum() for ch in t) for t in tokens))
        self.assertNotIn("，", tokens)

    def test_cosine_similarity_identical_text(self):
        """用例8: 完全相同的文本相似度为 1。"""
        text = "软件工程是研究和应用如何以系统性、规范化、可定量的过程化方法去开发和维护软件的学科。"
        freq = build_word_frequency(tokenize(text))
        self.assertAlmostEqual(cosine_similarity(freq, freq), 1.0, places=6)

    def test_cosine_similarity_unrelated_text(self):
        """用例9: 没有任何共同词语的文本相似度为 0。"""
        freq_a = build_word_frequency(tokenize("苹果香蕉橘子西瓜葡萄"))
        freq_b = build_word_frequency(tokenize("键盘鼠标显示器主机"))
        self.assertAlmostEqual(cosine_similarity(freq_a, freq_b), 0.0, places=6)

    def test_cosine_similarity_empty_vector(self):
        """用例10: 任一文本词频向量为空时抛出 SimilarityError。"""
        from collections import Counter
        freq_a = build_word_frequency(tokenize("今天天气很好"))
        with self.assertRaises(SimilarityError):
            cosine_similarity(freq_a, Counter())

    def test_calculate_similarity_plagiarized_sample(self):
        """用例11: 题目示例，抄袭版与原文应有较高重复率（0.5~1.0）。"""
        orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
        copy = "今天是周天，天气晴朗，我晚上要去看电影。"
        similarity = calculate_similarity(orig, copy)
        self.assertGreaterEqual(similarity, 0.5)
        self.assertLessEqual(similarity, 1.0)

    def test_calculate_similarity_empty_text(self):
        """用例12: 清洗后为空的文本无法计算相似度。"""
        with self.assertRaises(SimilarityError):
            calculate_similarity("", "今天天气很好")


class MainIntegrationTest(unittest.TestCase):
    """main.py 命令行集成测试。"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.main_path = os.path.join(os.path.dirname(__file__), "..", "main.py")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, self.main_path] + list(args),
            capture_output=True, text=True, timeout=30,
        )

    def test_main_normal_flow(self):
        """用例13: 正常流程，答案文件输出两位小数的重复率。"""
        answer_path = os.path.join(self.temp_dir, "ans.txt")
        result = self._run(
            os.path.join(DATA_DIR, "orig_sample.txt"),
            os.path.join(DATA_DIR, "copy_sample.txt"),
            answer_path,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(answer_path, encoding="utf-8") as f:
            answer = f.read()
        self.assertRegex(answer, r"^\d+\.\d{2}$")
        self.assertGreaterEqual(float(answer), 0.0)
        self.assertLessEqual(float(answer), 1.0)

    def test_main_wrong_argument_count(self):
        """用例14: 参数个数不足时退出码为 1 并提示用法。"""
        result = self._run(os.path.join(DATA_DIR, "orig_sample.txt"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("用法", result.stderr)

    def test_main_missing_input_file(self):
        """用例15: 输入文件不存在时退出码为 2 并给出错误信息。"""
        answer_path = os.path.join(self.temp_dir, "ans.txt")
        result = self._run(
            os.path.join(self.temp_dir, "no_such_file.txt"),
            os.path.join(DATA_DIR, "orig_sample.txt"),
            answer_path,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("文件读取错误", result.stderr)


if __name__ == "__main__":
    unittest.main()
