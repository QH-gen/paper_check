# 论文查重（第一次个人编程作业）

学号：3124004165

给定一篇原文和一篇在其基础上经过增删改的抄袭版论文，计算并输出两份文本的重复率。

## 使用方法

```bash
pip install -r requirements.txt
python main.py [原文文件的绝对路径] [抄袭版论文文件的绝对路径] [答案文件的绝对路径]
```

示例：

```bash
python main.py C:\tests\orig.txt C:\tests\orig_add.txt C:\tests\ans.txt
```

答案文件输出浮点型重复率，精确到小数点后两位（如 `0.82`）。

## 项目结构

```
3124004165/
├── main.py              # 程序入口：解析命令行参数，串联完整流程
├── text_processor.py    # 文本预处理：文件读取、编码识别、HTML 清洗
├── similarity.py        # 相似度计算：分词、词频统计、余弦相似度
├── requirements.txt     # 第三方依赖（jieba）
├── PSP.md               # PSP 表格（预估/实际耗时）
└── tests/
    ├── test_paper_checker.py   # 单元测试（15 个测试用例）
    └── data/                   # 测试数据
```

## 算法说明

1. **文本预处理**：以二进制读入文件，依次尝试 UTF-8、GBK 解码；
   用正则去除 HTML 标签、`<script>/<style>` 块、HTML 实体与所有空白字符。
2. **分词**：使用 jieba 对清洗后的中文文本分词，过滤纯标点词元。
3. **词频向量**：统计每个词出现的频次，将文本映射为高维词频向量。
4. **余弦相似度**：计算两个词频向量的夹角余弦值

   `sim(A, B) = (A · B) / (|A| × |B|)`

   结果落在 [0, 1] 区间，即为重复率。

## 异常处理

| 异常 | 场景 | 处理方式 |
| --- | --- | --- |
| TextLoadError | 文件不存在 / 无权限 / 编码无法识别 | 输出错误信息，退出码 2 |
| SimilarityError | 文本清洗后为空，无法构建词频向量 | 输出错误信息，退出码 3 |
| 参数错误 | 命令行参数个数不为 3 | 输出用法提示，退出码 1 |

## 运行测试

```bash
python -m unittest discover -s tests -v
```
