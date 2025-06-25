"""
查询分析模块，用于分析用户输入的科学问题，并生成检索关键词
"""

from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.models import DeepSeekModel, ModelFactory
from camel.types import ModelPlatformType, ModelType
from camel.configs import DeepSeekConfig
import re
import json
import logging

# from ..config import MODEL_CONFIG, SYSTEM_PROMPTS
MODEL_CONFIG = {
    "model_name": "deepseek",  # 可替换为其他模型
    "temperature": 0.2,
    "max_tokens": 1000
}
SYSTEM_PROMPTS = {
    "query_analyzer": """你是一个专业的科学问题分析助手。你的任务是:
1. 理解用户提出的科学问题
2. 确定相关的研究领域和子领域
3. 提取最适合用于论文检索的关键词3~5个""",
    
    "paper_analyzer": """你是一个专业的科学论文分析助手。你的任务是:
1. 仔细阅读提供的科学论文内容
2. 提取关键发现、方法和结论
3. 评估论文的相关性和重要性
4. 生成简洁但信息丰富的总结""",
    
    "review_generator": """你是一个专业的科学综述生成助手。你的任务是:
1. 基于多篇论文的分析结果
2. 组织一个结构良好的科学综述
3. 突出关键的研究进展、方法和发现
4. 指出研究差距和未来方向
5. 确保综述客观、全面且有深度"""
}


logger = logging.getLogger(__name__)
logging.root.setLevel(logging.INFO)

class QueryAnalyzer:
    def __init__(self, model_name=None):
        self.model_name = model_name or MODEL_CONFIG["model_name"]
        
        self.model = ModelFactory.create(
            model_platform=self.model_name,
            model_type=ModelType.DEEPSEEK_CHAT,
            model_config_dict=DeepSeekConfig(
                            temperature=1,
                            max_tokens=4028
            ).as_dict()
        )
        
        self.agent = ChatAgent(
            system_message=SYSTEM_PROMPTS["query_analyzer"],
            model=self.model
        )
        
        logger.info(f"查询分析器使用模型: {self.model_name}")
    
    def analyze(self, query):
        logger.info(f"用户想查询的科学问题: {query}")
        
#         prompt = f"""
# 请分析以下科学问题:

# {query}

# 请提供以下信息:
# 1. 主要研究领域和子领域
# 2. 用于检索论文的关键词（英文）
# 3. 可能相关的研究方法或技术

# 以JSON格式输出结果:
# {{
#     "keywords": ["关键词1", "关键词2", "关键词3"],
#     "research_area": "研究领域",
#     "methods": "研究方法",
# }}
# """

        prompt = f"""
请分析以下科学问题:

{query}

请提供以下信息:
1. 主要研究领域和子领域
2. 用于检索论文的关键词（英文）
3. 可能相关的研究方法或技术
"""
        
        response = self.agent.step(prompt)
        
        try:
            import json
            result = self._extract_json(response.msg.content)
            logger.info(f"分析完成，关键词数量: {len(result.get('keywords', []))}")
            return result
        except Exception as e:
            logger.error(f"Error parsing analysis result: {e}")
            return {
                "keywords": self._extract_keywords(response.msg.content),
                "research_area": self._extract_field(response.msg.content, "研究领域", "research area"),
                "raw_response": response.msg.content
            }
    
    def _extract_json(self, text):
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}', text)
        if json_match:
            json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
            return json.loads(json_str)
        
        result = {}
        result["keywords"] = self._extract_keywords(text)
        result["research_area"] = self._extract_field(text, "研究领域", "research area")
        result["methods"] = self._extract_field(text, "研究方法", "methods")
        result["strategy"] = self._extract_field(text, "检索策略", "strategy")
        result["raw_response"] = text
        
        return result
    
    def _extract_keywords(self, text):
        keywords_match = re.search(r'关键词[：:]\s*([\s\S]*?)(?:\n\n|\n\d\.|\Z)', text, re.IGNORECASE) or \
                         re.search(r'keywords[：:]\s*([\s\S]*?)(?:\n\n|\n\d\.|\Z)', text, re.IGNORECASE)
        
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            keywords = re.split(r'[,，、;\n]+', keywords_text)
            return [k.strip() for k in keywords if k.strip()]
        
        keywords = re.findall(r'"([^"]+)"', text) or re.findall(r"'([^']+)'", text)
        if keywords:
            return list(set(keywords))
            
        return []
    
    def _extract_field(self, text, cn_field, en_field):
        field_match = re.search(f'{cn_field}[：:]\s*([\s\S]*?)(?:\n\n|\n\d\.|\Z)', text, re.IGNORECASE) or \
                      re.search(f'{en_field}[：:]\s*([\s\S]*?)(?:\n\n|\n\d\.|\Z)', text, re.IGNORECASE)
        
        if field_match:
            return field_match.group(1).strip()
        
        return "" 

if __name__ == "__main__":
    analyzer = QueryAnalyzer()
    result = analyzer.analyze("如何提高大模型在科学问题分析中的准确性？")
    print(result)