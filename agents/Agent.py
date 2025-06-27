import json
import requests
from typing import Dict, Any, List, Optional
from toolbox.ToolExecutor import execute_tool_call

class Agent:
    def __init__(self):
        return
    def _chat(self, messages: List[Dict[str, str]]) -> str:
        response = '...'
        return response

    def create_tool_selection_prompt(self, tools_config: List[Dict[str, Any]], user_query: str) -> str:
        """
        创建用于工具选择的提示词
        :param tools_config: 工具配置列表
        :param user_query: 用户查询
        :return: 格式化的提示词
        """
        tools_description = ""
        for tool in tools_config:
            tools_description += f"工具ID: {tool['tool_id']}\n"
            tools_description += f"工具名称: {tool['tool_name']}\n"
            tools_description += f"工具描述: {tool.get('description', '无描述')}\n"
            tools_description += f"参数列表: {', '.join(tool['args'])}\n"
            tools_description += "参数说明:\n"
            for arg, desc in tool.get('arg_descriptions', {}).items():
                tools_description += f"  - {arg}: {desc}\n"
            tools_description += "\n"

        prompt = f"""作为一个AI助手，你的任务是分析用户的需求，并选择合适的工具来完成任务。
可用的工具列表：
{tools_description}

用户的需求是：{user_query}

请分析用户的需求，并按照以下JSON格式返回工具调用信息（如果找到合适的工具）：
{{
    "tool_id": <工具ID>,
    "args": {{
        "参数名1": 参数值1,
        "参数名2": 参数值2,
        ...
    }}
}}

如果没有找到合适的工具，请返回 null。

请只返回JSON格式的结果，不要包含任何其他解释或说明。"""
        return prompt

    def parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:

        try:
            result = json.loads(response.strip())
            return result
        except json.JSONDecodeError:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        return None 

    def load_tool_config(self):
        """加载工具配置文件"""
        with open('toolbox/tool_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_tool_selection(self, user_query: str):
        """
        让大语言模型选择合适的工具
        :param user_query: 用户查询
        :return: 工具调用信息或 None
        """
        tools_config = self.load_tool_config()
        prompt = self.create_tool_selection_prompt(tools_config, user_query)
    
        messages = [{"role": "user", "content": prompt}]
        response = self._chat(messages)
    
        return self.parse_llm_response(response)

    def give_final_answer(self, user_query: str):
        """
        让大语言模型生成最终答案
        :param user_query: 用户查询
        :return: 最终答案
        """

        tool_call = self.get_tool_selection(user_query)
        if tool_call:
            print(f"\n大语言模型决定调用的工具：")
            print(json.dumps(tool_call, ensure_ascii=False, indent=2))
        
            try:
                result = execute_tool_call(tool_call)
                print(f"\n工具调用的结果：{result}")
            
                # 让大语言模型生成最终答案
                final_prompt = f"""用户的问题是：{user_query}
工具返回的结果是：{result}
请结合结果为用户生成一个友好的回答。"""
            
                messages = [{"role": "user", "content": final_prompt}]
                final_answer = self._chat(messages)
                print(f"\n最终答案：{final_answer}")
            
            except Exception as e:
                print(f"\n工具调用出错：{str(e)}")
        else:
            print("\n大语言模型未找到合适的工具来处理该请求")