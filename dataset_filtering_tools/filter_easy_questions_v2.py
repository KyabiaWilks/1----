#!/usr/bin/env python3
"""
问题筛选程序 V2 - 改进版
主要改进：
1. 放宽筛选条件：只要答案一致性高且is_correct=True，就认为是简单题
2. 不再强制要求"最常见答案必须与正确答案格式完全匹配"
3. 更符合实际使用场景
4. 使用统一的答案检查函数（与voting.py保持一致）
"""

import json
import os
import argparse
from typing import List, Dict, Any, Tuple, Union
from collections import Counter
import random

# 导入统一的答案检查函数
try:
    from voting import check_answer_equality
except ImportError:
    # 如果无法导入，定义本地版本
    def check_answer_equality(pred: str, correct: Union[str, int]) -> bool:
        """检查预测答案和正确答案是否等价"""
        if not pred or correct is None:
            return False
        
        # 将correct_answer转换为整数（如果是字符串形式的数字）
        if isinstance(correct, str) and correct.isdigit():
            correct = int(correct)
        
        # 如果correct_answer是数字，将字母转换为对应数字
        if isinstance(correct, int):
            if pred in 'ABCD':
                return ord(pred) - ord('A') == correct
            return False
        
        # 如果correct_answer是字母，直接比较
        return pred == correct


