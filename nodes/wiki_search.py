import json
import json_repair
import math
import hashlib
import os
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY,OPENAI_API_BASE,MODEL_NAME,TEMPERATURE
from ddgs import DDGS
import time
import mimetypes, base64
import os
import json
import time
from typing import List, Dict, Optional
# ============== 依赖工具 ==============


def search_wikipedia(
    keyword: str, 
    max_retries: int = 3, 
    retry_delay: float = 1.0,
) -> Optional[Dict]:  
    # ========== 执行搜索（带重试）==========
    for attempt in range(1, max_retries + 1):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(keyword, max_results=10, region='wt-wt'))
            if not results:
                print(f"    🔍 No result for '{keyword}'")
                return None
            data = []
            for r in results:
                if 'title' in r and 'body' in r and 'href' in r:
                    data.append({
                        'title': r['title'],
                        'extract': r['body'],
                        'url': r['href'],
                    })
            return data
            
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** (attempt - 1))
                print(f"[⚠️ Retry {attempt}/{max_retries}] {e}")
                time.sleep(wait_time)
            else:
                print(f"[❌ Failed after {max_retries} retries] {e}")
    return None


class LLMTool:
    """封装 LLM 调用工具，内置本地文件缓存"""
    def __init__(self, model_name: str=MODEL_NAME, temperature: float = TEMPERATURE, 
                 api_key: str = OPENAI_API_KEY, base_url: str = OPENAI_API_BASE,
                 ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.temperature = temperature
    
    def call_llm(self, system_prompt: str, messages: list, 
                max_tokens: int = 2048, temperature: float = None,
                meme_src: str = None) -> str:
        content = []
        user_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
        content.append({"type": "text", "text": user_text})
        if meme_src:
            if meme_src.startswith(("http://", "https://")):
                image_url = meme_src
            else:
                mime_type, _ = mimetypes.guess_type(meme_src)
                with open(meme_src, "rb") as f:
                    b64_image = base64.b64encode(f.read()).decode('utf-8')
                image_url = f"{mime_type};base64,{b64_image}"
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens
        )
        result = response.choices[0].message.content
        return result
    
# ============== 🎯 FFV 主模块（简洁版）=============

