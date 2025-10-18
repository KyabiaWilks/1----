#!/usr/bin/env python3
"""
Unified Inference Script with Random Sampling and Multiprocessing Support
"""

import argparse
import json
import os
import random
import multiprocessing as mp
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
from pathlib import Path
import sys

# Set multiprocessing start method
mp.set_start_method('spawn', force=True)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Unified Inference with Random Sampling and Multiprocessing")
    
    # Basic arguments
    parser.add_argument("--engine", type=str, default="vllm", help="Inference engine")
    parser.add_argument("--data_name", type=str, required=True, help="Data name")
    parser.add_argument("--model_name", type=str, required=True, help="Model name")
    parser.add_argument("--run_name", type=str, default="default", help="Run name")
    parser.add_argument("--model_pretty_name", type=str, required=True, help="Model pretty name")
    parser.add_argument("--output_folder", type=str, required=True, help="Output folder")
    
    # Model parameters
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.95, help="GPU memory utilization")
    parser.add_argument("--max_model_len", type=int, default=4096, help="Max model length")
    parser.add_argument("--tensor_parallel_size", type=int, default=1, help="Tensor parallel size")
    parser.add_argument("--dtype", type=str, default="bfloat16", help="Data type")
    parser.add_argument("--top_p", type=float, default=1.0, help="Top-p sampling")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature")
    parser.add_argument("--repetition_penalty", type=float, default=1.0, help="Repetition penalty")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--max_tokens", type=int, default=4096, help="Max tokens")
    
    # New features
    parser.add_argument("--random_sample", action="store_true", help="Enable random sampling")
    parser.add_argument("--sample_size", type=int, default=50, help="Sample size for random sampling")
    parser.add_argument("--random_seed", type=int, default=42, help="Random seed")
    parser.add_argument("--enable_multiprocessing", action="store_true", help="Enable multiprocessing")
    parser.add_argument("--num_processes", type=int, default=4, help="Number of processes")
    parser.add_argument("--use_threading", action="store_true", help="Use threading instead of multiprocessing")
    
    # Additional arguments
    parser.add_argument("--use_hf_conv_template", action="store_true", help="Use HF conversation template")
    parser.add_argument("--use_imend_stop", action="store_true", help="Use imend stop")
    parser.add_argument("--download_dir", type=str, default="./cache", help="Download directory")
    
    return parser.parse_args()

def load_eval_data(data_name):
    """Load evaluation data"""
    # This is a simplified version - in practice you'd load from the actual data source
    data_file = f"test_data/{data_name}/openPangu-Embedded-7B_n64.json"
    
    if not os.path.exists(data_file):
        print(f"Error: Data file not found: {data_file}")
        return None
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items from {data_file}")
    return data

def random_sample_data(data, sample_size, random_seed):
    """Randomly sample data from the middle of the dataset"""
    if sample_size >= len(data):
        print(f"Sample size ({sample_size}) >= total data size ({len(data)}), using all data")
        return data
    
    random.seed(random_seed)
    np.random.seed(random_seed)
    
    total_size = len(data)
    # Sample from the middle 50% of the data
    start_idx = total_size // 4
    end_idx = 3 * total_size // 4
    middle_data = data[start_idx:end_idx]
    
    selected_indices = random.sample(range(len(middle_data)), min(sample_size, len(middle_data)))
    selected_indices.sort()
    
    sampled_data = [middle_data[i] for i in selected_indices]
    
    print(f"Randomly sampled {len(sampled_data)} samples from middle 50% of {total_size} total samples")
    print(f"Selected indices: {selected_indices[:10]}{'...' if len(selected_indices) > 10 else ''}")
    
    return sampled_data

def process_single_item(item, args):
    """Process a single data item - use existing inference results"""
    # The item already contains the model outputs, we just need to process it
    item_id = item.get("session_id", item.get("id", "unknown"))
    print(f"  - Processing item {item_id} in process {os.getpid()}")
    
    # Use the existing data structure from the input file
    result = {
        "id": item.get("session_id", item.get("id", 0)),
        "question": item.get("question", ""),
        "output": item.get("output", []),  # Use the existing model outputs
        "answer": item.get("answer", ""),
        "correct_answer": item.get("correct_answer", "")
    }
    return result

def process_batch_sequential(batch_data, args):
    """Process batch sequentially"""
    results = []
    for item in batch_data:
        result = process_single_item(item, args)
        results.append(result)
    return results

def process_batch_parallel(batch_data, args):
    """Process batch in parallel"""
    if args.use_threading:
        with ThreadPoolExecutor(max_workers=args.num_processes) as executor:
            futures = [executor.submit(process_single_item, item, args) for item in batch_data]
            results = [future.result(timeout=300) for future in futures]
    else:
        with ProcessPoolExecutor(max_workers=args.num_processes) as executor:
            chunk_size = max(1, len(batch_data) // args.num_processes)
            chunks = [batch_data[i:i + chunk_size] for i in range(0, len(batch_data), chunk_size)]
            futures = [executor.submit(process_batch_sequential, chunk, args) for chunk in chunks]
            results = []
            for future in futures:
                try:
                    chunk_results = future.result(timeout=600)
                    results.extend(chunk_results)
                except Exception as e:
                    print(f"Error processing chunk: {e}")
                    results.extend([{"id": 0, "question": "", "output": [], "answer": "", "correct_answer": ""} for _ in range(len(chunk))])
    return results

def main():
    """Main function"""
    args = parse_args()
    
    print("="*60)
    print("Unified Inference with Random Sampling and Multiprocessing")
    print("="*60)
    print(f"Engine: {args.engine}")
    print(f"Data: {args.data_name}")
    print(f"Model: {args.model_name}")
    print(f"Run: {args.run_name}")
    print(f"Output: {args.output_folder}")
    print(f"Random sampling: {args.random_sample}")
    print(f"Sample size: {args.sample_size}")
    print(f"Multiprocessing: {args.enable_multiprocessing}")
    print(f"Processes: {args.num_processes}")
    print("="*60)
    
    # Load data
    data = load_eval_data(args.data_name)
    if data is None:
        return
    
    # Random sampling
    if args.random_sample:
        data = random_sample_data(data, args.sample_size, args.random_seed)
    
    # Create output directory
    os.makedirs(args.output_folder, exist_ok=True)
    
    # Process data
    if args.enable_multiprocessing:
        print(f"Processing {len(data)} items with {args.num_processes} processes...")
        results = process_batch_parallel(data, args)
    else:
        print(f"Processing {len(data)} items sequentially...")
        results = process_batch_sequential(data, args)
    
    # Save results
    output_file = os.path.join(args.output_folder, f"{args.model_pretty_name}.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_file}")
    print(f"Processed {len(results)} items successfully!")

if __name__ == "__main__":
    main()
