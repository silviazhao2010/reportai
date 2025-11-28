import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from services.database_service import DatabaseService

class ReportService:
  """报表服务类，负责报表配置的CRUD操作"""
  
  def __init__(self, db_service: DatabaseService):
    self.db_service = db_service
  
  def create_report(self, name: str, description: str, data_source: str, 
                   layout_config: Dict[str, Any], query_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """创建报表配置"""
    try:
      # 验证数据源
      if not data_source:
        raise Exception('数据源不能为空')
      
      # 验证布局配置
      if not layout_config:
        raise Exception('布局配置不能为空')
      
      # 将配置转换为JSON字符串
      layout_json = json.dumps(layout_config, ensure_ascii=False)
      query_json = json.dumps(query_config, ensure_ascii=False) if query_config else None
      
      # 插入数据库
      sql = """
        INSERT INTO report_configs (name, description, data_source, layout_config, query_config, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      """
      connection = self.db_service.get_connection()
      cursor = connection.cursor()
      now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      cursor.execute(sql, (name, description, data_source, layout_json, query_json, now, now,))
      connection.commit()
      report_id = cursor.lastrowid
      cursor.close()
      
      return {
        'id': report_id,
        'name': name,
        'description': description,
        'data_source': data_source,
        'layout_config': layout_config,
        'query_config': query_config,
        'created_at': now,
        'updated_at': now,
      }
    except Exception as e:
      raise Exception(f'创建报表失败: {str(e)}')
  
  def get_report(self, report_id: int) -> Optional[Dict[str, Any]]:
    """获取报表配置"""
    try:
      sql = """
        SELECT id, name, description, data_source, layout_config, query_config, created_at, updated_at
        FROM report_configs
        WHERE id = ?
      """
      results = self.db_service.execute_query(sql, (report_id,))
      if not results:
        return None
      
      report = results[0]
      # 解析JSON配置
      report['layout_config'] = json.loads(report['layout_config']) if report['layout_config'] else {}
      report['query_config'] = json.loads(report['query_config']) if report['query_config'] else None
      
      return report
    except Exception as e:
      raise Exception(f'获取报表失败: {str(e)}')
  
  def list_reports(self) -> List[Dict[str, Any]]:
    """获取所有报表配置列表"""
    try:
      sql = """
        SELECT id, name, description, data_source, created_at, updated_at
        FROM report_configs
        ORDER BY updated_at DESC
      """
      return self.db_service.execute_query(sql)
    except Exception as e:
      raise Exception(f'获取报表列表失败: {str(e)}')
  
  def update_report(self, report_id: int, name: str = None, description: str = None,
                   layout_config: Dict[str, Any] = None, query_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """更新报表配置"""
    try:
      # 获取现有报表
      existing = self.get_report(report_id)
      if not existing:
        raise Exception('报表不存在')
      
      # 构建更新SQL
      updates = []
      params = []
      
      if name is not None:
        updates.append('name = ?')
        params.append(name)
      
      if description is not None:
        updates.append('description = ?')
        params.append(description)
      
      if layout_config is not None:
        updates.append('layout_config = ?')
        params.append(json.dumps(layout_config, ensure_ascii=False))
      
      if query_config is not None:
        updates.append('query_config = ?')
        params.append(json.dumps(query_config, ensure_ascii=False))
      
      if not updates:
        return existing
      
      # 更新更新时间
      updates.append('updated_at = ?')
      params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
      params.append(report_id)
      
      sql = f"UPDATE report_configs SET {', '.join(updates)} WHERE id = ?"
      connection = self.db_service.get_connection()
      cursor = connection.cursor()
      cursor.execute(sql, params)
      connection.commit()
      cursor.close()
      
      # 返回更新后的报表
      return self.get_report(report_id)
    except Exception as e:
      raise Exception(f'更新报表失败: {str(e)}')
  
  def delete_report(self, report_id: int) -> bool:
    """删除报表配置"""
    try:
      sql = "DELETE FROM report_configs WHERE id = ?"
      connection = self.db_service.get_connection()
      cursor = connection.cursor()
      cursor.execute(sql, (report_id,))
      connection.commit()
      deleted = cursor.rowcount > 0
      cursor.close()
      return deleted
    except Exception as e:
      raise Exception(f'删除报表失败: {str(e)}')
  
  def execute_report_query(self, query_config: Dict[str, Any]) -> Dict[str, Any]:
    """执行报表查询，根据查询配置生成SQL并执行"""
    try:
      # 构建SQL查询
      tables = query_config.get('tables', [])
      fields = query_config.get('fields', [])
      filters = query_config.get('filters', [])
      group_by = query_config.get('group_by', [])
      order_by = query_config.get('order_by', [])
      
      if not tables or not fields:
        raise Exception('表和字段不能为空')
      
      # 构建SELECT子句
      select_fields = []
      for field in fields:
        table_name = field.get('table')
        field_name = field.get('field')
        alias = field.get('alias', field_name)
        if table_name:
          select_fields.append(f"{table_name}.{field_name} AS {alias}")
        else:
          select_fields.append(f"{field_name} AS {alias}")
      
      # 构建FROM子句
      from_clause = ', '.join(tables)
      
      # 构建WHERE子句
      where_clause = ''
      where_params = []
      if filters:
        where_conditions = []
        for filter_item in filters:
          field = filter_item.get('field')
          operator = filter_item.get('operator', '=')
          value = filter_item.get('value')
          if field and value is not None:
            where_conditions.append(f"{field} {operator} ?")
            where_params.append(value)
        if where_conditions:
          where_clause = 'WHERE ' + ' AND '.join(where_conditions)
      
      # 构建GROUP BY子句
      group_by_clause = ''
      if group_by:
        group_by_clause = 'GROUP BY ' + ', '.join(group_by)
      
      # 构建ORDER BY子句
      order_by_clause = ''
      if order_by:
        order_by_items = []
        for order_item in order_by:
          field = order_item.get('field')
          direction = order_item.get('direction', 'ASC')
          order_by_items.append(f"{field} {direction}")
        order_by_clause = 'ORDER BY ' + ', '.join(order_by_items)
      
      # 组合SQL
      sql = f"SELECT {', '.join(select_fields)} FROM {from_clause} {where_clause} {group_by_clause} {order_by_clause}"
      
      # 执行查询
      results = self.db_service.execute_query(sql, tuple(where_params) if where_params else None)
      
      # 获取列信息
      columns = []
      if results:
        columns = list(results[0].keys())
      
      return {
        'success': True,
        'data': results,
        'columns': columns,
        'sql': sql,
      }
    except Exception as e:
      return {
        'success': False,
        'message': f'查询执行失败: {str(e)}',
        'data': [],
        'columns': [],
      }

