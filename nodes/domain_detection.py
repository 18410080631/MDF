#domain_detection.py
from typing import Dict, Any
from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
def detect_domain_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """检测模因所属领域节点"""
    # meme_text = state["meme_text"]
    # meme_src = state["meme_src"]
    meme_content = state.get("meme_content", "")
    detector = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
    domain = detector.call_llm(
        system_prompt="Classify the domain of the following memes in one or two words.",
        messages=[{"role": "user", "content": "the content of the meme:" + meme_content}],
        meme_src=None,
        temperature=TEMPERATURE
    ).strip()
    
    state["domain"] = domain
    print(f"🎯 检测到模因领域..")
    return state