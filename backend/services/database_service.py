import sqlite3
import os
from config import Config
from typing import List, Dict, Any

class DatabaseService:
  """数据库服务类"""
  
  def __init__(self):
    self.config = Config
    self.connection = None
    self._init_database()

  def _init_database(self):
    """初始化数据库，如果不存在则创建并执行初始化脚本"""
    db_path = self.config.DB_PATH
    db_dir = os.path.dirname(db_path)
    
    # 确保数据库目录存在
    if db_dir and not os.path.exists(db_dir):
      os.makedirs(db_dir, exist_ok=True)
    
    # 如果数据库文件不存在，执行初始化脚本
    if not os.path.exists(db_path):
      self._create_database()

  def _create_database(self):
    """创建数据库并执行初始化脚本"""
    init_sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'init.sql')
    
    if os.path.exists(init_sql_path):
      connection = sqlite3.connect(self.config.DB_PATH)
      try:
        with open(init_sql_path, 'r', encoding='utf-8') as f:
          sql_script = f.read()
        
        # 执行 SQL 脚本
        connection.executescript(sql_script)
        connection.commit()
      finally:
        connection.close()

  def get_connection(self):
    """获取数据库连接"""
    if self.connection is None:
      self.connection = sqlite3.connect(
        self.config.DB_PATH,
        check_same_thread=False,
      )
      # 设置返回字典格式的游标
      self.connection.row_factory = sqlite3.Row
    return self.connection

  def _row_to_dict(self, row):
    """将 SQLite Row 对象转换为字典"""
    if row is None:
      return None
    return dict(row)

  def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
    """执行查询SQL"""
    self._validate_sql(sql)
    
    # 将 MySQL 的占位符 %s 转换为 SQLite 的 ?
    sql = sql.replace('%s', '?')
    
    connection = self.get_connection()
    cursor = None
    try:
      cursor = connection.cursor()
      if params:
        cursor.execute(sql, params)
      else:
        cursor.execute(sql)
      results = cursor.fetchall()
      # 转换为字典列表
      return [self._row_to_dict(row) for row in results]
    except Exception as e:
      raise Exception(f'SQL执行失败: {str(e)}')
    finally:
      if cursor:
        cursor.close()

  def _validate_sql(self, sql: str):
    """验证SQL安全性"""
    sql_upper = sql.upper().strip()
    
    # 检查是否包含禁止的关键字
    for keyword in self.config.FORBIDDEN_SQL_KEYWORDS:
      if keyword in sql_upper:
        raise Exception(f'不允许执行包含 {keyword} 的SQL语句')
    
    # 检查是否以允许的关键字开头
    if not any(sql_upper.startswith(keyword) for keyword in self.config.ALLOWED_SQL_KEYWORDS):
      raise Exception('只允许执行SELECT查询语句')

  def get_tables(self) -> List[Dict[str, str]]:
    """获取所有表列表"""
    # 从映射表获取表信息
    sql = """
      SELECT 
        tm.id,
        tm.natural_name as naturalName,
        tm.db_table_name as name,
        tm.description
      FROM table_mapping tm
      ORDER BY tm.id
    """
    try:
      return self.execute_query(sql)
    except Exception:
      # 如果映射表不存在，返回空列表
      return []

  def get_table_columns(self, table_name: str) -> List[Dict[str, str]]:
    """获取表的字段信息"""
    # 先从映射表获取字段信息
    sql = """
      SELECT 
        cm.natural_name as naturalName,
        cm.db_column_name as name,
        cm.data_type as type,
        '' as description
      FROM column_mapping cm
      INNER JOIN table_mapping tm ON cm.table_id = tm.id
      WHERE tm.db_table_name = ?
      ORDER BY cm.id
    """
    try:
      columns = self.execute_query(sql, (table_name,))
      if columns:
        return columns
    except Exception:
      pass
    
    # 如果映射表查询失败，直接从数据库获取
    connection = self.get_connection()
    try:
      cursor = connection.cursor()
      cursor.execute(f"PRAGMA table_info({table_name})")
      rows = cursor.fetchall()
      columns = []
      for row in rows:
        columns.append({
          'name': row[1],  # name
          'type': row[2],  # type
          'naturalName': '',
          'description': '',
        })
      cursor.close()
      return columns
    except Exception:
      return []

  def close(self):
    """关闭数据库连接"""
    if self.connection:
      self.connection.close()
      self.connection = None
