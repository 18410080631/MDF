from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from state_schema import DebateState
from nodes.domain_detection import detect_domain_node
from nodes.profile_generation import generate_profiles_node
from nodes.evidence_collection import gather_evidence_node
from nodes.debate_phases import (
    run_opening_node, run_rebuttal_node, 
    run_free_debate_node, run_closing_node
)
from nodes.judging import score_dimensions_node, generate_summary_node
from nodes.saving import save_result_node
from config import ENABLE_EVIDENCE, EVIDENCE_PHASE, FREE_ROUNDS,MODEL_NAME

class DebateGraph:
    """LangGraph辩论流程管理器"""
    
    def __init__(self, model_name: str = MODEL_NAME, temperature: float = 1.0):
        self.model_name = model_name
        self.temperature = temperature
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建完整的辩论状态图"""
        # 初始化状态图
        workflow = StateGraph(DebateState)
        
        # 添加节点
        workflow.add_node("detect_domain", detect_domain_node)
        workflow.add_node("generate_profiles", generate_profiles_node)
        workflow.add_node("gather_evidence", gather_evidence_node)
        workflow.add_node("run_opening", run_opening_node)
        workflow.add_node("run_rebuttal", run_rebuttal_node)
        workflow.add_node("run_free_debate", run_free_debate_node)
        workflow.add_node("run_closing", run_closing_node)
        workflow.add_node("score_dimensions", score_dimensions_node)
        workflow.add_node("generate_summary", generate_summary_node)
        workflow.add_node("save_result", save_result_node)
        
        # 设置起点
        workflow.set_entry_point("detect_domain")
        
        # 顺序连接
        workflow.add_edge("detect_domain", "generate_profiles")
        
        # 条件边：是否在Opening阶段收集证据
        def should_gather_evidence_opening(state: DebateState) -> Literal["gather_evidence", "run_opening"]:
            # print(state)
            # if state["evidence_enabled"] and state["evidence_phase"] == "Opening":
            #     #print("🔄 证据系统启用且设定在Opening阶段收集证据，进入证据收集节点。")
            #     return "gather_evidence"
            # #print("⏭️ 跳过证据收集，直接进入Opening阶段。")
            return "run_opening"
        
        workflow.add_conditional_edges(
            "generate_profiles",
            should_gather_evidence_opening,
            {
                "gather_evidence": "gather_evidence",
                "run_opening": "run_opening"
            }
        )
        
        # 证据收集后连接到Opening
        workflow.add_edge("gather_evidence", "run_opening")
        
        # 辩论阶段顺序
        workflow.add_edge("run_opening", "run_rebuttal")
        workflow.add_edge("run_rebuttal", "run_free_debate")
        
        # 条件边：是否有自由辩论
        def should_run_free_debate(state: DebateState) -> Literal["run_free_debate", "run_closing"]:
            return "run_free_debate" if state["max_free_rounds"] > 0 else "run_closing"
        
        workflow.add_conditional_edges(
            "run_rebuttal",
            should_run_free_debate,
            {
                "run_free_debate": "run_free_debate",
                "run_closing": "run_closing"
            }
        )
        
        # 自由辩论循环
        def continue_free_debate(state: DebateState) -> Literal["run_free_debate", "run_closing"]:
            if state["free_debate_round"] <= state["max_free_rounds"]:
                return "run_free_debate"
            return "run_closing"
        
        workflow.add_conditional_edges(
            "run_free_debate",
            continue_free_debate,
            {
                "run_free_debate": "run_free_debate",
                "run_closing": "run_closing"
            }
        )
        
        # 继续辩论流程
        workflow.add_edge("run_closing", "score_dimensions")
        workflow.add_edge("score_dimensions", "generate_summary")
        workflow.add_edge("generate_summary", "save_result")
        workflow.add_edge("save_result", END)
        
        return workflow.compile()
    
    def run_debate(self, meme_text: str, meme_src: str, news_path: str, meme_content: str,evidence:str) -> Dict[str, Any]:
        """运行完整辩论流程"""
        print("\n" + "="*80)
        print("🚀 启动辩论到检测系统 ")
        print("="*80)
        
        # 初始化状态
        initial_state = {
            "meme_text": meme_text,
            "meme_src": meme_src,
            "meme_content": meme_content,
            "news_path": str(news_path),
            
            # 领域和角色
            "domain": "",
            "profiles": {},
            
            # 证据系统
            "evidence_enabled": ENABLE_EVIDENCE,
            "evidence_phase": EVIDENCE_PHASE,
            "evidence_data": evidence,
            "affirmative_evidence": None,
            "negative_evidence": None,
            
            # 辩论状态
            "current_phase": "Opening",
            "free_debate_round": 1,
            "max_free_rounds": FREE_ROUNDS,
            
            # 对话管理
            "shared_memory": [],
            "transcript": [],
            
            # 评分和判决
            "scores": {"Affirmative": 0, "Negative": 0},
            "verdict": "",
            "summary": "",
            
            # 中间结果
            "intermediate_results": {}
        }
        
        # 执行图
        final_state = self.graph.invoke(initial_state)
        
        # print("\n" + "="*80)
        # print("🏁 辩论流程完成!")
        # print(f"   🏆 最终判决: {final_state['verdict']}")
        # print(f"   💯 总分: Affirmative={final_state['scores']['Affirmative']}, Negative={final_state['scores']['Negative']}")
        # print("="*80)
        
        return final_state