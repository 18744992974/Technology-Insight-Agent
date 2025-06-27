import json
import requests
from typing import Dict, Any, List, Optional
from agents.Agent import Agent

class DeepseekAgent(Agent):
    def __init__(self, api_key: str, model_type: str = "deepseek-chat"):
        """
        初始化 Deepseek API 客户端
        :param api_key: API密钥
        :param model_type: 模型类型
        """
        self.api_key = api_key
        self.model_type = model_type
        self.api_base = "https://api.deepseek.com/v1"
        
    def _send_requests(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送请求到 Deepseek API
        :param endpoint: API端点
        :param payload: 请求负载
        :return: API响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{self.api_base}/{endpoint}",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API请求失败: {response.text}")
            
        return response.json()
    
    def _chat(self, messages: List[Dict[str, str]]) -> str:
        """
        调用 Deepseek Chat API
        :param messages: 对话消息列表
        :return: 模型回复的内容
        """
        payload = {
            "model": self.model_type,
            "messages": messages
        }
        
        response = self._send_requests("chat/completions", payload)
        return response["choices"][0]["message"]["content"]