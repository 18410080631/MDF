#tools.py
import os
import base64
import mimetypes
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASE,TEMPERATURE
import requests
from tavily import TavilyClient
import time
class LLMTool:
    """封装LLM调用工具，替代原有的Agent类"""
    
    def __init__(self, model_name: str, temperature: float = TEMPERATURE):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_API_BASE
        )
        self.model_name = model_name
        self.temperature = temperature
    
    def call_llm(self, system_prompt: str, messages: list, max_tokens: int = 4096, 
                    temperature: float = 0.7, meme_src: str = None,
                    max_retries: int = 3, retry_delay: float = 1.0, 
                    request_timeout: float = 10.0) -> str: # 1. 增加超时参数
            """调用LLM，支持多模态输入 + 简单重试 + 超时控制"""

            # 准备消息内容
            content = []
            # 获取用户最新的文本消息（或者合并之前的对话）
            user_text = "\n".join([m["content"] for m in messages if m["role"] == "user"])
            content.append({"type": "text", "text": user_text})

            if meme_src:
                # ... (Base64 处理逻辑保持不变)
                if meme_src.startswith(("http://", "https://")):
                    image_url = meme_src
                else:
                    import mimetypes, base64, os
                    mime_type, _ = mimetypes.guess_type(meme_src)
                    if mime_type is None:
                        ext = os.path.splitext(meme_src)[1].lower()
                        mime_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png'}
                        mime_type = mime_map.get(ext, 'image/jpeg')
                    try:
                        with open(meme_src, "rb") as f:
                            b64_image = base64.b64encode(f.read()).decode('utf-8')
                        image_url = f"data:{mime_type};base64,{b64_image}"
                    except FileNotFoundError:
                        print(f"[⚠️ 警告] 图片文件不存在: {meme_src}")
                        image_url = None
                if image_url:
                    content.append({"type": "image_url", "image_url": {"url": image_url}})

            # 构造完整消息列表
            # 注意：这里假设最后一个 user 消息被替换为带图片的内容
            full_messages = [
                {"role": "system", "content": system_prompt},
                *messages[:-1],
                {"role": "user", "content": content}
            ]

            # 2. 重试逻辑 (包含超时捕获)
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    # 使用 timeout 参数控制 API 响应时间
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=request_timeout # 3. 关键设置
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    last_error = e
                    # 识别是否为超时错误 (OpenAI 会抛出 APITimeoutError)
                    error_type = "超时" if "timeout" in str(e).lower() else "异常"
                    if attempt < max_retries:
                        wait = retry_delay * (2 ** attempt) # 指数退避
                        print(f"⚠️ 第{attempt+1}次{error_type}: {e}，{wait}s后重试...")
                        import time
                        time.sleep(wait)
                    else:
                        print(f"❌ 重试{max_retries+1}次后仍失败，最后一次错误: {e}")
            raise last_error
    
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
