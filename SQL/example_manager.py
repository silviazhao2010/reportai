"""样例管理模块"""
import json
import os
from typing import List, Dict, Any
from config import Config


class ExampleManager:
    """管理问题和SQL的样例数据"""
    
    def __init__(self, examples_file: str = None):
        """
        初始化样例管理器
        
        Args:
            examples_file: 样例文件路径，默认为config中的路径
        """
        self.examples_file = examples_file or Config.EXAMPLES_FILE
        self.examples = []
        self._ensure_file_exists()
        self.load()
    
    def _ensure_file_exists(self):
        """确保样例文件存在"""
        os.makedirs(os.path.dirname(self.examples_file), exist_ok=True)
        if not os.path.exists(self.examples_file):
            self.save([])
    
    def load(self) -> List[Dict[str, Any]]:
        """
        从文件加载样例数据
        
        Returns:
            样例列表
        """
        try:
            if os.path.exists(self.examples_file):
                with open(self.examples_file, 'r', encoding='utf-8') as f:
                    self.examples = json.load(f)
            else:
                self.examples = []
        except Exception as e:
            print(f"加载样例文件失败: {e}")
            self.examples = []
        
        return self.examples
    
    def save(self, examples: List[Dict[str, Any]] = None):
        """
        保存样例数据到文件
        
        Args:
            examples: 要保存的样例列表，如果为None则保存当前examples
        """
        if examples is not None:
            self.examples = examples
        
        try:
            with open(self.examples_file, 'w', encoding='utf-8') as f:
                json.dump(self.examples, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存样例文件失败: {str(e)}")
    
    def add_example(self, question: str, sql: str, description: str = ""):
        """
        添加一个样例
        
        Args:
            question: 用户问题
            sql: 对应的SQL语句
            description: 样例描述（可选）
        """
        example = {
            'question': question,
            'sql': sql,
            'description': description,
        }
        self.examples.append(example)
        self.save()
    
    def get_examples(self, count: int = None, method: str = 'all') -> List[Dict[str, Any]]:
        """
        获取样例列表
        
        Args:
            count: 返回的样例数量，None表示返回全部
            method: 选择方法，'all'表示全部，'random'表示随机，'similarity'表示相似度（暂未实现）
        
        Returns:
            样例列表
        """
        examples = self.examples.copy()
        
        if method == 'random':
            import random
            random.shuffle(examples)
        
        if count is not None:
            examples = examples[:count]
        
        return examples
    
    def format_examples_for_prompt(self, count: int = None) -> str:
        """
        将样例格式化为适合大模型输入的文本格式
        
        Args:
            count: 使用的样例数量
        
        Returns:
            格式化后的样例文本
        """
        examples = self.get_examples(count=count or Config.MAX_EXAMPLES)
        
        if not examples:
            return ""
        
        lines = []
        lines.append("## 参考样例\n")
        lines.append("以下是问题和SQL的对应关系示例，请参考这些样例生成SQL：\n")
        
        for i, example in enumerate(examples, 1):
            lines.append(f"### 样例 {i}")
            if example.get('description'):
                lines.append(f"说明: {example['description']}")
            lines.append(f"问题: {example['question']}")
            lines.append(f"SQL: ```sql\n{example['sql']}\n```")
            lines.append("")  # 空行分隔
        
        return "\n".join(lines)
    
    def get_count(self) -> int:
        """获取样例总数"""
        return len(self.examples)
