# Dataset Filtering Tools

数据集筛选工具，用于削减简单问题，保留难题进行评估。

## 文件说明

- `filter_easy_questions.py` - 第一版筛选脚本
- `filter_easy_questions_v2.py` - 改进版筛选脚本
- `run_filter.sh` - 快速运行筛选的shell脚本
- `test_filter.py` - 测试脚本

## 使用方法

### 快速开始

```bash
# 使用shell脚本运行
bash run_filter.sh

# 或直接运行Python脚本
python filter_easy_questions_v2.py \
    --input_file test_data/mmlu-redux/openPangu-Embedded-7B_n64.json \
    --output_file test_data/mmlu-redux/openPangu-Embedded-7B_n64_hard.json \
    --threshold 0.8
```

## 筛选策略

筛选掉以下简单问题：
- 所有trace都回答正确的问题
- 大部分trace回答一致且正确的问题
- 根据设定的阈值自动筛选

## 输出

生成新的JSON文件，只包含筛选后的难题。

## 注意事项

- 筛选前请备份原始数据
- 建议先在小数据集上测试阈值设置
- v2版本包含更多筛选策略和统计信息

