import os
import json
import time
from pathlib import Path
from config import AUTO_SAVE,DATASET_NAME
from typing import Dict, Any
import json
import os


def append_to_json(file_path: str,meme_id,data):
    """
    往 JSON 文件追加数据（list 格式），自动创建目录和文件。
    
    参数:
        file_path: JSON 文件路径
        data: 要追加的数据（任意 JSON 可序列化对象）
    """
    # 1. 自动创建目录
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    # 2. 读取现有数据（如果文件存在）
    file_path = os.path.join(file_path, "result.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)
    else:
        data_list = {}
    # 3. 追加并写入
    data_list[meme_id] = data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=2, ensure_ascii=False)

def save_result_node(state: Dict[str, Any]) -> Dict[str, Any]:
    os.makedirs(DATASET_NAME, exist_ok=True)
    meme_id = state['meme_src'].split('/')[-1].split('.')[0]
    # 准备保存数据
    save_data =  {
        "domain": state["domain"],
        "profiles": state["profiles"],
        "transcript": state["transcript"],
        "refer_dimension": state["refer_dimension"],
        "evidence_data":state["evidence_data"],
        "evidence_score":state["evidence_score"],
        "scores": state["scores"],
        "ground_truth": state["ground_truth"],
    }
    # 保存到文件
    append_to_json(DATASET_NAME, meme_id,save_data)
    print(f"✅ 结果已保存到: {os.path.join(DATASET_NAME, 'result.json')}")
    return state