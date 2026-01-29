from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME
import time
import json
from tqdm import tqdm
import random
random.seed(44)
if DATASET_NAME=="FHM":
    data_src = 'data/FHM/data/dev_with_description_copy.jsonl'
    img_src = 'data/FHM/data'
elif DATASET_NAME=="MAMI":
    data_src = 'data/MAMI/test_with_description.tsv'
    img_src = 'data/MAMI/img'
elif DATASET_NAME=="HARM":
    data_src = 'data/HARM/test_with_description_copy.jsonl'
    img_src = 'data/HARM/images'
else:
    raise ValueError("Unsupported DATASET_NAME. Choose either 'FHM' or 'MAMI'.")
if DATASET_NAME == 'FHM':
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    sampled_lines = random.sample(lines, min(100, len(lines)))
    for idx, line in tqdm(enumerate(sampled_lines), total=len(sampled_lines)):
        # 1. 解析当前行（假设是 JSONL 格式）
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        if True:#sample['id'] in [52634, 2364, 17045, 26397, 26439, 28406, 29174, 32049, 32875, 34975]: #52634, 2364, 17045, 26397, 26439, 28406, 29174, 32049, 32875, 34975, 39076, 42903, 43698, 46812, 47183, 49028, 52079, 52634, 53491, 57823, 59806, 61503, 62970, 65801, 76015, 78612, 82509, 84273, 84302, 85621, 92068, 92317, 92567, 93172, 95038, 97320
            search_res = sample.get('search_results', {})['results'][0]
            evidence = f"Title: {search_res.get('title', '')}\nContent: {search_res.get('content', '')}\n"
            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['img']}"
            meme_content = sample.get('description', "")
            label = sample['label']
            print(f"\n\n=== 处理样本 {idx + 1}/{len(lines)} ===")
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
                    evidence=evidence,
                    meme_text=meme_text,
                    meme_src=meme_src,
                    news_path='sample_news.txt',
                    meme_content = meme_content
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
                print(f"✅ 最终判决: {final_state['verdict']}",f"（真实标签: {label}")
                
            except Exception as e:
                print(f"\n❌ 执行过程中出错: {e}")
                import traceback
                traceback.print_exc()
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
    for idx, line in tqdm(enumerate(lines), total=len(lines)):
        # 1. 解析当前行（假设是 JSONL 格式）
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        search_res = sample.get('search_results', {})['results'][0]
        evidence = f"Title: {search_res.get('title', '')}\nContent: {search_res.get('content', '')}\n"
        meme_content = sample.get('description', "")
        labels = sample['labels']
        meme_text = sample['text']
        meme_src = f"{img_src}/{sample['image']}"
        search_res = sample.get('search_results', {})['results'][0]
        evidence = f"Title: {search_res.get('title', '')}\nContent: {search_res.get('content', '')}\n"
        print(f"\n\n=== 处理样本 {idx + 1}/{len(lines)} ===")
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
                meme_content = sample.get('description', ""),
                evidence=evidence
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
            print(f"✅ 最终判决: {final_state['verdict']}",f"（真实标签: {labels}")
        except Exception as e:
            print(f"\n❌ 执行过程中出错: {e}")
            import traceback
            traceback.print_exc()