import os
import base64
import mimetypes
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASE,TEMPERATURE
import requests
from tavily import TavilyClient
class LLMTool:
    """封装LLM调用工具，替代原有的Agent类"""
    
    def __init__(self, model_name: str, temperature: float = TEMPERATURE):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        self.model_name = model_name
        self.temperature = temperature
    
    def call_llm(self, system_prompt: str, messages: list, max_tokens: int = 1024, 
                temperature: float = None, meme_src: str = None) -> str:
        """调用LLM，支持多模态输入"""
        #print(f"Using model: {self.model_name}")
        # 准备消息内容
        content = []
        
        # 添加文本内容
        user_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
        content.append({"type": "text", "text": user_text})
        
        # 添加图像（如果提供）
        if meme_src:
            if meme_src.startswith(("http://", "https://")):
                image_url = meme_src
            else:
                mime_type, _ = mimetypes.guess_type(meme_src)
                with open(meme_src, "rb") as f:
                    b64_image = base64.b64encode(f.read()).decode('utf-8')
                image_url = f"data:{mime_type};base64,{b64_image}"
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        
        # 构建完整消息
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages[:-1],  # 保留历史消息
            {"role": "user", "content": content}
        ]
        
        # 调用API
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
import requests

class SearchTool:
    """封装搜索工具"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    def search(self, query: str) -> str:
# To install: pip install tavily-python
        client = TavilyClient(self.api_key)
        response = client.search(
            query=query,
            search_depth="advanced" #advanced basic
        )
        return response

if __name__ == "__main__":
    # 测试搜索工具
    search_tool = SearchTool(api_key="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")
    results = search_tool.search("enough is enough children are more important than freaks")
    print(results)
