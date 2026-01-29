from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME
import time
import json
from tqdm import tqdm
from tools import LLMTool

prompt = """
You are a meme judge. Given the meme text and image description, determine whether the meme is harmful or harmless. Provide your verdict and a concise justification in the following JSON format:
Do not include any other text, markdown, or explanation. Only output valid JSON like this:
{
  "verdict": "harmful" or "harmless",
  "reason": "your concise reason here"
}


"""
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
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    res = []
    for idx, line in tqdm(enumerate(lines), total=len(lines)):
        # 1. 解析当前行（假设是 JSONL 格式）
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        meme_text = sample['text']
        meme_src = f"{img_src}/{sample['img']}"
        llm = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
        response = llm.call_llm(
            system_prompt=prompt,
            messages=[{"role": "user", "content": meme_text}],
            meme_src=meme_src,
            temperature=TEMPERATURE
        ).strip().lower()
        res.append({
            'id': sample['id'],
            'prediction': response
        })
    with open('fhm_predictions.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
        
elif DATASET_NAME == 'MAMI':
    import pandas as pd
    data = pd.read_csv(data_src, sep='\t')
    img_src = 'data/MAMI/test_images'
    res = []
    for idx, row in tqdm(data.iterrows(), total=len(data)):
        meme_text = row['text']
        meme_src = f"{img_src}/{row['file_name']}"
        llm = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
        response = llm.call_llm(
            system_prompt=prompt,
            messages=[{"role": "user", "content": meme_text}],
            meme_src=meme_src,
            temperature=TEMPERATURE
        ).strip().lower()
        print(f"样本 {idx + 1}: 预测结果 - {response}")
        res.append({
            'id': row['id'],
            'prediction': response
        })  
    with open('mami_predictions.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)

elif DATASET_NAME == 'HARM':
    with open(data_src, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    res = []
    for idx, line in tqdm(enumerate(lines), total=len(lines)):
        # 1. 解析当前行（假设是 JSONL 格式）
        try:
            sample = json.loads(line.strip())
        except json.JSONDecodeError:
            print(f"❌ 跳过无法解析的行 {idx + 1}")
            continue
        meme_text = sample['text']
        meme_src = f"{img_src}/{sample['image']}"
        llm = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
        response = llm.call_llm(
            system_prompt=prompt,
            messages=[{"role": "user", "content": meme_text}],
            meme_src=meme_src,
            temperature=TEMPERATURE
        ).strip().lower()
        print(f"样本 {idx + 1}: 预测结果 - {response}")
        res.append({
            'id': sample['id'],
            'prediction': response
        })
    with open('harm_predictions.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
    