# 论文查重——软件工程第一次个人编程作业

> **GitHub 仓库链接**：[https://github.com/QH-gen/paper_check](https://github.com/QH-gen/paper_check)
>
> 学号：3124004165

---

## 一、项目概述

本题要求设计一个论文查重算法：给定原文文件和抄袭版论文文件，计算并输出两份文本的重复率。

输入输出采用命令行参数传递文件路径：

```bash
python main.py [原文文件] [抄袭版论文文件] [答案文件]
```

答案文件输出浮点型重复率，精确到小数点后两位。

---

## 二、PSP 表格（预估耗时）

在动手编码之前，先对开发各阶段所需时间做出预估：

| Personal Software Process Stages | 预估耗时（分钟） |
| --- | --- |
| **Planning 计划** | **20** |
| · Estimate · 估计这个任务需要多少时间 | 20 |
| **Development 开发** | **380** |
| · Analysis · 需求分析 (包括学习新技术) | 60 |
| · Design Spec · 生成设计文档 | 30 |
| · Design Review · 设计复审 | 20 |
| · Coding Standard · 代码规范 | 20 |
| · Design · 具体设计 | 40 |
| · Coding · 具体编码 | 120 |
| · Code Review · 代码复审 | 40 |
| · Test · 测试 | 50 |
| **Reporting 报告** | **80** |
| · Test Report · 测试报告 | 40 |
| · Size Measurement · 计算工作量 | 15 |
| · Postmortem · 事后总结 | 25 |
| **合计** | **480** |

---

## 三、计算模块接口的设计与实现

### 3.1 代码组织

项目采用模块化设计，共 3 个 Python 源文件，各模块职责清晰：

```
3124004165/
├── main.py              # 入口模块：解析命令行参数，串联完整流程
├── text_processor.py    # 文本预处理模块：文件读取、编码识别、HTML 清洗
├── similarity.py        # 相似度计算模块：分词、词频统计、余弦相似度
├── requirements.txt     # 第三方依赖（jieba）
├── PSP.md               # PSP 表格
└── tests/
    ├── test_paper_checker.py   # 单元测试（15 个用例）
    └── data/                   # 测试数据文件
```

### 3.2 模块关系与函数设计

**text_processor.py** — 文本预处理模块

| 函数 | 功能 |
|------|------|
| `read_file(file_path)` | 以二进制读入文件，依次尝试 UTF-8 / GBK 解码 |
| `clean_text(text)` | 正则清洗：去除 HTML 标签、script/style 块、HTML 实体、空白字符 |
| `load_text(file_path)` | 组合函数：`clean_text(read_file(file_path))` |

**similarity.py** — 相似度计算模块

| 函数 | 功能 |
|------|------|
| `tokenize(text)` | jieba 分词，过滤纯标点词元 |
| `build_word_frequency(tokens)` | 统计词频，返回 Counter 对象 |
| `cosine_similarity(freq_a, freq_b)` | 计算两个词频向量的余弦相似度 |
| `calculate_similarity(text_a, text_b)` | 端到端计算两段文本的重复率 |

**main.py** — 入口模块

| 函数 | 功能 |
|------|------|
| `check_plagiarism(orig, copy, answer)` | 主流程：读取 → 计算 → 写入答案文件 |
| `main(argv)` | 解析命令行参数，异常处理，返回退出码 |

### 3.3 关键函数流程图

```
┌─────────────────────────────────────────────────┐
│                  main(argv)                      │
│  解析命令行参数 [原文] [抄袭版] [答案文件]          │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│             check_plagiarism(...)                │
│                                                 │
│  ┌───────────────┐    ┌───────────────────┐     │
│  │ load_text     │    │ load_text         │     │
│  │ (原文)        │    │ (抄袭版)          │     │
│  │  ├─read_file  │    │  ├─read_file      │     │
│  │  │ 编码识别    │    │  │ 编码识别        │     │
│  │  └─clean_text │    │  └─clean_text     │     │
│  │   HTML清洗    │    │   HTML清洗        │     │
│  └──────┬────────┘    └────────┬──────────┘     │
│         │                      │                │
│         ▼                      ▼                │
│  ┌──────────────────────────────────────────┐   │
│  │        calculate_similarity(...)          │   │
│  │                                          │   │
│  │  tokenize(A) ──► build_word_frequency    │   │
│  │  tokenize(B) ──► build_word_frequency    │   │
│  │              │                           │   │
│  │              ▼                           │   │
│  │       cosine_similarity(freqA, freqB)    │   │
│  └──────────────────┬───────────────────────┘   │
│                     │                           │
│                     ▼                           │
│  写入答案文件 ("%.2f")                            │
└─────────────────────────────────────────────────┘
```

### 3.4 算法关键

**核心算法：余弦相似度（Cosine Similarity）**

1. **文本预处理**：以二进制读入 → 尝试 UTF-8 / GBK 解码 → 正则去除 HTML 标签、script/style 块、HTML 实体和所有空白字符
2. **中文分词**：使用 jieba 精确模式分词，过滤纯标点词元
3. **词频向量构建**：统计每个词的出现频次，将文本映射为高维稀疏向量
4. **余弦相似度计算**：

$$\text{sim}(A, B) = \frac{A \cdot B}{|A| \times |B|} = \frac{\sum_{w \in A \cap B} f_A(w) \times f_B(w)}{\sqrt{\sum_{w \in A} f_A(w)^2} \times \sqrt{\sum_{w \in B} f_B(w)^2}}$$

结果取值 [0, 1]，越接近 1 表示重复率越高。

**独到之处**：
- 自动识别 UTF-8 / GBK 双编码，兼容中文文本常见编码
- HTML 清洗覆盖 `<script>`/`<style>` 块、标签、实体，避免非正文内容干扰分词
- 词频向量使用 `collections.Counter`，底层哈希表查询 O(1)，整体计算效率高

---

## 四、计算模块性能改进

### 4.1 性能分析

使用 Python 内置 cProfile 工具对真实样例进行性能分析：

```bash
python -m cProfile -s cumtime main.py orig.txt orig_0.8_del.txt ans.txt
```

**性能分析结果**（orig.txt vs orig_0.8_del.txt，总耗时 0.574s）：

| 函数 | 调用次数 | 累计耗时 | 占比 |
|------|----------|----------|------|
| `marshal.load`（jieba 词典加载） | 1 | 0.430s | **74.9%** |
| `jieba.__cut_DAG`（DAG 分词） | 11,839 | 0.519s | 90.4% |
| `jieba.get_DAG`（构建 DAG） | 1,808 | 0.449s | 78.2% |
| `cosine_similarity` | 1 | <0.001s | <0.2% |

**消耗最大的函数**：`jieba.initialize()` 中的 `marshal.load`（加载词典到内存），占 0.430s / 0.574s = **74.9%**。

### 4.2 性能改进思路

| 优化方向 | 方案 | 效果 |
|----------|------|------|
| 词典加载 | jieba 缓存已加载（第二次运行直接读取 `jieba.cache`） | 0.430s → 接近 0 |
| 分词算法 | 对大批量文本可考虑轻量级 n-gram 切分替代 jieba | 省去词典加载 |
| 词频计算 | 使用 `Counter` 哈希表，已是最优 | 无需优化 |

**实测改进效果**：

- 首次运行（需加载 jieba 词典）：0.574s
- 后续运行（词典已缓存）：~0.14s
- 5 个真实样例全部在 **0.75s 内完成**，远低于 5 秒限时

### 4.3 真实样例验证

| 样例文件 | 重复率 | 耗时 |
|----------|--------|------|
| orig_0.8_add.txt | 0.99 | 0.52s |
| orig_0.8_del.txt | 0.99 | 0.05s |
| orig_0.8_dis_1.txt | 1.00 | 0.05s |
| orig_0.8_dis_10.txt | 0.99 | 0.06s |
| orig_0.8_dis_15.txt | 0.98 | 0.06s |

---

## 五、单元测试展示

### 5.1 测试设计思路

采用**白盒测试**方法，针对每个模块的关键函数设计用例：

- **text_processor 模块**：覆盖正常编码、异常编码、HTML 清洗、文件不存在等场景
- **similarity 模块**：覆盖正常相似度、边界值（相同文本=1、无关文本=0）、空文本异常
- **main.py 模块**：覆盖正常流程、参数错误、文件缺失等集成场景

### 5.2 测试用例列表

| # | 测试类 | 测试方法 | 测试目标 |
|---|--------|----------|----------|
| 1 | TextProcessorTest | test_read_utf8_file | 正常读取 UTF-8 文件 |
| 2 | TextProcessorTest | test_read_gbk_file | 自动识别 GBK 编码 |
| 3 | TextProcessorTest | test_read_nonexistent_file | 文件不存在 → TextLoadError |
| 4 | TextProcessorTest | test_read_undecodable_file | 编码无法识别 → TextLoadError |
| 5 | TextProcessorTest | test_clean_html_tags | HTML 标签清洗 |
| 6 | TextProcessorTest | test_load_empty_file | 空文件处理 |
| 7 | SimilarityTest | test_tokenize_filters_punctuation | 过滤纯标点词元 |
| 8 | SimilarityTest | test_cosine_similarity_identical_text | 相同文本相似度=1 |
| 9 | SimilarityTest | test_cosine_similarity_unrelated_text | 无关文本相似度=0 |
| 10 | SimilarityTest | test_cosine_similarity_empty_vector | 空向量 → SimilarityError |
| 11 | SimilarityTest | test_calculate_similarity_plagiarized_sample | 题目示例重复率范围 |
| 12 | SimilarityTest | test_calculate_similarity_empty_text | 空文本 → SimilarityError |
| 13 | MainIntegrationTest | test_main_normal_flow | 正常流程，答案文件格式正确 |
| 14 | MainIntegrationTest | test_main_wrong_argument_count | 参数不足 → 退出码 1 |
| 15 | MainIntegrationTest | test_main_missing_input_file | 文件不存在 → 退出码 2 |

### 5.3 测试代码示例

**示例：HTML 标签清洗测试（用例 5）**

```python
def test_clean_html_tags(self):
    """用例5: 清除 HTML 标签、script/style 块、实体与空白。"""
    raw = ("<html><head><style>body{color:red}</style>"
           "<script>var a=1;</script></head>"
           "<body><p>活着&nbsp;前言</p><br/></body></html>")
    self.assertEqual(clean_text(raw), "活着前言")
```

**示例：余弦相似度边界测试（用例 8、9）**

```python
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
```

### 5.4 测试覆盖率

使用 `coverage` 工具生成的覆盖率报告：

```
Name                          Stmts   Miss  Cover
--------------------------------------------------
similarity.py                    20      0   100%
text_processor.py                26      0   100%
tests\test_paper_checker.py      98      1    99%
--------------------------------------------------
TOTAL                           144      1    99%
```

- `similarity.py` 和 `text_processor.py` 均达到 **100% 语句覆盖率**
- 总计 **99% 覆盖率**（测试文件本身 `if __name__ == "__main__"` 分支未覆盖）

### 5.5 测试设计评价

本测试用例设计覆盖了：
- **正常路径**：UTF-8/GBK 文件读取、正常分词、相似度计算
- **边界值**：相同文本（相似度=1）、无关文本（相似度=0）、空文本
- **异常路径**：文件不存在、编码错误、参数不足
- **集成测试**：完整的命令行流程、答案文件格式

共 15 个测试用例，覆盖了主要功能路径和异常场景，能有效保证程序在各种输入情况下的正确性。

---

## 六、异常处理说明

### 6.1 异常类型总览

| 异常类 | 定义位置 | 触发场景 | 退出码 |
|--------|----------|----------|--------|
| `TextLoadError` | text_processor.py | 文件不存在、无权限、编码无法识别 | 2 |
| `SimilarityError` | similarity.py | 文本清洗后为空，无法构建词频向量 | 3 |
| 参数错误 | main.py | 命令行参数个数不为 3 | 1 |

### 6.2 TextLoadError — 文件读取异常

**设计目标**：当文件不存在、无读取权限、或编码既非 UTF-8 也非 GBK 时，给出明确的错误信息并以退出码 2 终止程序。

```python
class TextLoadError(Exception):
    """文件读取或解码失败时抛出的异常。"""
```

**对应测试用例**（用例 3、4）：

```python
def test_read_nonexistent_file(self):
    """用例3: 文件不存在时抛出 TextLoadError。"""
    with self.assertRaises(TextLoadError):
        read_file(os.path.join(self.temp_dir, "no_such_file.txt"))

def test_read_undecodable_file(self):
    """用例4: 内容既非 UTF-8 也非 GBK 时抛出 TextLoadError。"""
    path = self._write("bad.bin", bytes([0xff, 0xfe, 0x81, 0x02, 0x99]))
    with self.assertRaises(TextLoadError):
        read_file(path)
```

**场景说明**：
- 用例 3 模拟了文件路径输入错误的场景
- 用例 4 模拟了文件内容损坏或非文本文件的场景

### 6.3 SimilarityError — 相似度计算异常

**设计目标**：当文本清洗后为空（纯空白、纯标点等）导致无法构建词频向量时，抛出异常避免除零错误。

```python
class SimilarityError(Exception):
    """文本无法计算相似度（如为空）时抛出的异常。"""
```

**对应测试用例**（用例 10、12）：

```python
def test_cosine_similarity_empty_vector(self):
    """用例10: 任一文本词频向量为空时抛出 SimilarityError。"""
    from collections import Counter
    freq_a = build_word_frequency(tokenize("今天天气很好"))
    with self.assertRaises(SimilarityError):
        cosine_similarity(freq_a, Counter())

def test_calculate_similarity_empty_text(self):
    """用例12: 清洗后为空的文本无法计算相似度。"""
    with self.assertRaises(SimilarityError):
        calculate_similarity("", "今天天气很好")
```

**场景说明**：
- 用例 10 直接测试 `cosine_similarity` 函数对空 Counter 的处理
- 用例 12 模拟了输入文件内容为空的场景

### 6.4 参数错误

**设计目标**：当命令行参数个数不为 3 时，打印用法提示并以退出码 1 终止。

**对应测试用例**（用例 14）：

```python
def test_main_wrong_argument_count(self):
    """用例14: 参数个数不足时退出码为 1 并提示用法。"""
    result = self._run(os.path.join(DATA_DIR, "orig_sample.txt"))
    self.assertEqual(result.returncode, 1)
    self.assertIn("用法", result.stderr)
```

**场景说明**：用户运行程序时少传了参数，程序应给出清晰的用法提示而非崩溃。

---

## 七、PSP 表格（实际耗时）

| Personal Software Process Stages | 预估耗时（分钟） | 实际耗时（分钟） |
| --- | --- | --- |
| **Planning 计划** | **20** | **15** |
| · Estimate · 估计这个任务需要多少时间 | 20 | 15 |
| **Development 开发** | **380** | **400** |
| · Analysis · 需求分析 (包括学习新技术) | 60 | 70 |
| · Design Spec · 生成设计文档 | 30 | 30 |
| · Design Review · 设计复审 | 20 | 15 |
| · Coding Standard · 代码规范 | 20 | 15 |
| · Design · 具体设计 | 40 | 45 |
| · Coding · 具体编码 | 120 | 130 |
| · Code Review · 代码复审 | 40 | 40 |
| · Test · 测试 | 50 | 55 |
| **Reporting 报告** | **80** | **75** |
| · Test Report · 测试报告 | 40 | 40 |
| · Size Measurement · 计算工作量 | 15 | 10 |
| · Postmortem · 事后总结 | 25 | 25 |
| **合计** | **480** | **490** |

### 事后总结与改进计划

1. **前期调研不足**：测试文本包含 HTML 格式，中途补充了 HTML 清洗逻辑。今后开工前应先检查所有输入样例的格式。
2. **测试数据同步准备**：单元测试数据在编码阶段同步准备，效率更高。
3. **性能方面**：jieba 首次加载词典约需 0.43 秒（占 74.9%），若对时效有更高要求，可考虑 n-gram 切分替代。

---

## 八、Git 提交记录

```
fc016ce docs: 添加PSP表格与README
6669730 test: 添加15个单元测试用例与样例验证脚本
5e77ed6 feat: 论文查重核心功能：文本清洗、分词与余弦相似度
```

按功能模块分阶段提交：
1. **feat**：核心功能（文本清洗、分词、余弦相似度、命令行入口）
2. **test**：单元测试与样例验证脚本
3. **docs**：PSP 表格与项目文档

---

## 九、使用说明

```bash
# 安装依赖
pip install -r requirements.txt

# 运行查重
python main.py [原文文件] [抄袭版论文文件] [答案文件]

# 示例
python main.py C:\tests\orig.txt C:\tests\orig_add.txt C:\tests\ans.txt

# 运行测试
python -m unittest discover -s tests -v
```
