from typing import Dict, Any, List
from services.database_service import DatabaseService
from services.nl2sql_service import NL2SQLService
from config import Config

class QueryService:
  """查询服务类"""
  
  def __init__(self, db_service: DatabaseService, nl2sql_service: NL2SQLService):
    self.db_service = db_service
    self.nl2sql_service = nl2sql_service

  def execute_query(self, natural_language: str, show_sql: bool = True) -> Dict[str, Any]:
    """执行自然语言查询"""
    try:
      # 转换为SQL
      sql = self.nl2sql_service.convert_to_sql(natural_language)
      
      # 执行查询
      results = self.db_service.execute_query(sql)
      
      # 限制结果集大小
      if len(results) > Config.MAX_RESULT_SIZE:
        results = results[:Config.MAX_RESULT_SIZE]
      
      # 提取列名
      columns = []
      if results:
        columns = list(results[0].keys())
      
      # 构建返回结果
      result = {
        'success': True,
        'data': results,
        'columns': columns,
        'message': '查询成功',
      }
      
      if show_sql:
        result['sql'] = sql
      
      return result
      
    except Exception as e:
      return {
        'success': False,
        'message': str(e),
        'data': [],
        'columns': [],
      }

