import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
  """应用配置类"""
  # 数据库配置 (SQLite)
  _db_path = os.getenv('DB_PATH', 'database/ai_report.db')
  # 如果是相对路径，则相对于项目根目录；如果是绝对路径，则直接使用
  DB_PATH = os.path.join(BASE_DIR, _db_path) if not os.path.isabs(_db_path) else _db_path

  # 查询限制
  MAX_RESULT_SIZE = int(os.getenv('MAX_RESULT_SIZE', 10000))
  QUERY_TIMEOUT = int(os.getenv('QUERY_TIMEOUT', 30))

  # 安全配置
  ALLOWED_SQL_KEYWORDS = ['SELECT']
  FORBIDDEN_SQL_KEYWORDS = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']

