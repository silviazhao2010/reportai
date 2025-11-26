import json
import re
from typing import Dict, List, Any, Optional
import requests
from services.database_service import DatabaseService
from config import Config

class NL2SQLService:
  """NL2SQL转换服务 - 基于大模型"""
  
  def __init__(self, db_service: DatabaseService):
    self.db_service = db_service
    self.config = Config
    self.schema_info = self._load_schema_info()
  
  def _load_schema_info(self) -> Dict[str, Any]:
    """加载数据库schema信息，用于构建prompt"""
    schema = {
      'tables': [],
      'table_mapping': {},
      'column_mapping': {},
    }
    
    try:
      # 获取所有表
      tables = self.db_service.get_tables()
      for table in tables:
        table_name = table.get('name', '')
        natural_name = table.get('naturalName', '')
        description = table.get('description', '')
        
        if table_name:
          table_info = {
            'db_name': table_name,
            'natural_name': natural_name or table_name,
            'description': description,
            'columns': [],
          }
          
          # 获取表的字段信息
          columns = self.db_service.get_table_columns(table_name)
          for col in columns:
            col_name = col.get('name', '')
            col_natural_name = col.get('naturalName', '')
            col_type = col.get('type', '')
            col_desc = col.get('description', '')
            
            if col_name:
              column_info = {
                'db_name': col_name,
                'natural_name': col_natural_name or col_name,
                'type': col_type,
                'description': col_desc,
              }
              table_info['columns'].append(column_info)
              
              # 建立映射
              if col_natural_name:
                if table_name not in schema['column_mapping']:
                  schema['column_mapping'][table_name] = {}
                schema['column_mapping'][table_name][col_natural_name] = col_name
          
          schema['tables'].append(table_info)
          
          # 建立表名映射
          if natural_name:
            schema['table_mapping'][natural_name] = table_name
          schema['table_mapping'][table_name] = table_name
    except Exception as e:
      print(f'加载schema信息失败: {str(e)}')
    
    return schema
  
  def _build_schema_prompt(self) -> str:
    """构建数据库schema的prompt描述"""
    prompt_parts = ["数据库表结构信息：\n"]
    
    for table in self.schema_info['tables']:
      table_desc = f"表名: {table['db_name']}"
      if table['natural_name'] != table['db_name']:
        table_desc += f" (自然语言名称: {table['natural_name']})"
      if table['description']:
        table_desc += f" - {table['description']}"
      prompt_parts.append(table_desc)
      
      prompt_parts.append("字段列表:")
      for col in table['columns']:
        col_desc = f"  - {col['db_name']}"
        if col['natural_name'] != col['db_name']:
          col_desc += f" (自然语言名称: {col['natural_name']})"
        if col['type']:
          col_desc += f" 类型: {col['type']}"
        if col['description']:
          col_desc += f" - {col['description']}"
        prompt_parts.append(col_desc)
      prompt_parts.append("")
    
    return "\n".join(prompt_parts)
  
  def _build_system_prompt(self) -> str:
    """构建系统提示词"""
    schema_text = self._build_schema_prompt()
    
    return f"""你是一个专业的SQL生成助手。你的任务是根据用户的自然语言查询，生成准确的SQLite SQL语句。

{schema_text}

重要规则：
1. 只生成SELECT查询语句，不允许包含DROP、DELETE、UPDATE、INSERT等危险操作
2. 使用数据库中的实际表名和字段名（db_name），而不是自然语言名称
3. SQLite语法：使用?作为占位符，日期函数使用DATE()等SQLite函数
4. 只返回SQL语句，不要包含任何解释或markdown格式
5. 如果查询涉及多个表，使用JOIN连接
6. 确保SQL语法正确，可以直接执行
7. 对于模糊查询，使用LIKE操作符
8. 对于数值比较，使用标准的比较运算符（>, <, =, >=, <=）
9. 对于聚合查询，正确使用GROUP BY子句
10. 对于排序，使用ORDER BY子句

请根据用户的自然语言查询，生成对应的SQL语句。"""
  
  def _call_openai_api(self, user_query: str) -> str:
    """调用OpenAI API"""
    if not self.config.OPENAI_API_KEY:
      raise Exception('未配置OPENAI_API_KEY，请在环境变量中设置')
    
    headers = {
      'Authorization': f'Bearer {self.config.OPENAI_API_KEY}',
      'Content-Type': 'application/json',
    }
    
    data = {
      'model': self.config.OPENAI_MODEL,
      'messages': [
        {'role': 'system', 'content': self._build_system_prompt()},
        {'role': 'user', 'content': user_query},
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
        sql = result['choices'][0]['message']['content'].strip()
        # 清理可能的markdown代码块
        sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'^```\s*', '', sql)
        sql = re.sub(r'\s*```\s*$', '', sql)
        return sql.strip()
      else:
        raise Exception('API返回格式异常')
    except requests.exceptions.RequestException as e:
      raise Exception(f'调用OpenAI API失败: {str(e)}')
  
  def _call_qwen_api(self, user_query: str) -> str:
    """调用通义千问API"""
    if not self.config.DASHSCOPE_API_KEY:
      raise Exception('未配置DASHSCOPE_API_KEY，请在环境变量中设置')
    
    headers = {
      'Authorization': f'Bearer {self.config.DASHSCOPE_API_KEY}',
      'Content-Type': 'application/json',
    }
    
    data = {
      'model': self.config.QWEN_MODEL,
      'input': {
        'messages': [
          {'role': 'system', 'content': self._build_system_prompt()},
          {'role': 'user', 'content': user_query},
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
          sql = result['output']['choices'][0]['message']['content'].strip()
          # 清理可能的markdown代码块
          sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
          sql = re.sub(r'^```\s*', '', sql)
          sql = re.sub(r'\s*```\s*$', '', sql)
          return sql.strip()
      raise Exception('API返回格式异常')
    except requests.exceptions.RequestException as e:
      raise Exception(f'调用通义千问API失败: {str(e)}')
  
  def _call_llm_api(self, user_query: str) -> str:
    """根据配置调用对应的大模型API"""
    provider = self.config.LLM_PROVIDER.lower()
    
    if provider == 'openai':
      return self._call_openai_api(user_query)
    elif provider == 'qwen':
      return self._call_qwen_api(user_query)
    else:
      raise Exception(f'不支持的大模型提供商: {provider}，支持: openai, qwen')
  
  def _validate_sql(self, sql: str) -> None:
    """验证SQL安全性"""
    sql_upper = sql.upper().strip()
    
    # 检查是否包含禁止的关键字
    for keyword in self.config.FORBIDDEN_SQL_KEYWORDS:
      if keyword in sql_upper:
        raise Exception(f'生成的SQL包含禁止的关键字: {keyword}')
    
    # 检查是否以允许的关键字开头
    if not any(sql_upper.startswith(keyword) for keyword in self.config.ALLOWED_SQL_KEYWORDS):
      raise Exception('生成的SQL不是SELECT查询语句')
  
  def _clean_sql(self, sql: str) -> str:
    """清理和规范化SQL"""
    # 移除多余的空白
    sql = ' '.join(sql.split())
    
    # 确保SQLite兼容性：将MySQL的占位符转换为SQLite的?
    sql = sql.replace('%s', '?')
    
    return sql.strip()
  
  def convert_to_sql(self, natural_language: str) -> str:
    """将自然语言转换为SQL（使用大模型）"""
    if not natural_language or not natural_language.strip():
      raise Exception('自然语言查询不能为空')
    
    try:
      # 调用大模型API生成SQL
      sql = self._call_llm_api(natural_language.strip())
      
      # 验证SQL安全性
      self._validate_sql(sql)
      
      # 清理和规范化SQL
      sql = self._clean_sql(sql)
      
      return sql
    except Exception as e:
      raise Exception(f'NL2SQL转换失败: {str(e)}')
