from typing import TypedDict, List, Dict, Optional, Any, Literal
from typing_extensions import Annotated

class DebateState(TypedDict):
    """LangGraph状态定义，贯穿整个辩论流程"""
    meme_text: str
    meme_src: str
    news_path: str
    meme_content: str
    # 领域和角色信息
    domain: str
    profiles: Dict[str, str]
    
    # 证据系统
    evidence_enabled: bool
    evidence_phase: str
    evidence_data: Optional[Dict]
    affirmative_evidence: Optional[Dict]
    negative_evidence: Optional[Dict]
    
    # 辩论状态
    current_phase: str
    free_debate_round: int
    max_free_rounds: int
    
    # 对话管理
    shared_memory: List[Dict[str, Any]]
    transcript: List[Dict[str, str]]
    
    # 评分和判决
    scores: Dict[str, int]
    verdict: str
    summary: str
    
    # 中间结果展示
    intermediate_results: Dict[str, Any]