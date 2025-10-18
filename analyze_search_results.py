#!/usr/bin/env python3
"""
参数搜索结果分析脚本
分析 parameter_search_results.json 并生成可视化报告
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

RESULTS_FILE = "parameter_search_results.json"


def load_results(results_file: str) -> List[Dict[str, Any]]:
    """加载结果文件"""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return results
    except FileNotFoundError:
        print(f"错误: 结果文件不存在: {results_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: 结果文件格式错误: {results_file}")
        sys.exit(1)


def analyze_results(results: List[Dict[str, Any]]):
    """分析结果"""
    print("="*80)
    print("参数搜索结果分析")
    print("="*80)
    
    # 基本统计
    total = len(results)
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') != 'success']
    
    print(f"\n基本统计:")
    print(f"  总实验数: {total}")
    print(f"  成功: {len(successful)} ({len(successful)/total*100:.1f}%)")
    print(f"  失败: {len(failed)} ({len(failed)/total*100:.1f}%)")
    
    if not successful:
        print("\n无成功的实验结果")
        return
    
    # 转换为DataFrame便于分析
    df = pd.DataFrame([
        {
            'exp_id': r['exp_id'],
            'accuracy': r.get('accuracy', 0),
            'total_tokens': r.get('total_tokens', 0),
            'total_questions': r.get('total_questions', 0),
            'duration': r.get('duration', 0),
            'voting_power': r['config']['voting_power'],
            'N': r['config']['first_stage_token_limit'],
            'M': r['config']['k'],
            'K': r['config']['keyword_weight_multiplier'],
            'size': r['config']['keyword_window_size'],
        }
        for r in successful
    ])
    
    # 准确率统计
    print(f"\n准确率统计:")
    print(f"  平均: {df['accuracy'].mean():.4f} ({df['accuracy'].mean()*100:.2f}%)")
    print(f"  最大: {df['accuracy'].max():.4f} ({df['accuracy'].max()*100:.2f}%)")
    print(f"  最小: {df['accuracy'].min():.4f} ({df['accuracy'].min()*100:.2f}%)")
    print(f"  标准差: {df['accuracy'].std():.4f}")
    
    # Token统计
    print(f"\nToken使用统计:")
    print(f"  平均: {df['total_tokens'].mean():.0f}")
    print(f"  最大: {df['total_tokens'].max():.0f}")
    print(f"  最小: {df['total_tokens'].min():.0f}")
    
    # 耗时统计
    print(f"\n耗时统计:")
    print(f"  平均: {df['duration'].mean()/60:.1f} 分钟")
    print(f"  最大: {df['duration'].max()/60:.1f} 分钟")
    print(f"  最小: {df['duration'].min()/60:.1f} 分钟")
    
    # Top 10 准确率最高
    print(f"\n准确率最高的10个配置:")
    print("-"*80)
    top10_acc = df.nlargest(10, 'accuracy')
    for idx, row in top10_acc.iterrows():
        print(f"实验{row['exp_id']:4d}: 准确率={row['accuracy']:.4f} | "
              f"Token={row['total_tokens']:7.0f} | "
              f"vp={row['voting_power']:.1f} N={row['N']:3.0f} M={row['M']:2.0f} "
              f"K={row['K']:4.1f} size={row['size']:3.0f}")
    
    # Top 10 Token最少
    print(f"\nToken最少的10个配置:")
    print("-"*80)
    top10_token = df.nsmallest(10, 'total_tokens')
    for idx, row in top10_token.iterrows():
        print(f"实验{row['exp_id']:4d}: Token={row['total_tokens']:7.0f} | "
              f"准确率={row['accuracy']:.4f} | "
              f"vp={row['voting_power']:.1f} N={row['N']:3.0f} M={row['M']:2.0f} "
              f"K={row['K']:4.1f} size={row['size']:3.0f}")
    
    # 效率（准确率/Token）最高
    df['efficiency'] = df['accuracy'] / (df['total_tokens'] / 1000)  # 每1000 token的准确率
    print(f"\n效率最高的10个配置 (准确率/1K-tokens):")
    print("-"*80)
    top10_eff = df.nlargest(10, 'efficiency')
    for idx, row in top10_eff.iterrows():
        print(f"实验{row['exp_id']:4d}: 效率={row['efficiency']:.6f} | "
              f"准确率={row['accuracy']:.4f} Token={row['total_tokens']:7.0f} | "
              f"vp={row['voting_power']:.1f} N={row['N']:3.0f} M={row['M']:2.0f} "
              f"K={row['K']:4.1f} size={row['size']:3.0f}")
    
    # 各参数的影响分析
    print(f"\n各参数对准确率的影响 (平均值):")
    print("-"*80)
    for param in ['voting_power', 'N', 'M', 'K', 'size']:
        print(f"\n{param}:")
        grouped = df.groupby(param)['accuracy'].agg(['mean', 'std', 'count'])
        for val, row in grouped.iterrows():
            print(f"  {val:6}: 平均={row['mean']:.4f} 标准差={row['std']:.4f} 样本数={row['count']:.0f}")
    
    # 生成CSV报告
    csv_file = "parameter_search_analysis.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n详细结果已保存到: {csv_file}")
    
    # 最佳配置
    best_idx = df['accuracy'].idxmax()
    best = df.loc[best_idx]
    print(f"\n最佳配置 (准确率最高):")
    print(f"  实验ID: {best['exp_id']:.0f}")
    print(f"  准确率: {best['accuracy']:.4f} ({best['accuracy']*100:.2f}%)")
    print(f"  Token: {best['total_tokens']:.0f}")
    print(f"  参数:")
    print(f"    voting_power: {best['voting_power']}")
    print(f"    first_stage_token_limit (N): {best['N']:.0f}")
    print(f"    k (M): {best['M']:.0f}")
    print(f"    keyword_weight_multiplier (K): {best['K']}")
    print(f"    keyword_window_size (size): {best['size']:.0f}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="参数搜索结果分析")
    parser.add_argument("--results_file", type=str, default=RESULTS_FILE, 
                       help="结果文件路径")
    
    args = parser.parse_args()
    
    results = load_results(args.results_file)
    analyze_results(results)


if __name__ == "__main__":
    main()

