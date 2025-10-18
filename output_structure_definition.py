#!/usr/bin/env python3
"""
输出结构定义和使用示例
重新组织的评估流程：数值计算 -> pruning -> voting -> 结果

输出结构说明：
1. 数值计算结果：包含64个traces的各种指标
2. Pruning结果：剪枝后的数据和统计信息
3. Voting结果：最终投票结果和准确率
"""

import json
import os
import sys
from typing import Dict, Any, List


class OutputStructureDefinition:
    """
    输出结构定义类
    
    定义了重新组织评估流程中各个阶段的输出结构
    """
    
    @staticmethod
    def get_numerical_output_structure() -> Dict[str, Any]:
        """
        获取数值计算阶段的输出结构
        
        Returns:
            数值计算输出结构示例
        """
        return {
            "id": "问题ID",
            "question": "问题内容",
            "output": [
                "trace_1_output", "trace_2_output", "trace_3_output", "trace_4_output", "trace_5_output", "trace_6_output", "trace_7_output", "trace_8_output", "trace_9_output", "trace_10_output", "trace_11_output", "trace_12_output", "trace_13_output", "trace_14_output", "trace_15_output", "trace_16_output", "trace_17_output", "trace_18_output", "trace_19_output", "trace_20_output", "trace_21_output", "trace_22_output", "trace_23_output", "trace_24_output", "trace_25_output", "trace_26_output", "trace_27_output", "trace_28_output", "trace_29_output", "trace_30_output", "trace_31_output", "trace_32_output", "trace_33_output", "trace_34_output", "trace_35_output", "trace_36_output", "trace_37_output", "trace_38_output", "trace_39_output", "trace_40_output", "trace_41_output", "trace_42_output", "trace_43_output", "trace_44_output", "trace_45_output", "trace_46_output", "trace_47_output", "trace_48_output", "trace_49_output", "trace_50_output", "trace_51_output", "trace_52_output", "trace_53_output", "trace_54_output", "trace_55_output", "trace_56_output", "trace_57_output", "trace_58_output", "trace_59_output", "trace_60_output", "trace_61_output", "trace_62_output", "trace_63_output", "trace_64_output"
            ],
            "confidence": [
                0.85, 0.72, 0.91, 0.68, 0.79, 0.83, 0.77, 0.81, 0.76, 0.84, 0.78, 0.82, 0.80, 0.79, 0.83, 0.80, 0.75, 0.88, 0.73, 0.86, 0.74, 0.87, 0.72, 0.89, 0.71, 0.90, 0.70, 0.91, 0.69, 0.92, 0.68, 0.93, 0.67, 0.94, 0.66, 0.95, 0.65, 0.96, 0.64, 0.97, 0.63, 0.98, 0.62, 0.99, 0.61, 1.00, 0.60, 0.99, 0.59, 0.98, 0.58, 0.97, 0.57, 0.96, 0.56, 0.95, 0.55, 0.94, 0.54, 0.93, 0.53, 0.92, 0.52, 0.91
            ],
            "self_certainty": [
                -0.5, -0.8, -0.3, -0.7, -0.4, -0.6, -0.2, -0.9, -0.1, -1.0, -0.0, -1.1, 0.1, -1.2, 0.2, -1.3, 0.3, -1.4, 0.4, -1.5, 0.5, -1.6, 0.6, -1.7, 0.7, -1.8, 0.8, -1.9, 0.9, -2.0, 1.0, -2.1, 1.1, -2.2, 1.2, -2.3, 1.3, -2.4, 1.4, -2.5, 1.5, -2.6, 1.6, -2.7, 1.7, -2.8, 1.8, -2.9, 1.9, -3.0, 2.0, -3.1, 2.1, -3.2, 2.2, -3.3, 2.3, -3.4, 2.4, -3.5, 2.5, -3.6, 2.6, -3.7
            ],
            "semantic_entropy": [
                0.3, 0.8, 0.2, 0.6, 0.4, 0.7, 0.1, 0.9, 0.5, 1.0, 0.0, 1.1, 0.6, 1.2, 0.7, 1.3, 0.8, 1.4, 0.9, 1.5, 1.0, 1.6, 1.1, 1.7, 1.2, 1.8, 1.3, 1.9, 1.4, 2.0, 1.5, 2.1, 1.6, 2.2, 1.7, 2.3, 1.8, 2.4, 1.9, 2.5, 2.0, 2.6, 2.1, 2.7, 2.2, 2.8, 2.3, 2.9, 2.4, 3.0, 2.5, 3.1, 2.6, 3.2, 2.7, 3.3, 2.8, 3.4, 2.9, 3.5, 3.0, 3.6, 3.1, 3.7
            ],
            "consistency": [
                0.9, 0.7, 0.95, 0.8, 0.85, 0.75, 0.92, 0.88, 0.82, 0.78, 0.94, 0.86, 0.80, 0.84, 0.76, 0.90, 0.88, 0.72, 0.96, 0.74, 0.98, 0.76, 0.92, 0.78, 0.94, 0.80, 0.96, 0.82, 0.98, 0.84, 0.90, 0.86, 0.92, 0.88, 0.94, 0.90, 0.96, 0.92, 0.98, 0.94, 0.90, 0.96, 0.92, 0.98, 0.94, 0.90, 0.96, 0.92, 0.98, 0.94, 0.90, 0.96, 0.92, 0.98, 0.94, 0.90, 0.96, 0.92, 0.98, 0.94, 0.90, 0.96, 0.92, 0.98
            ],
            "answer": [
                "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D", "A", "B", "C", "D"
            ],
            "correct_answer": "正确答案",
        }
    


