#!/bin/bash
# 便捷脚本 - 运行问题筛选程序

# 默认参数
NUMERICAL_RESULTS="test_data/mmlu-redux/openPangu-Embedded-7B_n64_numerical_results.json"
ORIGINAL_DATA="test_data/mmlu-redux/openPangu-Embedded-7B_n64.json"
OUTPUT=""
THRESHOLD=0.8
KEEP_RATIO=0.1
RANDOM_SEED=42

# 显示帮助信息
show_help() {
    cat << EOF
使用方法: $0 [选项]

问题筛选程序 - 筛选并删除简单题目

选项:
    -n, --numerical FILE    数值计算结果文件路径
                           （默认: $NUMERICAL_RESULTS）
    
    -o, --original FILE     原始数据集文件路径
                           （默认: $ORIGINAL_DATA）
    
    -t, --threshold VALUE   同选项比例阈值（0-1）
                           （默认: $THRESHOLD，即80%）
    
    -k, --keep VALUE        简单题保留比例（0-1）
                           （默认: $KEEP_RATIO，即10%）
    
    -s, --seed VALUE        随机种子
                           （默认: $RANDOM_SEED）
    
    --output FILE          输出文件路径
                           （默认: 原始文件名_filtered.json）
    
    -h, --help             显示此帮助信息

示例:
    # 使用默认参数
    $0

    # 自定义阈值和保留比例
    $0 -t 0.75 -k 0.15

    # 指定输入输出文件
    $0 -n results.json -o data.json --output filtered.json

EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--numerical)
            NUMERICAL_RESULTS="$2"
            shift 2
            ;;
        -o|--original)
            ORIGINAL_DATA="$2"
            shift 2
            ;;
        -t|--threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        -k|--keep)
            KEEP_RATIO="$2"
            shift 2
            ;;
        -s|--seed)
            RANDOM_SEED="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "错误: 未知选项 $1"
            echo "使用 -h 或 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 检查文件是否存在
if [ ! -f "$NUMERICAL_RESULTS" ]; then
    echo "❌ 错误: 数值计算结果文件不存在: $NUMERICAL_RESULTS"
    exit 1
fi

if [ ! -f "$ORIGINAL_DATA" ]; then
    echo "❌ 错误: 原始数据集文件不存在: $ORIGINAL_DATA"
    exit 1
fi

# 构建命令
CMD="python filter_easy_questions.py"
CMD="$CMD --numerical_results \"$NUMERICAL_RESULTS\""
CMD="$CMD --original_data \"$ORIGINAL_DATA\""
CMD="$CMD --threshold $THRESHOLD"
CMD="$CMD --keep_ratio $KEEP_RATIO"
CMD="$CMD --random_seed $RANDOM_SEED"

if [ -n "$OUTPUT" ]; then
    CMD="$CMD --output \"$OUTPUT\""
fi

# 显示将要执行的命令
echo "=================================="
echo "将执行以下命令:"
echo "$CMD"
echo "=================================="
echo ""

# 询问确认
read -p "是否继续? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 执行命令
eval $CMD

# 检查执行结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 筛选完成!"
else
    echo ""
    echo "❌ 筛选失败!"
    exit 1
fi

