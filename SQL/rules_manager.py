"""业务规则管理模块"""
import json
import os
from typing import Dict, List, Any, Optional
from config import Config


class RulesManager:
    """管理数据库业务规则和约定"""
    
    def __init__(self, rules_file: str = None):
        """
        初始化规则管理器
        
        Args:
            rules_file: 规则文件路径，默认为config中的路径
        """
        self.rules_file = rules_file or os.path.join(Config.EXAMPLES_DIR, 'rules.json')
        self.rules = {
            'table_naming': [],      # 表命名规则
            'field_values': [],      # 字段值含义规则
            'query_patterns': [],     # 查询模式规则
            'business_rules': [],     # 业务规则
        }
        self._ensure_file_exists()
        self.load()
    
    def _ensure_file_exists(self):
        """确保规则文件存在"""
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        if not os.path.exists(self.rules_file):
            self.save(self.rules)
    
    def load(self) -> Dict[str, Any]:
        """
        从文件加载规则
        
        Returns:
            规则字典
        """
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
            else:
                self.rules = {
                    'table_naming': [],
                    'field_values': [],
                    'query_patterns': [],
                    'business_rules': [],
                }
        except Exception as e:
            print(f"加载规则文件失败: {e}")
            self.rules = {
                'table_naming': [],
                'field_values': [],
                'query_patterns': [],
                'business_rules': [],
            }
        
        return self.rules
    
    def save(self, rules: Dict[str, Any] = None):
        """
        保存规则到文件
        
        Args:
            rules: 要保存的规则字典，如果为None则保存当前rules
        """
        if rules is not None:
            self.rules = rules
        
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"保存规则文件失败: {str(e)}")
    
    def add_table_naming_rule(
        self,
        pattern: str,
        meaning: str,
        usage: str,
        examples: List[str] = None,
    ):
        """
        添加表命名规则
        
        Args:
            pattern: 命名模式（如：以_1h结尾）
            meaning: 含义说明（如：小时表）
            usage: 使用场景（如：当需要查询小时的时间范围时查询该表）
            examples: 示例表名列表
        """
        rule = {
            'pattern': pattern,
            'meaning': meaning,
            'usage': usage,
            'examples': examples or [],
        }
        self.rules['table_naming'].append(rule)
        self.save()
    
    def add_field_value_rule(
        self,
        table_name: str,
        field_name: str,
        value: Any,
        meaning: str,
        usage: str = None,
    ):
        """
        添加字段值含义规则
        
        Args:
            table_name: 表名（可以为空字符串表示通用规则）
            field_name: 字段名
            value: 字段值
            meaning: 值含义（如：保障用户）
            usage: 使用说明（可选）
        """
        rule = {
            'table_name': table_name,
            'field_name': field_name,
            'value': value,
            'meaning': meaning,
            'usage': usage,
        }
        self.rules['field_values'].append(rule)
        self.save()
    
    def add_query_pattern_rule(
        self,
        pattern: str,
        description: str,
        sql_example: str = None,
    ):
        """
        添加查询模式规则
        
        Args:
            pattern: 查询模式描述（如：查询小时数据）
            description: 规则说明
            sql_example: SQL示例（可选）
        """
        rule = {
            'pattern': pattern,
            'description': description,
            'sql_example': sql_example,
        }
        self.rules['query_patterns'].append(rule)
        self.save()
    
    def add_business_rule(
        self,
        rule: str,
        description: str,
        examples: List[str] = None,
    ):
        """
        添加业务规则
        
        Args:
            rule: 规则描述
            description: 详细说明
            examples: 示例列表（可选）
        """
        business_rule = {
            'rule': rule,
            'description': description,
            'examples': examples or [],
        }
        self.rules['business_rules'].append(business_rule)
        self.save()
    
    def format_rules_for_prompt(self) -> str:
        """
        将规则格式化为适合大模型输入的文本格式
        
        Returns:
            格式化后的规则文本
        """
        if not any(self.rules.values()):
            return ""
        
        lines = []
        lines.append("## 数据库业务规则和约定\n")
        lines.append("**重要**：生成SQL时必须严格遵守以下规则和约定。\n")
        
        # 1. 表命名规则
        if self.rules.get('table_naming'):
            lines.append("### 1. 表命名规则")
            lines.append("")
            for i, rule in enumerate(self.rules['table_naming'], 1):
                lines.append(f"**规则 {i}**: {rule['pattern']}")
                lines.append(f"- 含义: {rule['meaning']}")
                lines.append(f"- 使用场景: {rule['usage']}")
                if rule.get('examples'):
                    examples_str = "、".join(rule['examples'])
                    lines.append(f"- 示例表名: {examples_str}")
                lines.append("")
        
        # 2. 字段值含义规则
        if self.rules.get('field_values'):
            lines.append("### 2. 字段值含义规则")
            lines.append("")
            for i, rule in enumerate(self.rules['field_values'], 1):
                table_info = f"表 `{rule['table_name']}`" if rule['table_name'] else "所有表"
                lines.append(f"**规则 {i}**: {table_info} 的字段 `{rule['field_name']}`")
                lines.append(f"- 当 `{rule['field_name']} = {rule['value']}` 时，表示: {rule['meaning']}")
                if rule.get('usage'):
                    lines.append(f"- 使用说明: {rule['usage']}")
                lines.append("")
        
        # 3. 查询模式规则
        if self.rules.get('query_patterns'):
            lines.append("### 3. 查询模式规则")
            lines.append("")
            for i, rule in enumerate(self.rules['query_patterns'], 1):
                lines.append(f"**规则 {i}**: {rule['pattern']}")
                lines.append(f"- 说明: {rule['description']}")
                if rule.get('sql_example'):
                    lines.append(f"- SQL示例: ```sql\n{rule['sql_example']}\n```")
                lines.append("")
        
        # 4. 业务规则
        if self.rules.get('business_rules'):
            lines.append("### 4. 业务规则")
            lines.append("")
            for i, rule in enumerate(self.rules['business_rules'], 1):
                lines.append(f"**规则 {i}**: {rule['rule']}")
                lines.append(f"- 说明: {rule['description']}")
                if rule.get('examples'):
                    lines.append("- 示例:")
                    for example in rule['examples']:
                        lines.append(f"  - {example}")
                lines.append("")
        
        return "\n".join(lines)
    
    def get_rules_summary(self) -> str:
        """获取规则摘要"""
        summary = []
        if self.rules.get('table_naming'):
            summary.append(f"表命名规则: {len(self.rules['table_naming'])} 条")
        if self.rules.get('field_values'):
            summary.append(f"字段值规则: {len(self.rules['field_values'])} 条")
        if self.rules.get('query_patterns'):
            summary.append(f"查询模式规则: {len(self.rules['query_patterns'])} 条")
        if self.rules.get('business_rules'):
            summary.append(f"业务规则: {len(self.rules['business_rules'])} 条")
        
        return " | ".join(summary) if summary else "无规则"
