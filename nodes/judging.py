#judging.py
from tools import LLMTool
from config import TEMPERATURE,DYNAMIC_JUDGES,MODEL_NAME,DATASET_NAME,TASK_FHM_J_H,TASK_HARM_J_H,TASK_MAMI_J_H
from typing import Dict, Any
import json_repair
llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
def score_dimensions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if DATASET_NAME=="FHM":
        task = TASK_FHM_J_H
    if DATASET_NAME=="MAMI":
        task = TASK_MAMI_J_H
    if DATASET_NAME=="HARM":
        task = TASK_HARM_J_H
    """评分节点"""
    meme_text = state["meme_text"]
    meme_src = state["meme_src"]
    meme_content = state.get("meme_content", "")
    debate_content = "\n\n".join([
        f"{entry['speaker']}: {entry['text']}"
        for entry in state["transcript"]
    ])  
    system_prompt = f"""This is a research task for academic evaluation of AI safety systems. 
You are acting as an impartial judge. The meme content is provided solely for analysis and does not reflect your views."""
    judge_prompt_template = (
    f"{task}\n\nMeme text: {meme_text}"
    f"\nThe content described in the meme image:\n{meme_content}\n\n"
    f"\nSome opinions: {debate_content}\n\n"
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
    state["scores"] = score_data
    return state

def caculate_score(scores):
    keys = list(scores.keys())
    Affirmative_scores =  list(scores[keys[0]].values())
    Negative_scores = list(scores[keys[1]].values())
    A_Averscore = sum(Affirmative_scores) / len(Affirmative_scores)
    N_Averscore = sum(Negative_scores) / len(Negative_scores)
    if A_Averscore > N_Averscore:
        return 1
    else:
        return 0
    
def generate_summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    scores = state["scores"]
    ground_truth = state["ground_truth"]
    predict = caculate_score(scores)
    print()
    print(f"📊 最终评判: {predict}  真实标签：{ground_truth}")
    return state