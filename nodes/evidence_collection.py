#evidence_collection.py
from typing import Dict, Any, Optional
from config import OPENAI_API_KEY, OPENAI_API_BASE, MODEL_NAME,TEMPERATURE
from .wiki_search import LLMTool, FactFilterVerificationModule
llm = LLMTool(
    model_name=MODEL_NAME, 
    api_key=OPENAI_API_KEY, 
    base_url=OPENAI_API_BASE,
)
ffv = FactFilterVerificationModule(llm_tool=llm, threshold=0.65)
def gather_evidence_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """收集证据节点"""
    transcript = state["transcript"]
    speeches = [entry["text"] for entry in transcript]
    meme_content = state.get("meme_content", "")
    result = ffv._batch_evaluate_claims(speeches,meme_content)
    state["evidence_data"] = result
    state["evidence_score"] = result.get('cred_scores', [])
    return state