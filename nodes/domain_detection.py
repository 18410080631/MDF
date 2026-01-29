from typing import Dict, Any
from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
def detect_domain_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """检测模因所属领域节点"""
    print("\n" + "="*60)
    print("🔍 检测模因领域...")
    print("="*60)
    
    meme_text = state["meme_text"]
    meme_src = state["meme_src"]
    meme_content = state.get("meme_content", "")
    print(f"📝 模因文本: {meme_content[:100]}...")
    # 创建专用LLM工具
    detector = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
    
    # 调用LLM检测领域
    domain = detector.call_llm(
        system_prompt="Classify the domain of the following memes in one or two words.",
        #修改
        # messages=[{"role": "user", "content": meme_text}],
        messages=[{"role": "user", "content": "the content of the meme:" + meme_content}],
        # meme_src=meme_src,
        meme_src=None,
        temperature=TEMPERATURE
    ).strip()
    
    # 更新状态
    state["domain"] = domain
    state["intermediate_results"]["domain_detection"] = {
        "meme_text": meme_text,
        "detected_domain": domain
    }
    
    # 显示中间结果
    print(f"🎯 检测到模因领域: {domain}")
    print(f"📝 模因内容: {meme_text[:100]}...")
    
    return state