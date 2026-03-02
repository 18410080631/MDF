#profile_generation.py
from typing import Dict, Any
from config import DATASET_NAME, TASK_FHM,MODEL_NAME,TEMPERATURE,TASK_HARM
from tools import LLMTool
import json
import json_repair
def generate_profiles_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """生成角色画像节点"""
    domain = state["domain"]
    profiles = {
    'Affirmative_Opening': f'As the first affirmative speaker.',
    'Affirmative_Rebuttal': f'As the second affirmative speaker.',
    'Affirmative_Free': f'As the third affirmative speaker.',
    'Affirmative_Closing': f'As the final affirmative speaker.',

    'Negative_Opening': f'As the first negative speaker.',
    'Negative_Rebuttal': f'As the second negative speaker.',
    'Negative_Free': f'As the third negative speaker.',
    'Negative_Closing': f'As the final negative speaker.'
    }
    meme_text = state['meme_text']
    meme_src = state["meme_src"]
    meme_content = state.get("meme_content", "")
    prompt = (
        f"Domain: {domain}\n"
        f"Meme text:\n{meme_text}\n\n"
        f"Meme content:\n{meme_content}\n\n"
        "Evaluation criteria to guide the debate:\n"
        "Your task is to generate a concise expert profile for each of the following 8 debate roles. "
        "Each profile must:\n"
        "- Start with 'As ...';\n"
        "- Reflect an expert whose perspective directly engages with the evaluation criteria above;\n"
        "- Be tailored to the specific function of the role in the debate flow (e.g., opening establishes core claim, rebuttal counters opponent, etc.);\n"
        "- Remain general enough to apply across memes but specific enough to invoke relevant standards (e.g., legal, psychological, cultural);\n"
        "- Avoid verbose or fictional titles—focus on functional expertise.\n\n"
        "Debate roles:\n"
        "Affirmative_Opening, Affirmative_Rebuttal, Affirmative_Free, Affirmative_Closing,\n"
        "Negative_Opening, Negative_Rebuttal, Negative_Free, Negative_Closing\n\n"
        "Output ONLY a valid JSON object with the exact role names as keys and the profile strings as values. "
        "Do not include any other text, explanation, or formatting.\n\n"
        "Example output format:\n"
        "{"
        "  'Affirmative_Opening': 'As a ...',\n"
        "  'Affirmative_Rebuttal': 'As a ...',\n"
        "  'Affirmative_Free': 'As a ...',\n"
        "  'Affirmative_Closing': 'As a ...',\n"
        "  'Negative_Opening': 'As a ...',\n"
        "  'Negative_Rebuttal': 'As a ...',\n"
        "  'Negative_Free': 'As a ...',\n"
        "  'Negative_Closing': 'As a ...'\n"
        "}"
    )
    llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
    response = llm_tool.call_llm(
            system_prompt="You are an expert in generating role profiles for adversarial debate agents in zero-shot harmful meme detection.",
            messages=[{"role": "user", "content": prompt}],
            #meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=512
        )
    try:
        profiles = json_repair.loads(response)
        print("角色画像生成完成...")
    except Exception as e:
        print(response)
        print("⚠️ JSON解析错误，使用预定义画像。")
    # 更新状态
    state["profiles"] = profiles
    return state