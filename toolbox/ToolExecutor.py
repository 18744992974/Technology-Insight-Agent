import json
import importlib.util
from typing import Dict, Any, Optional
from importlib.machinery import ModuleSpec

class ToolExecutor:
    def __init__(self, config_path: str = 'toolbox/tool_config.json'):
        """
        初始化工具执行器
        :param config_path: 工具配置文件的路径
        """
        self.config_path = config_path
        self.tools_config = self._load_config()
        
    def _load_config(self) -> list:
        """
        加载工具配置文件
        :return: 工具配置列表
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_tool_config(self, tool_id: int) -> Optional[Dict[str, Any]]:
        """
        根据工具ID获取工具配置
        :param tool_id: 工具ID
        :return: 工具配置信息，如果未找到则返回 None
        """
        for tool in self.tools_config:
            if tool['tool_id'] == tool_id:
                return tool
        return None
    
    def _validate_args(self, tool_config: Dict[str, Any], args: Dict[str, Any]) -> None:
        """
        验证参数是否符合工具配置要求
        :param tool_config: 工具配置
        :param args: 实际传入的参数
        :raises ValueError: 如果参数验证失败
        """
        required_args = tool_config['args']
        
        # 必需的不缺
        for arg in required_args:
            if arg not in args:
                raise ValueError(f"缺少必需参数：{arg}")
        
        # 多余的没有
        for arg in args:
            if arg not in required_args:
                raise ValueError(f"未知参数：{arg}")
    
    def execute(self, tool_call: Dict[str, Any]) -> Any:
        """
        执行工具调用
        :param tool_call: 工具调用请求，格式如：
                         {'tool_id': 1, 'args': {'digit1': 12, 'digit2': 15, 'digit3': 9}}
        :return: 工具执行结果
        :raises ValueError: 如果工具ID无效或参数验证失败
        :raises ImportError: 如果工具模块导入失败
        """

        tool_config = self._get_tool_config(tool_call['tool_id'])
        if not tool_config:
            raise ValueError(f"找不到 ID 为 {tool_call['tool_id']} 的工具")
        
        self._validate_args(tool_config, tool_call['args'])
        
        # 导入工具模块
        tool_name = tool_config['tool_name']
        module_path = f'toolbox/{tool_name}.py'
        spec = importlib.util.spec_from_file_location(tool_name, module_path)
        
        if spec is None or spec.loader is None:
            raise ImportError(f"无法加载工具模块：{module_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 获取工具函数
        tool_func = getattr(module, tool_name)
        
        return tool_func(**tool_call['args'])



# 创建全局工具执行器实例
executor = ToolExecutor()

def execute_tool_call(tool_call: Dict[str, Any]) -> Any:
    """
    执行工具调用的便捷函数
    :param tool_call: 工具调用请求
    :return: 工具执行结果
    """
    return executor.execute(tool_call)
