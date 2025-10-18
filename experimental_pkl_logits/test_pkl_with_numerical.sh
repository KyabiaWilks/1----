#!/bin/bash
# 测试使用PKL文件加速的numerical_calculator

echo "========================================"
echo "测试PKL加速的numerical_calculator"
echo "========================================"

# 测试参数
INPUT_FILE="test_data/mmlu-redux/openPangu-Embedded-7B_n64.json"
PKL_FILE="test_data/mmlu-redux/openPangu-Embedded-7B_n64-infer-results.pkl"
OUTPUT_FILE="test_data/mmlu-redux/openPangu-Embedded-7B_n64_with_pkl_results.json"
MAX_ITEMS=1  # 只测试第一个问题（因为PKL只有1个问题的数据）

echo ""
echo "参数："
echo "  输入文件: $INPUT_FILE"
echo "  PKL文件: $PKL_FILE"
echo "  输出文件: $OUTPUT_FILE"
echo "  处理数量: $MAX_ITEMS"
echo ""

python3 numerical_calculator_with_pkl.py \
    --input_file "$INPUT_FILE" \
    --pkl_file "$PKL_FILE" \
    --output_file "$OUTPUT_FILE" \
    --max_items $MAX_ITEMS \
    --run_prunning_voting \
    --k 10 \
    --first_stage_token_limit 10 \
    --save_interval 1 \
    --voting_power 0.5 \
    --voting_metric confidence \
    --keyword_weight_multiplier 10.0 \
    --keyword_window_size 50

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"

