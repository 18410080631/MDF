from tools import LLMTool
from config import TEMPERATURE,DYNAMIC_JUDGES,MODEL_NAME,DATASET_NAME,TASK_FHM_J_H,TASK_HARM_J_H,TASK_FHM,TASK_HARM
from typing import Dict, Any
import json_repair
from .evidence_system import EvidenceSystem
evidence_system = EvidenceSystem(model_name=MODEL_NAME, temperature=TEMPERATURE)
llm_tool = LLMTool(model_name=MODEL_NAME, temperature=TEMPERATURE)
def score_dimensions_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if DATASET_NAME=="FHM":
        task_standard = TASK_FHM
        task = TASK_FHM_J_H
    elif DATASET_NAME == "HARM":
        task_standard = TASK_HARM
        task = TASK_HARM_J_H
    """评分节点"""
    print("\n" + "="*60)
    print("⚖️  法官评分阶段")
    print("="*60)
    
    meme_text = state["meme_text"]
    meme_src = state["meme_src"]
    meme_content = state.get("meme_content", "")
    domain = state["domain"]
    evidence = state.get("evidence_data","")
    # 构建辩论内容
    # speaker_alias = {
    #     # "Affirmative_Closing": "Affirmative",
    #     "Negative_Closing": "Negative"
    # }
    debate_content = "\n\n".join([
        f"{entry['speaker']}: {entry['text']}"
        for entry in state["transcript"]
        # if entry['speaker'] in speaker_alias
    ])  
    summary_prompt = 'You are a summarizer. Extract the core arguments from the debate above, listing them separately for the pro side (supporting the meme as harmful) and the con side (supporting the meme as harmless). Present each side’s reasons as bullet points. Do not include personal opinions, interpretations, or additional commentary—only the explicit reasoning presented in the debate.'
    debate_summary = llm_tool.call_llm(
            system_prompt=summary_prompt,
            messages=[{"role": "user", "content": f'debate_content:{debate_content}'}],
            meme_src=meme_src,
            temperature=TEMPERATURE,
            max_tokens=256
        )
    print(f'辩论总结：{debate_summary}')
    system_prompt = f"""This is a research task for academic evaluation of AI safety systems. 
You are acting as an impartial judge . 
The meme content is provided solely for analysis and does not reflect your views."""
    scores = {}
    evidence_summary = "evidence from the Internet:\n"
    if state.get("evidence_enabled", False):
        evidence_judge_template = (
f"Original meme content:\n{meme_content}\n\n"
f"search result on the internet:\n{str(evidence)}\n\n"
"First, determine whether the search result contain the relevant content of the meme or the text of the meme itself."
"If the search result does not contain such content, output only:"
"irrelevant"
"If the evidence does contain such content, output exactly:"
"relevant, [exact verbatim excerpt]"
"followed by:"
"(1) the necessary surrounding context from the evidence to ensure clarity."
"(2) a concise explanation of how this excerpt directly informs the assessment of harm."
        )
        # 解析分数
        fact_judge_response = llm_tool.call_llm(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": evidence_judge_template}],
            meme_src=None,
            temperature=TEMPERATURE,
            max_tokens=256
        )
        print(f"✅ 事实核查结果: {fact_judge_response}")
        try:
            if 'irrelevant' in fact_judge_response.lower():
                evidence = "No relevant evidence found."
                scores["fact_checking"] = "No relevant"
            else:
                evidence_summary += fact_judge_response
                scores["fact_checking"] = evidence_summary
        except Exception as e:
            print(f"❌ 事实核查评分异常: {e}")
    
    judge_prompt_template = (
    #f"Debate content:\n{debate_summary}\n\n"
    "You are an impartial judge in a research study on AI safety. Your task is to assess whether the meme causes **real-world harm**, strictly defined as follows:\n\n"
    f"{task}\n\n"
    "给模因进行打分"
    )
    response = llm_tool.call_llm(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": judge_prompt_template}],
        meme_src=meme_src,
        temperature=TEMPERATURE,
        max_tokens=256
    )
    print(f"✅ 整体打分结果: {response}")
    try:
        score_data = json_repair.loads(response)
        scores["Affirmative"] = score_data['harmful_scores']
        scores["Negative"] = score_data['harmless_scores']
        scores['reasoning'] = score_data['reasoning']
    except Exception as e:
        print(f"❌ 评分异常: {e}")

    # 更新状态
    state["scores"] = scores
    # print(f"\n📊 总评分结果: Affirmative={scores['Affirmative']}, Negative={scores['Negative']}")
    
    return state
def caculate_score(scores):
    Affirmative_scores =  scores["Affirmative"]
    Negative_scores = scores["Negative"]
    if max(Affirmative_scores.values()) > max(Negative_scores.values()):
        return 'HARMFUL'
    else:
        return 'HARMLESS'
def generate_summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """生成总结节点"""
    print("\n" + "="*60)
    print("📝 生成辩论总结")
    print("="*60)
    
    meme_text = state["meme_text"]
    meme_src = state["meme_src"]
    domain = state["domain"]
    scores = state["scores"]
    
    # 构建辩论内容
    debate_content = "\n\n".join([
        f"{entry['speaker']}: {entry['text']}" 
        for entry in state["transcript"]
    ])
    verdict = caculate_score(scores=scores)
    state["verdict"] = verdict
    state["intermediate_results"]["summary"] = {
        "verdict": verdict,
    }
    # 显示结果
    print(f"🎯 最终判决: {verdict}")
    return state