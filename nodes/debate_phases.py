#debate_phases.py
from tools import LLMTool
from config import PHASE_TEMPLATES, DEBATE_ROLES,TEMPERATURE,MODEL_NAME,DATASET_NAME,TASK_FHM,TASK_HARM,TASK_FHM_J_H,TASK_HARM_J_H,TASK_MAMI,TASK_MAMI_J_H
from typing import Dict, Any
import re
import json_repair
llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
def extract_json_from_output(text):
    """
    从文本中提取 JSON/字典部分，支持多种格式：
    1. ```json { ... } ```
    2. ``` { ... } ```
    3. 纯字典 { ... }
    """
    # 尝试 1: 匹配 ```json 代码块
    match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
    if match:
        return json_repair.loads(match.group(1).strip())
    
    # 尝试 2: 匹配 ``` 代码块（无语言标识）
    match = re.search(r'```\s*(\{[\s\S]*?\})\s*```', text)
    if match:
        return json_repair.loads(match.group(1).strip())
    
    # 尝试 3: 直接匹配最外层的 { } （处理嵌套）
    # 从第一个 { 开始，找到匹配的 }
    start_idx = text.find('{')
    if start_idx != -1:
        # 计数括号匹配
        brace_count = 0
        end_idx = start_idx
        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if brace_count == 0:
            data = json_repair.loads(text[start_idx:end_idx].strip())
            return data
    return None
def run_debate_phase_node(state: Dict[str, Any], phase: str) -> Dict[str, Any]:
    """运行特定辩论阶段的通用节点"""
     # 初始化维度计数器
    if DATASET_NAME=="FHM":
        js = extract_json_from_output(TASK_FHM_J_H)
        dim = len(js[list(js.keys())[0]]) + len(js[list(js.keys())[1]])
        dims_strs = list(js[list(js.keys())[0]].keys()) + list(js[list(js.keys())[1]].keys()) 
        refer_dimension = state.get("refer_dimension", [0]*dim) 
        task = TASK_FHM
    elif DATASET_NAME=="HARM":
        js = extract_json_from_output(TASK_HARM_J_H)
        dim = len(js[list(js.keys())[0]]) + len(js[list(js.keys())[1]])
        dims_strs = list(js[list(js.keys())[0]].keys()) + list(js[list(js.keys())[1]].keys()) 
        refer_dimension = state.get("refer_dimension", [0]*dim) 
        task = TASK_HARM
    elif DATASET_NAME=="MAMI":
        js = extract_json_from_output(TASK_MAMI_J_H)
        dim = len(js[list(js.keys())[0]]) + len(js[list(js.keys())[1]])
        dims_strs = list(js[list(js.keys())[0]].keys()) + list(js[list(js.keys())[1]].keys()) 
        refer_dimension = state.get("refer_dimension", [0]*dim) 
        task = TASK_MAMI
    else:
        ValueError(f"未知数据集：{DATASET_NAME}，支持的数据集：FHM, HARM, MAMI")
    meme_text = state['meme_text']
    meme_src = state["meme_src"]
    domain = state["domain"]
    profiles = state["profiles"]
    # 确定该阶段的发言人
    speakers = []
    if phase == "Opening":
        speakers = ["Affirmative_Opening", "Negative_Opening"]
    elif phase == "Rebuttal":
        speakers = ["Affirmative_Rebuttal", "Negative_Rebuttal"]
    elif phase == "Free":
        # 自由辩论阶段，按轮次控制
        speakers = ["Affirmative_Free", "Negative_Free"]
        state["free_debate_round"] += 1
    elif phase == "Closing":
        speakers = ["Affirmative_Closing", "Negative_Closing"]
    meme_content = state.get("meme_content", "")
    # 为每个发言人生成回应
    for speaker in speakers:
        print(f"💬 {speaker} 发言中...")
        # 获取系统提示
        stance = "harmful" if speaker.startswith("Affirmative") else "harmless"
        system_prompt = system_prompt = (
        "You are participating in an academic research simulation on AI safety. "
        "Your role is to represent a specific perspective in a structured debate about whether an internet meme is harmful.\n\n"
        f"Debate stance: You are arguing that the meme is **{stance}**.\n"
        f"Domain context: {domain}\n"
        f"The content described in the meme image:\n{meme_content}\n"
        f"You are {speaker}\n\nYour role profile: {profiles.get(speaker, 'A thoughtful participant with relevant expertise.')}\n\n"
        f"The evaluation criteria are as follows:"
        f"###"
        f"{task}"
        f"###\n"
        f"Explicitly reference which specific criterion(H1,H2,..,N1,N2,...,N6) from the evaluation criteria above it is based on. Your justification should directly link the meme’s content to the relevant standard—such as “harmful” or “harmless”—and explain how the meme meets or fails to meet that criterion."
        "- Keep your response concise (~60 words).\n\n"
        )
        opponent_last = ""
        for entry in state["transcript"]:
            entry_speaker = entry["speaker"]
            entry_text = entry["text"]
            opponent_last += f"{entry_speaker}: {entry_text}\n"
        template = PHASE_TEMPLATES[phase]
        if phase == "Free":
            prompt = template.format(
                turn=state["free_debate_round"],
                opponent_text=opponent_last
            )
        elif phase in ["Rebuttal", "Closing"]:
            prompt = template
        elif phase == 'Opening':
            prompt = template.format(
                meme_text=meme_text
            )
        response = llm_tool.call_llm(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            #meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=512
        )
        for idx,d in enumerate(dims_strs):
            if d in response:
                refer_dimension[idx]+=1
        state["transcript"].append({
            "speaker": speaker,
            "text": response
        })
    state["refer_dimension"] = refer_dimension
    state["current_phase"] = phase
    return state

# 具体阶段节点
def run_opening_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return run_debate_phase_node(state, "Opening")
def run_rebuttal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return run_debate_phase_node(state, "Rebuttal")
def run_free_debate_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return run_debate_phase_node(state, "Free")
def run_closing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return run_debate_phase_node(state, "Closing")

if __name__ == "__main__":
    data = extract_json_from_output(TASK_FHM_J_H)
    print(data)