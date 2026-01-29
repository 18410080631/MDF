from tools import LLMTool
from config import PHASE_TEMPLATES, DEBATE_ROLES,TEMPERATURE,MODEL_NAME,DATASET_NAME,TASK_FHM,TASK_HARM
from .evidence_system import EvidenceSystem
from typing import Dict, Any

def run_debate_phase_node(state: Dict[str, Any], phase: str) -> Dict[str, Any]:
    """运行特定辩论阶段的通用节点"""
    print("\n" + "="*60)
    print(f"🎤 {phase} 阶段辩论")
    print("="*60)
    #print(state)
    if DATASET_NAME == "FHM":
        task = TASK_FHM
    elif DATASET_NAME == "HARM":
        task = TASK_HARM
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
    elif phase == "Free" and state["free_debate_round"] <= state["max_free_rounds"]:
        # 自由辩论阶段，按轮次控制
        speakers = ["Affirmative_Free", "Negative_Free"]
        state["free_debate_round"] += 1
    elif phase == "Closing":
        speakers = ["Affirmative_Closing", "Negative_Closing"]
    #改
    meme_content = state.get("meme_content", "")
    # 为每个发言人生成回应
    for speaker in speakers:
        print(f"\n💬 {speaker} 发言中...")
        
        # 获取系统提示
        stance = "harmful" if speaker.startswith("Affirmative") else "harmless"
         
        
        system_prompt = system_prompt = (
        "You are participating in an academic research simulation on AI safety. "
        "Your role is to represent a specific perspective in a structured debate about whether an internet meme is harmful.\n\n"
        f"Debate stance: You are arguing that the meme is **{stance}**.\n"
        f"Domain context: {domain}\n"
        f"Original meme content:\n{meme_content}\n"
        f"Your role profile: {profiles.get(speaker, 'A thoughtful participant with relevant expertise.')}\n\n"
        f"The evaluation criteria are as follows:"
        f"{task}"
        f"Explicitly reference which specific criterion from the evaluation criteria above it is based on. Your justification should directly link the meme’s content to the relevant standard—such as “harmful” or “harmless”—and explain how the meme meets or fails to meet that criterion."
        "- Keep your response concise (~100 words).\n\n"
        )
        # 构建用户提示
        opponent = "Negative" if speaker.startswith("Affirmative") else "Affirmative"
        opponent_role = f"{opponent}_{'_'.join(speaker.split('_')[1:])}"
        
        # 获取对手上一轮发言
        opponent_last = ""
        for entry in reversed(state["transcript"]):
            if entry["speaker"] == opponent_role:
                opponent_last = entry["text"]
                break
        # 选择模板
        print(f"📝 准备 {phase} 阶段提示...")
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
        # 调用LLM
        llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
        response = llm_tool.call_llm(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            #改
            #meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=512
        )
        # 记录到transcript
        state["transcript"].append({
            "speaker": speaker,
            "text": response
        })
        # 记录到shared_memory
        state["shared_memory"].extend([
            {"role": "user", "content": f"{speaker}: {prompt}"},
            {"role": "assistant", "content": f"{speaker}: {response}"}
        ])
        # 显示结果
        print(f"✅ {speaker} 发言完成:")
        print(f"   {response[:200]}...")
    # 更新当前阶段
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