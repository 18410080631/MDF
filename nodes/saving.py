import os
import json
import time
from pathlib import Path
from config import SAVE_DIR, SAVE_FMT, AUTO_SAVE,DATASET_NAME
from typing import Dict, Any

def save_result_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """保存结果节点"""
    if not AUTO_SAVE:
        print("\n" + "="*60)
        print("💾 自动保存已禁用，跳过保存步骤...")
        print("="*60)
        return state
    
    print("\n" + "="*60)
    print("💾 保存辩论结果...")
    print("="*60)
    #timestamp = time.strftime("%Y%m%d%H%M%S")
    os.makedirs(SAVE_DIR+DATASET_NAME, exist_ok=True)
    meme_id = state['meme_src'].split('/')[-1].split('.')[0]
    output_path = Path(SAVE_DIR+DATASET_NAME) / f"{meme_id}.{SAVE_FMT.lower()}"
    
    # 准备保存数据
    save_data = {
        "verdict": state["verdict"],
        "scores": state["scores"],
        "domain": state["domain"],
        "profiles": state["profiles"],
        "evidence_enabled": state["evidence_enabled"],
        "meme_text": state["meme_text"],
        "summary": state["summary"],
        "transcript": state["transcript"],
        "intermediate_results": state["intermediate_results"]
    }
    
    # # 保存证据信息
    # if state["evidence_enabled"] and state["evidence_data"]:
    #     save_data.update({
    #         "evidence_data": {
    #             state["evidence_data"]
    #         }
    #     })
    
    # 保存到文件
    if SAVE_FMT.lower() == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Verdict: {state['verdict']}\n")
            f.write(f"Scores: {state['scores']}\n")
            f.write(f"Domain: {state['domain']}\n\n")
            f.write("=== SUMMARY ===\n")
            f.write(state["summary"] + "\n\n")
            f.write("=== TRANSCRIPT ===\n")
            for entry in state["transcript"]:
                f.write(f"{entry['speaker']}: {entry['text']}\n\n")
    
    print(f"✅ 结果已保存到: {output_path}")
    return state