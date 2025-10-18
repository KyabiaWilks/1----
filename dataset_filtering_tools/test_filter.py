#!/usr/bin/env python3
"""
测试脚本 - 生成测试数据并运行筛选程序
"""

import json
import os
import sys
import tempfile
from filter_easy_questions import QuestionFilter


def generate_test_data(num_questions=100, num_traces=64):
    """生成测试数据"""
    import random
    random.seed(42)
    
    # 生成numerical_results数据
    numerical_data = []
    original_data = []
    
    for i in range(num_questions):
        question_id = f"question_{i+1}"
        correct_answer = random.choice(["A", "B", "C", "D"])
        
        # 生成不同难度的题目
        if i < 20:  # 前20个是简单题（90%正确）
            answers = [correct_answer] * 58 + [random.choice(["A", "B", "C", "D"]) for _ in range(6)]
            is_correct = True
        elif i < 40:  # 接下来20个是中等题（70%正确）
            answers = [correct_answer] * 45 + [random.choice(["A", "B", "C", "D"]) for _ in range(19)]
            is_correct = random.random() > 0.3
        else:  # 其余是难题（随机）
            answers = [random.choice(["A", "B", "C", "D"]) for _ in range(num_traces)]
            is_correct = random.random() > 0.5
        
        # numerical_results条目
        numerical_item = {
            "id": question_id,
            "question": f"This is test question {i+1}",
            "answer": answers,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "confidence": [random.random() for _ in range(len(answers))],
            "output": [f"Output trace {j+1}" for j in range(len(answers))]
        }
        numerical_data.append(numerical_item)
        
        # original_data条目
        original_item = {
            "id": question_id,
            "question": f"This is test question {i+1}",
            "output": [f"Output trace {j+1}" for j in range(num_traces)],
            "dataset": "test",
            "generator": "test_model"
        }
        original_data.append(original_item)
    
    return numerical_data, original_data


def test_filter():
    """测试筛选功能"""
    print("=" * 80)
    print("筛选程序测试")
    print("=" * 80)
    
    # 1. 生成测试数据
    print("\n📝 生成测试数据...")
    numerical_data, original_data = generate_test_data(num_questions=100, num_traces=64)
    print(f"  - 生成了 {len(numerical_data)} 个题目")
    
    # 2. 创建临时文件
    with tempfile.TemporaryDirectory() as tmpdir:
        numerical_file = os.path.join(tmpdir, "numerical_results.json")
        original_file = os.path.join(tmpdir, "original_data.json")
        output_file = os.path.join(tmpdir, "filtered_data.json")
        
        # 保存测试数据
        print("\n💾 保存测试数据...")
        with open(numerical_file, 'w', encoding='utf-8') as f:
            json.dump(numerical_data, f, indent=2)
        with open(original_file, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, indent=2)
        print(f"  - numerical_results: {numerical_file}")
        print(f"  - original_data: {original_file}")
        
        # 3. 运行筛选
        print("\n🔧 运行筛选程序...")
        filter_obj = QuestionFilter(threshold=0.8, keep_ratio=0.1, random_seed=42)
        
        try:
            report = filter_obj.filter_questions(
                numerical_results_file=numerical_file,
                original_data_file=original_file,
                output_file=output_file
            )
            
            # 4. 验证结果
            print("\n✅ 验证结果...")
            
            # 读取筛选后的数据
            with open(output_file, 'r', encoding='utf-8') as f:
                filtered_data = json.load(f)
            
            print(f"  - 原始数据: {len(original_data)} 个题目")
            print(f"  - 筛选后数据: {len(filtered_data)} 个题目")
            print(f"  - 删除了: {len(original_data) - len(filtered_data)} 个题目")
            
            # 检查报告
            assert report['summary']['original_count'] == len(original_data)
            assert report['summary']['filtered_count'] == len(filtered_data)
            assert report['summary']['removed_count'] == len(original_data) - len(filtered_data)
            
            print("\n✅ 测试通过!")
            print("\n📊 详细统计:")
            print(f"  - 发现简单题目: {report['summary']['easy_questions_found']}")
            print(f"  - 保留简单题目: {report['summary']['easy_questions_kept']}")
            print(f"  - 删除简单题目: {report['summary']['easy_questions_removed']}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_with_real_data():
    """使用真实数据测试（如果存在）"""
    print("\n" + "=" * 80)
    print("真实数据测试")
    print("=" * 80)
    
    numerical_file = "test_data/mmlu-redux/openPangu-Embedded-7B_n64_numerical_results.json"
    original_file = "test_data/mmlu-redux/openPangu-Embedded-7B_n64.json"
    
    if not os.path.exists(numerical_file) or not os.path.exists(original_file):
        print("\n⚠️  真实数据文件不存在，跳过此测试")
        print(f"  需要的文件:")
        print(f"  - {numerical_file}")
        print(f"  - {original_file}")
        return None
    
    print(f"\n📖 找到真实数据文件:")
    print(f"  - {numerical_file}")
    print(f"  - {original_file}")
    
    # 询问是否继续
    print("\n⚠️  注意：此操作将处理真实数据文件，可能需要较长时间")
    response = input("是否继续？(y/n): ")
    
    if response.lower() != 'y':
        print("已取消")
        return None
    
    # 运行筛选
    filter_obj = QuestionFilter(threshold=0.8, keep_ratio=0.1, random_seed=42)
    
    output_file = original_file.replace(".json", "_filtered.json")
    
    try:
        report = filter_obj.filter_questions(
            numerical_results_file=numerical_file,
            original_data_file=original_file,
            output_file=output_file
        )
        print("\n✅ 真实数据测试成功!")
        return True
    except Exception as e:
        print(f"\n❌ 真实数据测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("筛选程序测试套件\n")
    
    # 测试1: 使用模拟数据
    print("测试1: 模拟数据测试")
    test1_passed = test_filter()
    
    # 测试2: 使用真实数据（可选）
    if len(sys.argv) > 1 and sys.argv[1] == "--real-data":
        print("\n" + "=" * 80)
        print("测试2: 真实数据测试")
        test2_passed = test_with_real_data()
    else:
        print("\n" + "=" * 80)
        print("提示：使用 --real-data 参数测试真实数据")
        test2_passed = None
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"模拟数据测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    if test2_passed is not None:
        print(f"真实数据测试: {'✅ 通过' if test2_passed else '❌ 失败'}")
    print("=" * 80)
    
    return 0 if test1_passed else 1


if __name__ == "__main__":
    exit(main())