class QuestionFilterV2:
    """问题筛选器 V2 - 改进版"""
    
    def __init__(self, 
                 threshold: float = 0.8,
                 keep_ratio: float = 0.1,
                 random_seed: int = 42,
                 strict_mode: bool = False):
        """
        初始化筛选器
        
        Args:
            threshold: 同选项比例阈值（默认0.8，即80%）
            keep_ratio: 简单题目保留比例（默认0.1，即10%）
            random_seed: 随机种子
            strict_mode: 是否使用严格模式（需要答案格式匹配，默认False）
        """
        self.threshold = threshold
        self.keep_ratio = keep_ratio
        self.strict_mode = strict_mode
        random.seed(random_seed)
    
    def analyze_question(self, item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        分析单个题目是否为简单题目
        
        V2改进：
        - 默认模式（strict_mode=False）：只要一致性高且is_correct，就是简单题
        - 严格模式（strict_mode=True）：还需要答案格式匹配
        
        Args:
            item: 题目数据项
            
        Returns:
            (是否为简单题目, 统计信息)
        """
        answers = item.get("answer", [])
        correct_answer = item.get("correct_answer", "")
        is_correct = item.get("is_correct", False)
        
        if not answers:
            return False, {}
        
        # 统计答案分布
        answer_counts = Counter(answers)
        total_answers = len(answers)
        
        if total_answers == 0:
            return False, {}
        
        # 找出最常见的答案
        most_common_answer, most_common_count = answer_counts.most_common(1)[0]
        most_common_ratio = most_common_count / total_answers
        
        # V2改进：两种判断模式
        # 使用统一的答案检查函数
        answer_matches = check_answer_equality(str(most_common_answer), correct_answer)
        
        if self.strict_mode:
            # 严格模式：三个条件都要满足（V1逻辑）
            is_easy = (
                most_common_ratio >= self.threshold and 
                answer_matches and
                is_correct
            )
        else:
            # 默认模式：只要一致性高且is_correct（V2改进）
            is_easy = (
                most_common_ratio >= self.threshold and
                is_correct
            )
        
        stats = {
            "total_answers": total_answers,
            "most_common_answer": most_common_answer,
            "most_common_count": most_common_count,
            "most_common_ratio": most_common_ratio,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "answer_matches": answer_matches,
            "answer_distribution": dict(answer_counts)
        }
        
        return is_easy, stats
    
    def filter_questions(self, 
                        numerical_results_file: str,
                        original_data_file: str,
                        output_file: str = None) -> Dict[str, Any]:
        """
        筛选并删除简单题目
        
        Args:
            numerical_results_file: 数值计算结果文件路径
            original_data_file: 原始数据集文件路径
            output_file: 输出文件路径（可选）
            
        Returns:
            筛选统计信息
        """
        mode_str = "严格模式" if self.strict_mode else "标准模式"
        print(f"\n{'='*80}")
        print(f"开始筛选简单题目... ({mode_str})")
        print(f"{'='*80}\n")
        
        # 1. 读取numerical_results文件
        print(f"📖 读取数值计算结果: {numerical_results_file}")
        with open(numerical_results_file, 'r', encoding='utf-8') as f:
            numerical_data = json.load(f)
        print(f"  - 共加载 {len(numerical_data)} 个题目")
        
        # 2. 分析每个题目，找出简单题目
        print(f"\n🔍 分析题目难度...")
        print(f"  - 筛选模式: {mode_str}")
        print(f"  - 一致性阈值: {self.threshold*100}%")
        if not self.strict_mode:
            print(f"  - 条件: 答案一致性≥{self.threshold*100}% 且 is_correct=True")
        else:
            print(f"  - 条件: 答案一致性≥{self.threshold*100}% 且 答案匹配 且 is_correct=True")
        
        easy_question_ids = []
        question_stats = []
        
        for item in numerical_data:
            question_id = item.get("id")
            is_easy, stats = self.analyze_question(item)
            
            stats["id"] = question_id
            stats["is_easy"] = is_easy
            question_stats.append(stats)
            
            if is_easy:
                easy_question_ids.append(question_id)
        
        print(f"  ✅ 发现 {len(easy_question_ids)} 个简单题目 ({len(easy_question_ids)/len(numerical_data)*100:.1f}%)")
        
        # 3. 决定保留哪些简单题目
        num_to_keep = max(1, int(len(easy_question_ids) * self.keep_ratio))
        kept_easy_ids = random.sample(easy_question_ids, num_to_keep) if easy_question_ids else []
        ids_to_remove = set(easy_question_ids) - set(kept_easy_ids)
        
        print(f"  - 保留 {len(kept_easy_ids)} 个简单题目 ({self.keep_ratio*100}%)")
        print(f"  - 将删除 {len(ids_to_remove)} 个简单题目")
        
        # 4. 读取原始数据集
        print(f"\n📖 读取原始数据集: {original_data_file}")
        with open(original_data_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        print(f"  - 原始数据集共有 {len(original_data)} 个题目")
        
        # 5. 从原始数据集中删除简单题目
        print(f"\n🗑️  删除简单题目...")
        
        # 构建ID映射（处理不同的ID字段名和格式）
        def get_item_id(item):
            """获取题目ID，支持多种ID字段名"""
            return item.get("id") or item.get("session_id") or item.get("question_id")
        
        def normalize_id(item_id):
            """
            标准化ID格式
            - 如果是 "mmlu-redux#123" 格式，提取数字部分
            - 如果是纯数字字符串，转换为整数
            - 如果是整数，直接返回
            """
            if item_id is None:
                return None
            
            # 如果是字符串，尝试提取数字
            if isinstance(item_id, str):
                # 处理 "mmlu-redux#123" 格式
                if '#' in item_id:
                    try:
                        return int(item_id.split('#')[-1])
                    except ValueError:
                        pass
                # 处理纯数字字符串
                try:
                    return int(item_id)
                except ValueError:
                    pass
            
            # 如果已经是整数，直接返回
            if isinstance(item_id, int):
                return item_id
            
            # 其他情况返回原值
            return item_id
        
        # 标准化要删除的ID列表
        normalized_ids_to_remove = set(normalize_id(id_val) for id_val in ids_to_remove)
        
        filtered_data = []
        removed_count = 0
        
        for item in original_data:
            item_id = get_item_id(item)
            normalized_id = normalize_id(item_id)
            
            if normalized_id not in normalized_ids_to_remove:
                filtered_data.append(item)
            else:
                removed_count += 1
        
        print(f"  - 成功删除 {removed_count} 个题目")
        print(f"  - 剩余 {len(filtered_data)} 个题目 ({len(filtered_data)/len(original_data)*100:.1f}%)")
        
        # 6. 保存筛选后的数据集
        if output_file is None:
            base_name = os.path.splitext(original_data_file)[0]
            suffix = "_strict" if self.strict_mode else "_v2"
            output_file = f"{base_name}_filtered{suffix}.json"
        
        print(f"\n💾 保存筛选后的数据集: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        print(f"  ✅ 保存成功!")
        
        # 7. 生成筛选报告
        report_file = output_file.replace(".json", "_report.json")
        report = {
            "version": "v2",
            "mode": "strict" if self.strict_mode else "relaxed",
            "summary": {
                "original_count": len(original_data),
                "filtered_count": len(filtered_data),
                "removed_count": removed_count,
                "easy_questions_found": len(easy_question_ids),
                "easy_questions_kept": len(kept_easy_ids),
                "easy_questions_removed": len(ids_to_remove),
                "threshold": self.threshold,
                "keep_ratio": self.keep_ratio
            },
            "easy_questions": {
                "kept_ids": kept_easy_ids,
                "removed_ids": list(ids_to_remove)
            },
            "question_stats": question_stats
        }
        
        print(f"\n📊 保存筛选报告: {report_file}")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 8. 打印详细统计
        print(f"\n{'='*80}")
        print(f"筛选完成!")
        print(f"{'='*80}")
        print(f"\n📈 统计信息:")
        print(f"  原始题目数: {len(original_data)}")
        print(f"  筛选后题目数: {len(filtered_data)}")
        print(f"  删除题目数: {removed_count} ({removed_count/len(original_data)*100:.1f}%)")
        print(f"\n  发现简单题目: {len(easy_question_ids)} ({len(easy_question_ids)/len(original_data)*100:.1f}%)")
        print(f"  保留简单题目: {len(kept_easy_ids)}")
        print(f"  删除简单题目: {len(ids_to_remove)}")
        print(f"\n⚙️  筛选配置:")
        print(f"  模式: {mode_str}")
        print(f"  同选项阈值: {self.threshold*100}%")
        print(f"  简单题保留比例: {self.keep_ratio*100}%")
        if not self.strict_mode:
            print(f"  注: V2版本不要求答案格式匹配，只要一致性高且is_correct即可")
        print(f"\n📁 输出文件:")
        print(f"  筛选后数据集: {output_file}")
        print(f"  筛选报告: {report_file}")
        print(f"{'='*80}\n")
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="问题筛选程序 V2 - 改进版（放宽筛选条件）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
改进说明：
  V2版本默认使用放宽的筛选条件：
  - 只要答案一致性≥阈值 且 is_correct=True，就认为是简单题
  - 不再强制要求"最常见答案与正确答案格式完全匹配"
  - 如需使用V1的严格模式，请添加 --strict 参数

示例用法:
  # 使用V2默认模式（推荐）
  python filter_easy_questions_v2.py \\
    --numerical_results test_data/mmlu-redux/openPangu-Embedded-7B_n64_numerical_results.json \\
    --original_data test_data/mmlu-redux/openPangu-Embedded-7B_n64.json
  
  # 使用严格模式（V1逻辑）
  python filter_easy_questions_v2.py \\
    --numerical_results results.json \\
    --original_data data.json \\
    --strict
        """
    )
    
    parser.add_argument(
        "--numerical_results",
        type=str,
        required=True,
        help="数值计算结果文件路径"
    )
    
    parser.add_argument(
        "--original_data",
        type=str,
        required=True,
        help="原始数据集文件路径"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出文件路径（默认：原始文件名_filtered_v2.json）"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="同选项比例阈值（默认：0.8，即80%%）"
    )
    
    parser.add_argument(
        "--keep_ratio",
        type=float,
        default=0.1,
        help="简单题目保留比例（默认：0.1，即10%%）"
    )
    
    parser.add_argument(
        "--random_seed",
        type=int,
        default=42,
        help="随机种子（默认：42）"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="使用严格模式（V1逻辑：需要答案格式匹配）"
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not os.path.exists(args.numerical_results):
        print(f"❌ 错误: 数值计算结果文件不存在: {args.numerical_results}")
        return 1
    
    if not os.path.exists(args.original_data):
        print(f"❌ 错误: 原始数据集文件不存在: {args.original_data}")
        return 1
    
    # 验证参数范围
    if not 0 < args.threshold <= 1:
        print(f"❌ 错误: threshold必须在(0, 1]范围内，当前值: {args.threshold}")
        return 1
    
    if not 0 <= args.keep_ratio <= 1:
        print(f"❌ 错误: keep_ratio必须在[0, 1]范围内，当前值: {args.keep_ratio}")
        return 1
    
    # 创建筛选器并执行筛选
    filter_obj = QuestionFilterV2(
        threshold=args.threshold,
        keep_ratio=args.keep_ratio,
        random_seed=args.random_seed,
        strict_mode=args.strict
    )
    
    try:
        report = filter_obj.filter_questions(
            numerical_results_file=args.numerical_results,
            original_data_file=args.original_data,
            output_file=args.output
        )
        return 0
    except Exception as e:
        print(f"\n❌ 筛选过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

