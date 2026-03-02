from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME,DATASET_NAME
import time
import json
from tqdm import tqdm
import random
import os
random.seed(44)
if DATASET_NAME=="FHM":
    data_src = 'data/FHM/data/dev_with_description.jsonl'
    img_src = 'data/FHM/data'
elif DATASET_NAME=="MAMI":
    data_src = 'data/MAMI/test_with_description.tsv'
    img_src = 'data/MAMI/img'
elif DATASET_NAME=="HARM":
    data_src = 'data/HARM/test_with_description.jsonl'
    img_src = 'data/HARM/images'
else:
    raise ValueError("Unsupported DATASET_NAME. Choose either 'FHM' or 'MAMI'.")
if DATASET_NAME == 'FHM':
    # 1. 初始化缓存路径与已处理 ID 集合
    cache_dir = DATASET_NAME
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_path = os.path.join(cache_dir, "result.json")
    processed_ids = set()
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            try:
                cache_data = json.load(f)
                processed_ids = set(cache_data.keys())
            except json.JSONDecodeError:
                print("⚠️ 缓存文件格式错误，将重新开始")
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in tqdm(enumerate(lines), total=len(lines), desc="Processing FHM"):
        # 3. 解析当前行
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        meme_text = sample.get('text', "")
        meme_src = f"{img_src}/{sample['img']}"
        meme_id = meme_src.split('/')[-1].split('.')[0]
        if meme_id in processed_ids:
            continue
        meme_content = sample.get('description', "")
        ground_truth = sample.get('label')  # FHM 标签通常已经是 0/1
        if not os.path.isfile(meme_src):
            print(f"⚠️ 图片文件不存在: {meme_src}")
            continue
        # 6. 初始化并运行辩论系统
        print(f"\n\n=== 处理 FHM 样本 {meme_id} ({idx + 1}/{len(lines)}) ===")
        debate_graph = DebateGraph(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE
        )
        
        start_time = time.time()
        try:
            final_state = debate_graph.run_debate(
                meme_text=meme_text,
                meme_src=meme_src,
                news_path='sample_news.txt',
                meme_content=meme_content,
                ground_truth=ground_truth
            )
            total_time = time.time() - start_time
            print(f"⏱️ 总执行时间: {total_time:.2f} 秒")
        except Exception as e:
            print(f"❌ 执行样本 {meme_id} 时出错: {e}")
            # traceback.print_exc() # 需要调试时取消注释
            continue
elif DATASET_NAME == 'MAMI':
    import pandas as pd
    data = pd.read_csv(data_src, sep='\t')
    img_src = 'data/MAMI/test_images'
    for idx, row in tqdm(data.iterrows(), total=len(data)):
        meme_text = row['text']
        meme_src = f"{img_src}/{row['file_name']}"
        print(f"\n\n=== 处理样本 {idx + 1}/{len(data)} ===")
        print("🤖 初始化辩论系统...")
        print(f"📊 模因文本: {meme_text}")
        print(f"🖼️  模因图片: {meme_src}")
        debate_graph = DebateGraph(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE
        )

        # 记录开始时间
        start_time = time.time()
        # 运行辩论
        try:
            final_state = debate_graph.run_debate(
                meme_text=meme_text,
                meme_src=meme_src,
                news_path='sample_news.txt',
                meme_content = row.get('description', "")
            )

            # 总耗时
            total_time = time.time() - start_time
            print(f"\n⏱️  总执行时间: {total_time:.2f} 秒")
            # 显示关键结果
            print("\n" + "="*60)
            print("🎯 关键结果摘要")
            print("="*60)
            print(f"✅ 领域检测: {final_state['domain']}")
            print(f"✅ 证据收集: {'已启用' if final_state['evidence_enabled'] else '已禁用'}")
            print(f"✅ 总发言数: {len(final_state['transcript'])}")
            print(f"✅ 最终判决: {final_state['verdict']}")
        except Exception as e:
            print(f"\n❌ 执行过程中出错: {e}")
            import traceback
            traceback.print_exc()

elif DATASET_NAME == 'HARM':
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    cache_dir = DATASET_NAME
    cache_path = os.path.join(cache_dir, "result.json")
    processed_ids = set()
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        processed_ids = set(cache_data.keys())
    for idx, line in tqdm(enumerate(lines), total=len(lines)):
        # 1. 解析当前行（假设是 JSONL 格式）
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        meme_text = sample['text']
        meme_src = f"{img_src}/{sample['image']}"
        meme_id = meme_src.split('/')[-1].split('.')[0]
        if meme_id in processed_ids:
            print(f"⚡ 跳过已处理样本: {meme_id}")
            continue
        meme_content = sample.get('description', "")
        labels = sample['labels']
        if 'not harmful' in labels:
            ground_truth = 0
        else:
            ground_truth = 1

        if not os.path.isfile(meme_src):
            print(f"[✗] 图片文件不存在: {meme_src}")

        debate_graph = DebateGraph(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE
        )
        # 记录开始时间
        start_time = time.time()
        # 运行辩论
        try:
            final_state = debate_graph.run_debate(
                meme_text=meme_text,
                meme_src=meme_src,
                news_path='sample_news.txt',
                meme_content = sample.get('description', ""),
                ground_truth = ground_truth
            )
            # 总耗时
            total_time = time.time() - start_time
            print(f"\n⏱️  总执行时间: {total_time:.2f} 秒")
        except Exception as e:
            continue