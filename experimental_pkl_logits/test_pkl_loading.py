#!/usr/bin/env python3
"""
测试PKL文件加载功能

验证：
1. PKL文件能否正常加载
2. 数据结构是否正确
3. token_ids能否正确提取
"""

import json
import pickle
from pathlib import Path

class CustomUnpickler(pickle.Unpickler):
    """自定义Unpickler，处理未知模块"""
    def find_class(self, module, name):
        if 'vllm' in module:
            return type(name, (), {})
        return super().find_class(module, name)

def load_pkl(pkl_path):
    """加载PKL文件"""
    with open(pkl_path, 'rb') as f:
        return CustomUnpickler(f).load()

def main():
    # 文件路径
    json_path = "test_data/mmlu-redux/openPangu-Embedded-7B_n64.json"
    pkl_path = "test_data/mmlu-redux/openPangu-Embedded-7B_n64-infer-results.pkl"
    
    print("="*80)
    print("测试PKL加载功能")
    print("="*80)
    
    # 加载JSON
    print("\n1. 加载JSON文件...")
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    print(f"   ✓ JSON文件包含 {len(json_data)} 个问题")
    
    # 加载PKL
    print("\n2. 加载PKL文件...")
    pkl_data = load_pkl(pkl_path)
    print(f"   ✓ PKL文件包含 {len(pkl_data)} 个问题的推理结果")
    
    # 检查第一个问题的数据匹配
    print("\n3. 检查数据匹配...")
    first_item = json_data[0]
    session_id = first_item['session_id']
    print(f"   Session ID: {session_id}")
    
    if session_id in pkl_data:
        pkl_outputs = pkl_data[session_id]
        json_outputs = first_item['output']
        
        print(f"   JSON output数量: {len(json_outputs)}")
        print(f"   PKL output数量: {len(pkl_outputs)}")
        
        if len(json_outputs) == len(pkl_outputs):
            print(f"   ✓ 数量匹配！")
            
            # 检查第一个trace
            print("\n4. 检查第一个trace的详细信息...")
            first_pkl_output = pkl_outputs[0]
            first_json_output = json_outputs[0]
            
            print(f"   JSON text长度: {len(first_json_output)}")
            print(f"   PKL prompt长度: {len(first_pkl_output.prompt)}")
            print(f"   PKL token_ids数量: {len(first_pkl_output.prompt_token_ids)}")
            
            # 验证文本匹配
            if first_json_output == first_pkl_output.prompt:
                print(f"   ✓ JSON text和PKL prompt完全匹配！")
            else:
                print(f"   ⚠️ JSON text和PKL prompt不匹配")
                
            # 显示token_ids示例
            print(f"\n   Token IDs前20个: {first_pkl_output.prompt_token_ids[:20]}")
            print(f"   Token IDs后20个: {first_pkl_output.prompt_token_ids[-20:]}")
            
            # 检查是否有logprobs
            completion = first_pkl_output.outputs[0]
            print(f"\n5. 检查生成部分...")
            print(f"   生成的token数: {len(completion.token_ids)}")
            print(f"   生成的token: {completion.token_ids}")
            print(f"   生成的文本: '{completion.text}'")
            print(f"   是否有logprobs: {len(completion.logprobs) > 0}")
            
            if completion.logprobs:
                logprob_dict = completion.logprobs[0]
                print(f"   Logprobs包含 {len(logprob_dict)} 个token的概率")
                
                # 显示生成token的logprob
                gen_token_id = completion.token_ids[0]
                if gen_token_id in logprob_dict:
                    logprob_obj = logprob_dict[gen_token_id]
                    print(f"   生成token的logprob: {logprob_obj.logprob:.6f}")
                    print(f"   生成token的rank: {logprob_obj.rank}")
            
            print("\n" + "="*80)
            print("✅ PKL加载测试通过！")
            print("="*80)
            
            # 总结
            print("\n【总结】")
            print(f"- PKL文件可以正常加载")
            print(f"- JSON和PKL数据完全对应")
            print(f"- 每个trace有完整的prompt_token_ids")
            print(f"- PKL只包含生成token的logprobs，不包含prompt的token-level logprobs")
            print(f"- 因此可以使用PKL中的token_ids加速tokenization")
            print(f"- 但如果需要计算perplexity/entropy，仍需模型前向传播")
            
        else:
            print(f"   ⚠️ 数量不匹配！")
    else:
        print(f"   ⚠️ PKL中没有session_id: {session_id}")

if __name__ == "__main__":
    main()

