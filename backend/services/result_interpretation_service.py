import json
import re
from typing import Dict, List, Any, Optional
import requests
from config import Config

class ResultInterpretationService:
  """报表结果解读服务 - 基于大模型"""
  
  def __init__(self):
    self.config = Config
  
  def _build_system_prompt(self) -> str:
    """构建系统提示词"""
    return """你是一个专业的数据分析师。你的任务是根据用户查询和查询结果，生成清晰、准确、有价值的数据解读。

解读要求：
1. 用简洁明了的语言总结查询结果的主要发现
2. 突出关键数据和趋势
3. 如果数据量较大，重点解读总体情况和主要特征
4. 如果涉及数值，提供具体的数值和比较
5. 如果涉及时间序列，描述趋势变化
6. 使用中文回答，语言要专业但易懂
7. 避免冗长的描述，重点突出核心洞察
8. 如果结果为空，说明可能的原因

请根据查询结果生成一段简洁的数据解读（建议100-300字）。"""
  
  def _format_data_for_prompt(self, data: List[Dict[str, Any]], columns: List[str], max_rows: int = 20) -> str:
    """格式化数据用于prompt"""
    if not data:
      return "查询结果为空，没有数据。"
    
    # 限制行数，避免prompt过长
    display_data = data[:max_rows]
    
    # 构建数据表格文本
    lines = []
    lines.append("查询结果数据：")
    lines.append("")
    
    # 表头
    header = " | ".join(columns)
    lines.append(header)
    lines.append("-" * len(header))
    
    # 数据行
    for row in display_data:
      row_values = []
      for col in columns:
        value = row.get(col, '')
        # 格式化值，避免过长
        value_str = str(value)
        if len(value_str) > 50:
          value_str = value_str[:47] + "..."
        row_values.append(value_str)
      lines.append(" | ".join(row_values))
    
    if len(data) > max_rows:
      lines.append(f"\n（共 {len(data)} 条记录，仅显示前 {max_rows} 条）")
    
    return "\n".join(lines)
  
  def _call_openai_api(self, user_query: str, data_text: str) -> str:
    """调用OpenAI API"""
    if not self.config.OPENAI_API_KEY:
      raise Exception('未配置OPENAI_API_KEY，请在环境变量中设置')
    
    headers = {
      'Authorization': f'Bearer {self.config.OPENAI_API_KEY}',
      'Content-Type': 'application/json',
    }
    
    prompt = f"""用户查询：{user_query}

{data_text}

请对以上查询结果进行专业的数据解读。"""
    
    data = {
      'model': self.config.OPENAI_MODEL,
      'messages': [
        {'role': 'system', 'content': self._build_system_prompt()},
        {'role': 'user', 'content': prompt},
      ],
      'temperature': self.config.OPENAI_TEMPERATURE,
      'max_tokens': self.config.OPENAI_MAX_TOKENS,
    }
    
    try:
      response = requests.post(
        f'{self.config.OPENAI_BASE_URL}/chat/completions',
        headers=headers,
        json=data,
        timeout=30,
      )
      response.raise_for_status()
      result = response.json()
      
      if 'choices' in result and len(result['choices']) > 0:
        interpretation = result['choices'][0]['message']['content'].strip()
        return interpretation
      else:
        raise Exception('API返回格式异常')
    except requests.exceptions.RequestException as e:
      raise Exception(f'调用OpenAI API失败: {str(e)}')
  
  def _call_qwen_api(self, user_query: str, data_text: str) -> str:
    """调用通义千问API"""
    if not self.config.DASHSCOPE_API_KEY:
      raise Exception('未配置DASHSCOPE_API_KEY，请在环境变量中设置')
    
    headers = {
      'Authorization': f'Bearer {self.config.DASHSCOPE_API_KEY}',
      'Content-Type': 'application/json',
    }
    
    prompt = f"""用户查询：{user_query}

{data_text}

请对以上查询结果进行专业的数据解读。"""
    
    data = {
      'model': self.config.QWEN_MODEL,
      'input': {
        'messages': [
          {'role': 'system', 'content': self._build_system_prompt()},
          {'role': 'user', 'content': prompt},
        ],
      },
      'parameters': {
        'temperature': self.config.OPENAI_TEMPERATURE,
        'max_tokens': self.config.OPENAI_MAX_TOKENS,
      },
    }
    
    try:
      response = requests.post(
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
        headers=headers,
        json=data,
        timeout=30,
      )
      response.raise_for_status()
      result = response.json()
      
      if 'output' in result and 'choices' in result['output']:
        if len(result['output']['choices']) > 0:
          interpretation = result['output']['choices'][0]['message']['content'].strip()
          return interpretation
      raise Exception('API返回格式异常')
    except requests.exceptions.RequestException as e:
      raise Exception(f'调用通义千问API失败: {str(e)}')
  
  def _call_llm_api(self, user_query: str, data_text: str) -> str:
    """根据配置调用对应的大模型API"""
    provider = self.config.LLM_PROVIDER.lower()
    
    if provider == 'openai':
      return self._call_openai_api(user_query, data_text)
    elif provider == 'qwen':
      return self._call_qwen_api(user_query, data_text)
    else:
      raise Exception(f'不支持的大模型提供商: {provider}，支持: openai, qwen')
  
  def interpret_result(self, user_query: str, data: List[Dict[str, Any]], columns: List[str]) -> Optional[str]:
    """解读查询结果"""
    try:
      # 格式化数据
      data_text = self._format_data_for_prompt(data, columns)
      
      # 调用大模型API生成解读
      interpretation = self._call_llm_api(user_query, data_text)
      
      return interpretation
    except Exception as e:
      # 解读失败不影响主流程，返回None
      print(f'结果解读失败: {str(e)}')
      return None

