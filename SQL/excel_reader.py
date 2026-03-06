"""Excel表定义读取模块"""
import pandas as pd
from typing import List, Dict, Any
from collections import defaultdict


class ExcelReader:
    """读取Excel格式的数据库表定义"""
    
    def __init__(self, excel_path: str):
        """
        初始化Excel读取器
        
        Args:
            excel_path: Excel文件路径
        """
        self.excel_path = excel_path
        self.schema = None
    
    def read(self) -> Dict[str, Any]:
        """
        读取Excel文件并解析为数据库schema
        
        Returns:
            数据库schema字典，格式：
            {
                "表名": {
                    "表含义": "说明",
                    "字段": [
                        {"字段名": "name", "字段类型": "VARCHAR", "字段含义": "说明"}
                    ]
                }
            }
        """
        try:
            df = pd.read_excel(self.excel_path)
            
            # 标准化列名（去除空格，统一大小写）
            df.columns = df.columns.str.strip()
            
            # 检查必需的列
            required_columns = ['表名', '表含义', '字段名', '字段类型', '字段含义']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Excel文件缺少必需的列: {missing_columns}")
            
            # 按表名分组
            schema = {}
            
            for _, row in df.iterrows():
                table_name = str(row['表名']).strip()
                table_desc = str(row['表含义']).strip()
                field_name = str(row['字段名']).strip()
                field_type = str(row['字段类型']).strip()
                field_desc = str(row['字段含义']).strip()
                
                if table_name not in schema:
                    schema[table_name] = {
                        '表含义': table_desc,
                        '字段': [],
                    }
                
                schema[table_name]['字段'].append({
                    '字段名': field_name,
                    '字段类型': field_type,
                    '字段含义': field_desc,
                })
            
            self.schema = schema
            return schema
        
        except Exception as e:
            raise Exception(f"读取Excel文件失败: {str(e)}")
    
    def format_schema_for_prompt(self) -> str:
        """
        将schema格式化为适合大模型输入的文本格式
        
        Returns:
            格式化后的schema文本
        """
        if not self.schema:
            self.read()
        
        lines = []
        lines.append("## 数据库表结构定义\n")
        
        for table_name, table_info in self.schema.items():
            lines.append(f"### 表名: {table_name}")
            lines.append(f"表含义: {table_info['表含义']}\n")
            lines.append("字段列表:")
            
            for field in table_info['字段']:
                lines.append(
                    f"  - {field['字段名']} ({field['字段类型']}): {field['字段含义']}"
                )
            
            lines.append("")  # 空行分隔
        
        return "\n".join(lines)
    
    def get_table_names(self) -> List[str]:
        """获取所有表名"""
        if not self.schema:
            self.read()
        return list(self.schema.keys())
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取指定表的信息"""
        if not self.schema:
            self.read()
        return self.schema.get(table_name, {})