class FactFilterVerificationModule:
    """事实过滤核查模块 - 简洁版"""
    
    def __init__(self, llm_tool: LLMTool, threshold: float = 0.65, 
                 max_afus_per_claim: int = 4):
        self.llm = llm_tool
        self.threshold = threshold
        self.max_afus = max_afus_per_claim
    def _get_wikipedia_evidence(self, keyword: str) -> str:
        """获取 Wikipedia 证据"""
        result = search_wikipedia(keyword[:380])
        if len(result) == 0 or result is None:
            evidence = "[No evidence]"
        else:
            evidence = "\n\n".join([f"{r['title']}:\n{r['extract'][:300]}" for r in result])
        return evidence,result
    
    # ========== 📦 Batch 1: 批量 AFU 分解 ==========
    def _batch_claims_score(self, claims: List[str], meme_content: str,evidence:str) -> List[Dict]:
        system_prompt = """You are a rigorous Fact-Checking Expert. 
### Mission Goal
Evaluate each provided "Fact Statement" based on the "Web Search Evidence" and the "Meme Description." You must output a three-dimensional score for each statement.
### Scoring Dimensions (0.0 - 1.0)
* **factual_accuracy**: The degree to which the statement aligns with authoritative facts found in the evidence.
* **evidence_relevance**: The directness of the connection between the provided search evidence and the specific statement.
* **contextual_completeness**: Whether the evidence provides sufficient background and nuance to fully support or refute the statement.
### Strict Guidelines
* **Neutrality**: In cases of insufficient or ambiguous evidence, assign a conservative score between 0.4 and 0.6. 
* **No Hallucinations**: Do not fabricate facts or assume information not explicitly present in the provided evidence. 
* **Avoid Extremes**: Unless the evidence is definitive and exhaustive, avoid 0.0 or 1.0 scores.
### Output Specification
1.  **Format**: You must strictly output a valid JSON object.
2.  **Indexing**: The Keys in your JSON must exactly match the numeric indices of the input statements.
3.  **Structure**: Each Value must contain the three scoring dimensions listed above.
### Example Output
{
  "0": {
    "factual_accuracy": 0.85,
    "evidence_relevance": 0.90,
    "contextual_completeness": 0.75
  },
  "1": {
    "factual_accuracy": 0.50,
    "evidence_relevance": 0.45,
    "contextual_completeness": 0.40
  }
}"""
        input_dict = {i: c for i, c in enumerate(claims)}
        messages = [{
            "role": "user", 
            "content": f"#### Meme Description:\n{meme_content}\n\n#### Web Search Evidence:\n{evidence}\n\n## Please evaluate the following fact statements:\n{json.dumps(input_dict, ensure_ascii=False)}"
        }]
        response = self.llm.call_llm(system_prompt, messages, max_tokens=2000)
        try:
            score_data = json_repair.loads(response.strip())
        except Exception as e:
            print(f"[⚠️ AFU 评分异常] {e}")
            ##全都给默认分
            score_data = {str(i): {"factual_accuracy": 0.5, "evidence_relevance": 0.5, "contextual_completeness": 0.5} for i in range(len(claims))}
        for i in range(len(claims)):
            if str(i) not in score_data:
                score_data[str(i)] = {"factual_accuracy": 0.5, "evidence_relevance": 0.5, "contextual_completeness": 0.5}
        return score_data
    def _batch_decompose_claims(self, claims: List[str], meme_content: str = None) -> Dict[int, List[str]]:
        """
        通过显式 ID 映射分解主张
        返回格式: {0: ["AFU_1", "AFU_2"], 1: ["AFU_3"]}
        """
        if not claims: return {}
        claims_dict = {i: c for i, c in enumerate(claims)}
        system_prompt = """You are a professional Fact Decomposition and Verifiability Extraction Expert, specializing in debate and argumentation scenarios.
### Mission Goal
You will receive a JSON object where the Key is an Argument ID and the Value is the argument text. 
Your task: For each argument, decompose it into 1-2 objective "fact units" that MUST be verified through internet search to determine their truthfulness.
### Extraction Guidelines
✅ SHOULD EXTRACT (Requires external verification):
- Specific Events: "The 2024 Paris Olympics opening ceremony was held on the Seine."
- Statistics/Data: "The global AI market size reached $150 billion in 2023."
- Policies/Regulations: "The EU AI Act officially entered into force on August 1, 2024."
- Actions of Persons/Organizations: "OpenAI released the GPT-4o model."
- Scientific Conclusions: "mRNA vaccines stimulate an immune response by inducing cells to produce antigen proteins."
❌ SHOULD NOT EXTRACT (No/Cannot be verified via web):
- Subjective Opinions: "This policy is very wise," "The argument lacks persuasiveness."
- Logical Reasoning: "If A is true, then B must occur."
- Value Judgments: "We should prioritize privacy over efficiency."
- Vague References: "The aforementioned phenomenon," "This practice," "This result."
### Core Rules
1. ID Conservation: The Keys in the output JSON must be strictly identical to the input; do not add, delete, or modify IDs.
2. Precision Limit: Extract only 1-2 core fact units per argument. Too many dilute the verification; too few may miss key info.
3. Atomicity: Each fact unit must be an independent, complete statement that can function as a standalone search query (not a fragment).
4. Zero Vague References: Forbidden to use "the event," "this data," or "the above." You must restore the full Entity + Predicate.
5. Output Format: Output ONLY a standard JSON object. No Markdown, no explanations, no extra fields.
### Example
Input:
{
  "0": "China's NEV sales accounted for 60% of the global total in 2023, proving our clear industrial lead as number one in the world.",
  "1": "If we continue to loosen restrictions on cross-border data flow, it will seriously threaten national security.",
  "2": "The Tesla Shanghai Gigafactory delivered its first batch of vehicles on December 30, 2019, two months ahead of schedule."
}
Output:
{
  "0": ["China's NEV sales accounted for 60% of the global total in 2023", "China ranks first in the world in the New Energy Vehicle sector"],
  "1": ["Loosening restrictions on cross-border data flow threatens national security"],
  "2": ["Tesla Shanghai Gigafactory delivered its first batch of vehicles on December 30, 2019", "Tesla Shanghai Gigafactory delivered its first vehicles two months ahead of the original plan"]
}"""
        messages = [{"role": "user", "content": f"请处理以下主张对象：\n{json.dumps(claims_dict, ensure_ascii=False)}"}]
        response = self.llm.call_llm(system_prompt, messages, max_tokens=2000)
        raw_result = json_repair.loads(response.strip())
        final_map = {}
        for i, original_claim in claims_dict.items():
            afus = raw_result.get(str(i)) or raw_result.get(i)
            if afus and isinstance(afus, list) and len(afus) > 0:
                final_map[i] = afus[:self.max_afus]
            else:
                print(f"[⚠️ ID {i} 校验失败] 使用原句兜底")
                final_map[i] = [original_claim]
        return final_map
    
    # ========== 📦 Batch 3: 批量事实验证 ==========
    
    def _batch_verify_afus(self, afu_items: list[dict], evidence: str, meme_content: str) -> list[dict]:
        """
        通过显式数字索引锚点校验，批量验证原子事实得分
        :param afu_items: [{'idx': 0, 'text': '...'}, {'idx': 1, 'text': '...'}, ...]
        """
        if not afu_items:
            return []
        if evidence=="[No evidence]":
            print("[⚠️ 无检索证据] 全部 AFU 默认中性分")
            return [{
                'idx': item['idx'],
                'text': item.get('text', ''),
                'factual_accuracy': 0.5, 
                'evidence_relevance': 0.5, 
                'contextual_completeness': 0.5
            } for item in afu_items]
        input_dict = {item['idx']: item['text'] for item in afu_items}
        system_prompt = """你是一个严谨的事实核查专家。
    任务：请依据提供的"网络搜索证据"和模因内容描述，为输入的每个"事实陈述"输出三维得分。
    【评分维度】(0.0-1.0)
    • factual_accuracy: 内容与权威事实的符合程度
    • evidence_relevance: 证据与陈述的直接关联性
    • contextual_completeness: 证据是否提供充分背景
    【特别注意】
    证据不足时给 0.4-0.6 保守分，不要臆造，不要极端。
    【输出要求】
    1. 严格输出 JSON 对象，Key 必须与输入的数字索引完全一致。
    2. 每个 Value 包含上述三个得分维度。
    示例输出：{"0": {"factual_accuracy": 0.9, ...}, "1": {...}}"""
        messages = [{
            "role": "user", 
            "content": f"####模因内容描述：\n{meme_content}\n\n####网络搜索证据：\n{evidence}\n\n##请核查以下事实对象：\n{json.dumps(input_dict, ensure_ascii=False)}"
        }]
        response = self.llm.call_llm(system_prompt, messages, max_tokens=2000)
        raw_result = json_repair.loads(response.strip())
        final_results = []
        for item in afu_items:
            curr_idx = item['idx']
            scores = raw_result.get(str(curr_idx)) or raw_result.get(curr_idx)
            if isinstance(scores, dict):
                dims = ['factual_accuracy', 'evidence_relevance', 'contextual_completeness']
                final_results.append({
                    'idx': curr_idx,
                    'text': item.get('text', ''),
                    **{d: max(0.0, min(1.0, float(scores.get(d, 0.5)))) for d in dims}
                })
            else:
                print(f"[⚠️ 验证索引 {curr_idx} 缺失] 已自动补全默认分")
                final_results.append({
                    'idx': curr_idx,
                    'text': item.get('text', ''),
                    'factual_accuracy': 0.5, 'evidence_relevance': 0.5, 'contextual_completeness': 0.5
                })
        return final_results
    
    @staticmethod
    def _geo_mean(values: List[float]) -> float:
        """几何平均"""
        if not values:
            return 0.5
        safe = [max(v, 0.01) for v in values]
        return math.exp(sum(math.log(v) for v in safe) / len(safe))
    
    def _aggregate_claim_score(self, afu_scores: List[Dict]) -> float:
        """聚合 AFU 得分→claim 可信度"""
        if not afu_scores:
            return 0.0
        dim_scores = list(afu_scores.values())
        return round(sum(dim_scores) / len(dim_scores), 4)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """单条文本关键词提取"""
        system_prompt = """You are an information retrieval expert specializing in multimodal content understanding. Your task is to analyze the description of a meme and generate search queries related to the underlying background events.
### Mission Goal
Identify and extract 2-3 highly recognizable core background events from the provided meme description to facilitate factual verification or harm assessment.
### Extraction Guidelines
1. **Event Priority**: Precisely target names of people, locations, organizations, legal acts, or pivotal historical moments.
2. **Abstract to Concrete**: If the content contains metaphors or satire, extract the actual social controversies, news incidents, or cultural backgrounds it references.
3. **Search-Friendly**: Queries must be comprehensive, containing specific subject-verb-object information to ensure search engines can directly locate the relevant event.
4. **Specificity Over Brevity**: Each generated search query should be sufficiently detailed and descriptive rather than a short keyword.
### Output Specification
- You must strictly adhere to a JSON array format. 
- Do not include any explanatory text, preambles, or content outside of the Markdown code block.
- Each element must be a string.
### Example
Input: The image shows a man waving a flag at a rally with the 2021 Capitol riot in the background; the text implies this was due to election fraud.
Output: ["2021 United States Capitol attack", "2021 US presidential election fraud allegations", "January 6th United States Capitol rally"]"""
        messages = [{"role": "user", "content": f"Please extract keywords for the following text:\n{text[:500]}"}]
        try:
            response = self.llm.call_llm(system_prompt, messages, max_tokens=500)
            return response
        except Exception as e:
            print(f"[⚠️ 关键词提取失败] {e}")
            return [text[:20].strip()]
    # ========== 🎯 核心接口 ==========
    def _batch_evaluate_claims(self, claims: list[str],meme_content:str) -> list[dict]:
        if not claims:
            return []
        print("🔍 关键词抽取...")
        # id_to_afus = self._batch_decompose_claims(claims,meme_content)
        # flat_afus = []
        # for c_id in range(len(claims)):
        #     afus = id_to_afus.get(c_id) or id_to_afus.get(str(c_id)) or [claims[c_id]]
        #     for text in afus:
        #         flat_afus.append({
        #             'claim_id': c_id,  # 原始 claim 的索引
        #             'text': text, 
        #             'idx': len(flat_afus) # 当前 AFU 的绝对索引，给验证环节用
        #         })
        # if not flat_afus:
        #     return [{'claim': c, 'credibility_score': 0.5, 'is_reliable': False} for c in claims]
        search_query = self._extract_keywords(meme_content)
        print(f"🔍 网络证据检索")
        evidence,search_result = self._get_wikipedia_evidence(search_query)
        evi_scores = self._batch_claims_score(claims, meme_content,evidence)
        # scores_list = self._batch_verify_afus(flat_afus, evidence,meme_content)
        # claim_buckets = {i: [] for i in range(len(claims))}
        # for i, score_obj in enumerate(scores_list):
        #     c_id = flat_afus[i]['claim_id']
        #     claim_buckets[c_id].append(score_obj)
        # results = []
        cred_scores = []
        for i, original_claim in enumerate(claims):
            scores = evi_scores.get(str(i), [])
            if scores:
                cred_score = self._aggregate_claim_score(scores)
            else:
                cred_score = 0.5
            cred_scores.append(cred_score)
        result = {
            'search_result':search_result,
            'evi_scores': evi_scores,
            'cred_scores':cred_scores
        }
        return result
    
if __name__ == "__main__":
    llm = LLMTool(
        model_name=MODEL_NAME, 
        api_key=OPENAI_API_KEY, 
        base_url=OPENAI_API_BASE,
    )
    ffv = FactFilterVerificationModule(llm_tool=llm, threshold=0.65)
    print("=== 首次运行 ===")
    result = ffv._batch_evaluate_claims(["疫苗接种会导致自闭症","接种疫苗会降低抵抗力"])
    for r in result:
        print(f"Claim: {r['claim']}\nScore: {r['credibility_score']}\nReliable: {r['is_reliable']}\n")