def create_sample_data():
    """
    创建示例数据文件
    """
    sample_data = [
        {
            "id": "sample_001",
            "question": "What is the capital of France?",
            "choices": ["A) London", "B) Paris", "C) Berlin", "D) Madrid"],
            "correct_answer": "B",
            "output": [
                f"Trace {i+1}: The capital of France is Paris." for i in range(64)
            ],
            "generator": "sample_model",
            "dataset": "mmlu"
        },
        {
            "id": "sample_002", 
            "question": "What is 2 + 2?",
            "choices": ["A) 3", "B) 4", "C) 5", "D) 6"],
            "correct_answer": "B",
            "output": [
                f"Trace {i+1}: 2 + 2 = 4." for i in range(64)
            ],
            "generator": "sample_model",
            "dataset": "mmlu"
        }
    ]
    
    return sample_data


def main():
    """主函数 - 演示数值计算输出结构"""
    print("="*80)
    print("数值计算阶段输出结构")
    print("="*80)
    
    # 创建输出结构定义实例
    output_def = OutputStructureDefinition()
    
    print("\n数值计算阶段输出结构:")
    print("-" * 40)
    numerical_structure = output_def.get_numerical_output_structure()
    print(json.dumps(numerical_structure, indent=2, ensure_ascii=False))
    
    print("\n" + "="*80)
    print("字段说明:")
    print("="*80)
    print("• id: 问题ID")
    print("• question: 问题内容")
    print("• output: 64个traces的原始输出")
    print("• confidence: 64个traces的置信度分数")
    print("• self_certainty: 64个traces的自确定性分数")
    print("• semantic_entropy: 64个traces的语义熵分数")
    print("• consistency: 64个traces的一致性分数")
    print("• answer: 64个traces的大模型推理答案")
    print("• correct_answer: 题目的正确答案")
    print("="*80)
    
    # 创建示例数据文件
    sample_data = create_sample_data()
    sample_file = "sample_input_data.json"
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n示例数据文件已创建: {sample_file}")
    print("可以使用以下命令运行数值计算:")
    print(f"python numerical_calculator.py --input_file {sample_file}")


if __name__ == "__main__":
    main()
