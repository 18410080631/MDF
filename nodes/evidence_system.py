# evidence_system.py —— 全部改为同步！

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import quote
from tools import LLMTool
from config import TEMPERATURE,MODEL_NAME
from ddgs import DDGS
import re
from typing import Optional, Dict
from tenacity import retry, stop_after_attempt, wait_exponential


class EvidenceSystem:
    def __init__(self, model_name: str = MODEL_NAME, temperature: float = TEMPERATURE):
        self.temperature = temperature
        self.llm_tool = LLMTool(model_name=model_name, temperature=temperature)

    def extract_keywords(self, meme_text: str) -> List[str]:
        prompt_pos = f"You are an expert in generating search terms. Your task is to generate 3–5 search terms for the following meme text that can help retrieve encyclopedia pages supporting the meme’s content as harmless, reasonable, or grounded in cultural or social context.Meme text: {meme_text}.Please generate search terms that facilitate finding relevant positive or neutral background information. Return only the terms, separated by commas, in the following format: term1, term2, term3"
        prompt_neg = f"You are an expert in generating search terms. Your task is to generate 3–5 search terms for the following meme text that can help retrieve encyclopedia pages supporting the meme’s content as harmful, misleading, or lacking cultural or social context.Meme text: {meme_text}.Please generate search terms that facilitate finding relevant negative or critical background information. Return only the terms, separated by commas, in the following format: term1, term2, term3"
        #prompt = f"从以下文本中提取3-5个可用于维基百科搜索的关键词：\n文本: \"{meme_text}\"\n\n返回格式: 关键词1, 关键词2, 关键词3"
        try:
            response_pos = self.llm_tool.call_llm(
                system_prompt="You are a keyword expert.",
                messages=[{"role": "user", "content": prompt_pos}],
                temperature=self.temperature,
                max_tokens=128
            )
            keywords_pos = [k.strip() for k in response_pos.split(",") if k.strip()]
            response_neg = self.llm_tool.call_llm(
                system_prompt="You are a keyword expert.",
                messages=[{"role": "user", "content": prompt_neg}],
                temperature=self.temperature,
                max_tokens=128
            )
            keywords_neg = [k.strip() for k in response_neg.split(",") if k.strip()]        
            return list(set(keywords_pos + keywords_neg))[:5]
        except Exception as e:
            print(f"[⚠️ Keyword extraction failed] {e}")
            words = re.findall(r'\b\w+\b', meme_text.lower())
            return list(set(word for word in words if len(word) > 3))[:5]



    def search_wikipedia(self, keywords: List[str]) -> List[Optional[Dict]]:
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        def _search_single(keyword: str) -> Optional[Dict]:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(keyword, max_results=3, region='wt-wt'))
                if not results:
                    print(f"    🔍 No result found for '{keyword}'")
                    return None
                result = results[0]
                return {
                    'title': result.get('title', keyword),
                    'extract': result.get('body', ''),
                    'url': result.get('href', ''),
                    'keyword': keyword
                }
            except Exception as e:
                print(f"    ❌ Error searching for '{keyword}': {e}")
                return None
        results = [None] * len(keywords)
        with ThreadPoolExecutor(max_workers=min(5, len(keywords) or 1)) as executor:
            future_to_index = {
                executor.submit(_search_single, kw): idx
                for idx, kw in enumerate(keywords)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    print(f"    ❌ Unexpected error in thread: {e}")
                    results[idx] = None
        return results

    def analyze_evidence_stance(self, evidence: Dict[str, Any], meme_text: str) -> str:
        prompt = f"""
        分析以下证据是否支持"该meme是有害的"这一主张：
        Meme文本: "{meme_text}"
        证据标题: {evidence.get('title', '')}
        证据摘要: {evidence.get('extract', '')}
        返回: SUPPORTS_TRUE / SUPPORTS_FALSE / NEUTRAL
        """
        try:
            response = self.llm_tool.call_llm(
                system_prompt="You are an impartial fact-checker.",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=64
            )
            stance = response.strip().upper()
            print(f"    🧐 Stance analysis result: {stance}")
            if 'SUPPORTS_TRUE' in stance:
                return 'SUPPORTS_TRUE'
            elif 'SUPPORTS_FALSE' in stance:
                return 'SUPPORTS_FALSE'
            else:
                return 'NEUTRAL'
        except Exception as e:
            print(f"[⚠️ Stance analysis failed] {e}")
            return 'NEUTRAL'

    def gather_evidence(self, keywords: str, meme_src: Optional[str] = None) -> Dict[str, Any]:
        print(f"  🌐 搜索: {keywords}")
        wiki_result = self.search_wikipedia(keywords)
        if not wiki_result:
            wiki_result = {}
        return {
            "evidence": wiki_result
        }

    # 保留兼容接口
    def filter_evidence_by_stance(self, evidence_data: Dict, target_stance: str) -> Dict:
        if target_stance == 'SUPPORTS_TRUE':
            evidence = evidence_data.get("affirmative_evidence", {})
        elif target_stance == 'SUPPORTS_FALSE':
            evidence = evidence_data.get("negative_evidence", {})
        else:
            evidence = {k: v for k, v in evidence_data["evidence"].items() if v.get("stance") == "NEUTRAL"}
        return {"keywords": evidence_data["keywords"], "evidence": evidence}

    def has_favorable_evidence(self, evidence_dict: Dict, target_stance: str) -> bool:
        return len(evidence_dict.get("evidence", {})) > 0

    def format_evidence_for_debate(self, evidence_data: Dict) -> str:
        if not evidence_data or not evidence_data.get("evidence"):
            return "No relevant evidence found."
        lines = []
        for kw, info in evidence_data["evidence"].items():
            stance = info.get("stance", "NEUTRAL")
            lines.append(f"[{stance}] {info['title']}: {info['extract'][:150]}...")
        return "\n".join(lines)