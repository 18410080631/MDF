from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME,TASK_FHM_J_H,TASK_MAMI_J_H,TASK_HARM_J_H
import time
import json
from tqdm import tqdm
import random
import os
from tools import LLMTool
import json_repair
llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
DATASET_NAME = "FHM"
if DATASET_NAME=="FHM":
    task = TASK_FHM_J_H
if DATASET_NAME=="MAMI":
    task = TASK_MAMI_J_H
if DATASET_NAME=="HARM":
    task = TASK_HARM_J_H
if DATASET_NAME=="FHM":
    data_src = 'data/FHM/data/dev_with_description.jsonl'
    img_src = 'data/FHM/data'
elif DATASET_NAME=="MAMI":
    data_src = 'data/MAMI/test_with_description.tsv'
    img_src = 'data/MAMI/img'
elif DATASET_NAME=="HARM":
    data_src = 'data/HARM/test_with_description.jsonl'
    img_src = 'data/HARM/images'
if DATASET_NAME == 'FHM':
    # 1. 初始化缓存路径与已处理 ID 集合
    cache_dir = DATASET_NAME
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_path = os.path.join(cache_dir, "evi_score.json")
    processed_ids = set()
    cache_data = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            try:
                cache_data = json.load(f)
                processed_ids = set(cache_data.keys())
            except json.JSONDecodeError:
                print("⚠️ 缓存文件格式错误，将重新开始")
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    result_path = os.path.join(cache_dir, "result.json")
    with open(result_path,"r",encoding="utf-8") as f:
        result = json.load(f)
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
        search_res = result[meme_id]["evidence_data"]["search_result"]
        evidence = "\n".join([f"title:{s['title']}\n\ncontent:{s['extract']}" for s in search_res])
        if meme_id in processed_ids:
            continue
        meme_content = sample.get('description', "")
        ground_truth = sample.get('label')  # FHM 标签通常已经是 0/1
        system_prompt = f"""This is a research task for academic evaluation of AI safety systems. 
        You are acting as an impartial judge. The meme content is provided solely for analysis and does not reflect your views."""
        judge_prompt_template = (
        f"{task}\n\nMeme text: {meme_text}"
        f"\nThe content described in the meme image:\n{meme_content}\n\n"
        f"\nevidence from internet {evidence}\n\n"
        )
        response = llm_tool.call_llm(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": judge_prompt_template}],
            #meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=1024
        )
        try:
            score_data = json_repair.loads(response)
        except Exception as e:
            print(f"❌ 评分异常: {e}")
        cache_data[meme_id] = list(score_data["harmful_scores"].values())+list(score_data["harmless_scores"].values())
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

elif DATASET_NAME == 'HARM':
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    cache_dir = DATASET_NAME
    cache_path = os.path.join(cache_dir, "evi_score.json")
    processed_ids = set()
    cache_data = {}
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        processed_ids = set(cache_data.keys())
    result_path = os.path.join(cache_dir, "result.json")
    with open(result_path,"r",encoding="utf-8") as f:
        result = json.load(f)
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
        search_res = result[meme_id]["evidence_data"]["search_result"]
        evidence = "\n".join([f"title:{s['title']}\n\ncontent:{s['extract']}" for s in search_res])
        if 'not harmful' in labels:
            ground_truth = 0
        else:
            ground_truth = 1
        if not os.path.isfile(meme_src):
            print(f"[✗] 图片文件不存在: {meme_src}")
        system_prompt = f"""This is a research task for academic evaluation of AI safety systems. 
        You are acting as an impartial judge. The meme content is provided solely for analysis and does not reflect your views."""
        judge_prompt_template = (
        f"{task}\n\nMeme text: {meme_text}"
        f"\nThe content described in the meme image:\n{meme_content}\n\n"
        f"\nevidence from internet {evidence}\n\n"
        )
        response = llm_tool.call_llm(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": judge_prompt_template}],
            #meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=1024
        )
        try:
            score_data = json_repair.loads(response)
        except Exception as e:
            print(f"❌ 评分异常: {e}")
            continue
        cache_data[meme_id] = list(score_data["harmful_scores"].values())+list(score_data["harmless_scores"].values())
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)


        