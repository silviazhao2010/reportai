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
  
  # 大模型配置
  # 支持: openai, qwen, wenxin 等
  LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
  
  # OpenAI配置
  OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
  OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
  OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
  OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
  OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
  
  # 通义千问配置
  DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
  QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-turbo')
  
  # 文心一言配置
  WENXIN_API_KEY = os.getenv('WENXIN_API_KEY', '')
  WENXIN_SECRET_KEY = os.getenv('WENXIN_SECRET_KEY', '')
  WENXIN_MODEL = os.getenv('WENXIN_MODEL', 'ernie-bot-turbo')

