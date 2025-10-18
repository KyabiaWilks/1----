# Experimental PKL/Logits Tools

实验性工具：从上游PKL文件提取logits和token_ids，用于加速tokenization和计算。

## 文件说明

- `numerical_calculator_with_pkl.py` - 支持PKL加速的numerical_calculator副本
- `test_pkl_loading.py` - 测试PKL文件加载和数据结构
- `test_pkl_with_numerical.sh` - 运行PKL加速版numerical_calculator的测试脚本

## 背景

上游提供了 `openPangu-Embedded-7B_n64-infer-results.pkl` 文件，包含：
- 每个trace的 `prompt_token_ids` (已tokenized)
- 生成token的logprobs (仅生成部分，不包含prompt的token-level logprobs)

## 功能

1. **加速tokenization**: 直接使用PKL中的token_ids，避免重复tokenization
2. **验证数据一致性**: 检查JSON和PKL数据的对应关系

## 使用方法

```bash
# 测试PKL加载
python test_pkl_loading.py

# 运行PKL加速版numerical_calculator
bash test_pkl_with_numerical.sh
```

## 限制

- PKL文件只包含1个问题的数据（mmlu-redux#0）
- PKL中没有prompt的token-level logprobs
- 如果需要计算perplexity/entropy，仍需加载模型进行前向传播
- PKL的prompt可能包含question前缀，与JSON的output text不完全相同

## 结论

PKL文件可用于加速tokenization，但对于完整的metrics计算（perplexity/entropy），收益有限。
主程序 `numerical_calculator.py` 已默认不加载模型，仅使用tokenizer，已经足够高效。

## 注意

这是实验性代码，不影响主程序运行。

