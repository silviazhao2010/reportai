"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置"""
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Anthropic配置
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
    
    # 默认LLM提供商
    DEFAULT_LLM_PROVIDER = os.getenv('DEFAULT_LLM_PROVIDER', 'openai')
    
    # 文件路径配置
    EXAMPLES_DIR = 'examples'
    EXAMPLES_FILE = os.path.join(EXAMPLES_DIR, 'examples.json')
    DATA_DIR = 'data'
    
    # Few-shot learning配置
    MAX_EXAMPLES = 5  # 最多使用多少个样例
    EXAMPLE_SELECTION_METHOD = 'similarity'  # 'similarity' 或 'random'
