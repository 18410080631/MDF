from ddgs import DDGS
from typing import Optional, Dict

# def search_wikipedia(self, keyword: str) -> Optional[Dict]:
#     """
#     使用 DuckDuckGo 通用搜索替代维基百科查询。
#     输入关键词，返回最相关的一条搜索结果（模拟原维基摘要结构）。
#     """
#     try:
#         with DDGS() as ddgs:
#             results = list(ddgs.text(keyword, max_results=1, region='wt-wt'))
        
#         if not results:
#             print(f"    🔍 No result found for '{keyword}'")
#             return None

#         result = results[0]
#         title = result.get('title', keyword)
#         snippet = result.get('body', '')
#         url = result.get('href', '')

#         print(f"    🔍 Found result for '{keyword}': {title}")

#         return {
#             'title': title,
#             'extract': snippet,          # 对应原维基的 extract
#             'url': url,
#             'keyword': keyword
#         }

#     except Exception as e:
#         print(f"[⚠️ DuckDuckGo search failed for '{keyword}'] {e}")
#         return None
# word = 'example'
# result = search_wikipedia(None, word)
# print(result)

from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
from debate_graph import DebateGraph
from pathlib import Path
from config import TEMPERATURE,DATASET_NAME,MODEL_NAME,SEARCH_KEY
import time
import json
from tqdm import tqdm
from tools import SearchTool
search_tool = SearchTool(api_key=SEARCH_KEY)
if DATASET_NAME=="FHM":
    data_src = 'data/FHM/data/dev.jsonl'
    img_src = 'data/FHM/data'
elif DATASET_NAME=="MAMI":
    data_src = 'data/MAMI/data/test.tsv'
    img_src = 'data/MAMI/data/test_images'
elif DATASET_NAME=="HARM":
    data_src = 'data/HARM/test.jsonl'
    img_src = 'data/HARM/images'
else:
    raise ValueError("Unsupported DATASET_NAME. Choose either 'FHM' or 'MAMI'.")
if DATASET_NAME == 'FHM':
    output_path = data_src.replace('.jsonl', '_with_search_results.jsonl') 
    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        lines = f_in.readlines()
        for idx, line in tqdm(enumerate(lines), total=len(lines)):
            if idx<=491:
                continue
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"❌ 跳过无法解析的行 {idx + 1}")
                continue
            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['img']}"
            search_results = search_tool.search(meme_text)
            sample['search_results'] = search_results
            # 写回一行 JSON
            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')

        
elif DATASET_NAME == 'MAMI':
    import pandas as pd
    data = pd.read_csv(data_src, sep='\t')
    img_src = 'data/MAMI/data/test_images'

    descriptions = []
    for idx, row in tqdm(data.iterrows(), total=len(data)):
        meme_text = row['text']
        meme_src = f"{img_src}/{row['file_name']}"
        search_results = search_tool.search(meme_text)
        descriptions.append(search_results)

    # 添加新列
    data['description'] = descriptions

    # 写回（建议写到新文件）
    output_path = data_src.replace('.tsv', '_with_search_results.tsv')
    data.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
    

elif DATASET_NAME == 'HARM':
    import json
    from tqdm import tqdm

    output_path = data_src.replace('.jsonl', '_with_search_results.jsonl')

    with open(data_src, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:

        lines = f_in.readlines()
        for idx, line in tqdm(enumerate(lines), total=len(lines)):
            try:
                sample = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"❌ 跳过无法解析的行 {idx + 1}")
                continue

            meme_text = sample['text']
            meme_src = f"{img_src}/{sample['image']}"  # 注意字段是 'image'
            try:
                search_results = search_tool.search(meme_text)
            except Exception as e:
                print(f"⚠️ 搜索失败 (行 {idx + 1}): {e}")
                search_results = []  # 或 None

            sample['search_results'] = search_results
            f_out.write(json.dumps(sample, ensure_ascii=False) + '\n')