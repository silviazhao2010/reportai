"""Prompt格式化模块"""
from typing import Optional
from excel_reader import ExcelReader
from example_manager import ExampleManager
from rules_manager import RulesManager
from config import Config


class PromptFormatter:
    """格式化Prompt，优化大模型输入"""
    
    def __init__(
        self,
        excel_reader: ExcelReader,
        example_manager: ExampleManager,
        rules_manager: RulesManager = None,
    ):
        """
        初始化Prompt格式化器
        
        Args:
            excel_reader: Excel读取器实例
            example_manager: 样例管理器实例
            rules_manager: 规则管理器实例，如果为None则自动创建
        """
        self.excel_reader = excel_reader
        self.example_manager = example_manager
        self.rules_manager = rules_manager or RulesManager()
    
    def format_prompt(
        self,
        user_question: str,
        use_examples: bool = True,
        max_examples: int = None,
        include_schema: bool = True,
        include_rules: bool = True,
    ) -> str:
        """
        格式化完整的Prompt
        
        Args:
            user_question: 用户问题
            use_examples: 是否使用few-shot examples
            max_examples: 最多使用的样例数量
            include_schema: 是否包含数据库schema
            include_rules: 是否包含业务规则
        
        Returns:
            格式化后的完整Prompt
        """
        parts = []
        
        # 1. 系统提示词
        parts.append(self._get_system_prompt())
        parts.append("")
        
        # 2. 数据库schema
        if include_schema:
            schema_text = self.excel_reader.format_schema_for_prompt()
            parts.append(schema_text)
            parts.append("")
        
        # 3. 业务规则和约定（在schema之后，examples之前）
        if include_rules:
            rules_text = self.rules_manager.format_rules_for_prompt()
            if rules_text:
                parts.append(rules_text)
                parts.append("")
        
        # 4. Few-shot examples
        if use_examples:
            examples_text = self.example_manager.format_examples_for_prompt(
                count=max_examples or Config.MAX_EXAMPLES
            )
            if examples_text:
                parts.append(examples_text)
                parts.append("")
        
        # 5. 用户问题
        parts.append("## 用户问题\n")
        parts.append(user_question)
        parts.append("")
        
        # 6. 输出要求
        parts.append(self._get_output_requirements())
        
        return "\n".join(parts)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """# SQL生成助手

你是一个专业的SQL生成助手，能够根据用户的问题和数据库表结构，生成准确、高效的SQL查询语句。

## 任务说明
1. 仔细分析用户的问题意图
2. 参考数据库表结构定义，选择合适的表和字段
3. **严格遵守业务规则和约定**（如表命名规则、字段值含义等）
4. 参考提供的样例，保持SQL风格的一致性
5. 生成标准SQL语句（支持MySQL语法）
6. 只返回SQL语句，不要包含其他解释性文字"""
    
    def _get_output_requirements(self) -> str:
        """获取输出要求"""
        return """## 输出要求

请根据上述信息生成SQL查询语句，要求：
1. **必须严格遵守业务规则和约定**（如表命名规则、字段值含义等）
2. SQL语句必须符合MySQL语法规范
3. 只返回SQL语句本身，不要包含markdown代码块标记
4. 确保SQL语句能够正确执行
5. 如果问题涉及多个表，请使用适当的JOIN操作
6. 如果问题不明确或无法生成SQL，请返回 "无法生成SQL: [原因]"

请直接输出SQL语句："""
