from .evidence_system import EvidenceSystem
from typing import Dict, Any, Optional
from config import OPENAI_API_KEY, OPENAI_API_BASE, MODEL_NAME,TEMPERATURE
def gather_evidence_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """收集证据节点"""
    if not state["evidence_enabled"]:
        print("\n" + "="*60)
        print("🔍 证据系统已禁用，跳过证据收集...")
        print("="*60)
        return state
    
    print("\n" + "="*60)
    print("📚 收集网络证据...")
    print("="*60)
    
    meme_text = state["meme_text"]
    meme_src = state["meme_src"]
    
    # 初始化证据系统
    evidence_system = EvidenceSystem(model_name = MODEL_NAME,temperature=TEMPERATURE)
    
    # 收集证据
    evidence_data = evidence_system.gather_evidence(meme_text, meme_src)
    
    # 过滤证据
    affirmative_evidence = evidence_system.filter_evidence_by_stance(evidence_data, 'SUPPORTS_TRUE')
    negative_evidence = evidence_system.filter_evidence_by_stance(evidence_data, 'SUPPORTS_FALSE')
    
    # 更新状态
    state["evidence_data"] = evidence_data
    state["affirmative_evidence"] = affirmative_evidence
    state["negative_evidence"] = negative_evidence
    
    # 计算统计信息
    total_evidence = len(evidence_data['evidence'])
    aff_count = len(affirmative_evidence['evidence'])
    neg_count = len(negative_evidence['evidence'])
    
    # 记录中间结果
    evidence_summary = {
        "total_evidence": total_evidence,
        "affirmative_favorable": aff_count,
        "negative_favorable": neg_count,
        "keywords": evidence_data['keywords']
    }
    
    state["intermediate_results"]["evidence_collection"] = evidence_summary
    
    # 显示中间结果
    print(f"📊 证据收集结果:")
    print(f"   • 总证据数: {total_evidence}")
    print(f"   • 支持正方 (有害): {aff_count}")
    print(f"   • 支持反方 (无害): {neg_count}")
    print(f"   • 关键词: {', '.join(evidence_data['keywords'])}")
    
    # 显示部分证据
    if total_evidence > 0:
        print("\n🔍 部分证据预览:")
        for i, (kw, info) in enumerate(list(evidence_data['evidence'].items())[:3]):
            print(f"  {i+1}. [{info.get('stance', 'NEUTRAL')}] {info['title']}")
            print(f"     摘要: {info['extract'][:100]}...")
    
    return state