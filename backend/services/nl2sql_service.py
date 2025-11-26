import re
from typing import Dict, List, Any
from services.database_service import DatabaseService

class NL2SQLService:
  """NL2SQL转换服务"""
  
  def __init__(self, db_service: DatabaseService):
    self.db_service = db_service
    self.table_mapping = self._load_table_mapping()
    self.column_mapping = self._load_column_mapping()

  def _load_table_mapping(self) -> Dict[str, str]:
    """加载表名映射"""
    mapping = {}
    try:
      tables = self.db_service.get_tables()
      for table in tables:
        natural_name = table.get('naturalName', '')
        db_name = table.get('name', '')
        if natural_name and db_name:
          mapping[natural_name] = db_name
          # 也支持直接使用数据库表名
          mapping[db_name] = db_name
    except Exception:
      pass
    
    # 默认映射
    default_mapping = {
      '用户': 'users',
      '用户表': 'users',
      '订单': 'orders',
      '订单表': 'orders',
      '产品': 'products',
      '产品表': 'products',
    }
    mapping.update(default_mapping)
    return mapping

  def _load_column_mapping(self) -> Dict[str, Dict[str, str]]:
    """加载字段映射"""
    mapping = {}
    try:
      for table_name in self.table_mapping.values():
        columns = self.db_service.get_table_columns(table_name)
        if table_name not in mapping:
          mapping[table_name] = {}
        for col in columns:
          natural_name = col.get('naturalName', '')
          db_name = col.get('name', '')
          if natural_name and db_name:
            mapping[table_name][natural_name] = db_name
          # 也支持直接使用数据库字段名
          mapping[table_name][db_name] = db_name
    except Exception:
      pass
    
    # 默认映射
    default_mapping = {
      'users': {
        '编号': 'id',
        '姓名': 'name',
        '名字': 'name',
        '年龄': 'age',
        '城市': 'city',
        '创建时间': 'created_at',
      },
      'orders': {
        '编号': 'id',
        '用户编号': 'user_id',
        '产品名称': 'product_name',
        '金额': 'amount',
        '订单日期': 'order_date',
        '状态': 'status',
      },
      'products': {
        '编号': 'id',
        '名称': 'name',
        '分类': 'category',
        '价格': 'price',
        '库存': 'stock',
      },
    }
    for table, cols in default_mapping.items():
      if table not in mapping:
        mapping[table] = {}
      mapping[table].update(cols)
    
    return mapping

  def convert_to_sql(self, natural_language: str) -> str:
    """将自然语言转换为SQL"""
    # 文本预处理
    text = natural_language.strip()
    
    # 识别表名
    table_name = self._extract_table_name(text)
    if not table_name:
      raise Exception('无法识别查询的表名，请明确指定表名（如：用户、订单、产品）')
    
    # 识别查询类型和字段
    select_clause = self._build_select_clause(text, table_name)
    where_clause = self._build_where_clause(text, table_name)
    group_by_clause = self._build_group_by_clause(text, table_name)
    order_by_clause = self._build_order_by_clause(text, table_name)
    limit_clause = self._build_limit_clause(text)
    
    # 构建SQL
    sql = f"SELECT {select_clause} FROM {table_name}"
    if where_clause:
      sql += f" WHERE {where_clause}"
    if group_by_clause:
      sql += f" GROUP BY {group_by_clause}"
    if order_by_clause:
      sql += f" ORDER BY {order_by_clause}"
    if limit_clause:
      sql += f" LIMIT {limit_clause}"
    
    return sql

  def _extract_table_name(self, text: str) -> str:
    """提取表名"""
    for natural_name, db_name in self.table_mapping.items():
      if natural_name in text:
        return db_name
    return None

  def _build_select_clause(self, text: str, table_name: str) -> str:
    """构建SELECT子句"""
    # 识别聚合函数
    if '统计' in text or '总数' in text or '数量' in text:
      if '每个' in text or '按' in text:
        # 需要GROUP BY，先返回字段名
        field = self._extract_field_name(text, table_name, ['城市', 'category', '分类'])
        if field:
          return f"{field}, COUNT(*) as count"
        return "*, COUNT(*) as count"
      return "COUNT(*) as count"
    
    if '总和' in text or '总金额' in text or '合计' in text:
      field = self._extract_field_name(text, table_name, ['金额', 'amount', '价格', 'price'])
      if field:
        return f"SUM({field}) as total"
      return "SUM(amount) as total"
    
    if '平均' in text or '平均值' in text:
      field = self._extract_field_name(text, table_name, ['金额', 'amount', '价格', 'price', '年龄', 'age'])
      if field:
        return f"AVG({field}) as avg_value"
      return "AVG(amount) as avg_value"
    
    if '最大' in text or '最高' in text:
      field = self._extract_field_name(text, table_name, ['金额', 'amount', '价格', 'price', '年龄', 'age'])
      if field:
        return f"MAX({field}) as max_value"
      return "MAX(amount) as max_value"
    
    if '最小' in text or '最低' in text:
      field = self._extract_field_name(text, table_name, ['金额', 'amount', '价格', 'price', '年龄', 'age'])
      if field:
        return f"MIN({field}) as min_value"
      return "MIN(amount) as min_value"
    
    # 默认查询所有字段
    if '所有' in text or '*' in text:
      return "*"
    
    # 尝试提取特定字段
    fields = self._extract_fields(text, table_name)
    if fields:
      return ", ".join(fields)
    
    return "*"

  def _extract_field_name(self, text: str, table_name: str, keywords: List[str]) -> str:
    """提取字段名"""
    if table_name not in self.column_mapping:
      return None
    
    for keyword in keywords:
      if keyword in text:
        mapping = self.column_mapping[table_name]
        if keyword in mapping:
          return mapping[keyword]
    
    return None

  def _extract_fields(self, text: str, table_name: str) -> List[str]:
    """提取多个字段名"""
    if table_name not in self.column_mapping:
      return []
    
    fields = []
    mapping = self.column_mapping[table_name]
    for natural_name, db_name in mapping.items():
      if natural_name in text:
        fields.append(db_name)
    
    return fields if fields else None

  def _build_where_clause(self, text: str, table_name: str) -> str:
    """构建WHERE子句"""
    conditions = []
    
    # 数值条件
    age_match = re.search(r'年龄[大于小于等于]+(\d+)', text)
    if age_match:
      age_value = age_match.group(1)
      if '大于' in text:
        conditions.append(f"age > {age_value}")
      elif '小于' in text:
        conditions.append(f"age < {age_value}")
      elif '等于' in text:
        conditions.append(f"age = {age_value}")
    
    # 金额条件
    amount_match = re.search(r'金额[大于小于等于]+([\d.]+)', text)
    if amount_match:
      amount_value = amount_match.group(1)
      if '大于' in text:
        conditions.append(f"amount > {amount_value}")
      elif '小于' in text:
        conditions.append(f"amount < {amount_value}")
      elif '等于' in text:
        conditions.append(f"amount = {amount_value}")
    
    # 状态条件
    if '已完成' in text or '完成' in text:
      conditions.append("status = '已完成'")
    elif '待处理' in text or '未完成' in text:
      conditions.append("status = '待处理'")
    
    # 时间条件
    if '今天' in text:
      conditions.append("DATE(order_date) = CURDATE()")
    elif '昨天' in text:
      conditions.append("DATE(order_date) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
    elif '本周' in text:
      conditions.append("YEARWEEK(order_date) = YEARWEEK(CURDATE())")
    elif '本月' in text:
      conditions.append("YEAR(order_date) = YEAR(CURDATE()) AND MONTH(order_date) = MONTH(CURDATE())")
    
    return " AND ".join(conditions) if conditions else ""

  def _build_group_by_clause(self, text: str, table_name: str) -> str:
    """构建GROUP BY子句"""
    if '每个' in text or '按' in text:
      # 提取分组字段
      if '城市' in text or 'city' in text:
        return "city"
      elif '分类' in text or 'category' in text:
        return "category"
      elif '用户' in text or 'user_id' in text:
        return "user_id"
      elif '日期' in text or 'order_date' in text:
        return "order_date"
    
    return ""

  def _build_order_by_clause(self, text: str, table_name: str) -> str:
    """构建ORDER BY子句"""
    if '排序' in text or '排列' in text or '顺序' in text:
      # 提取排序字段
      field = None
      if '金额' in text or 'amount' in text:
        field = "amount"
      elif '年龄' in text or 'age' in text:
        field = "age"
      elif '日期' in text or 'order_date' in text:
        field = "order_date"
      elif '价格' in text or 'price' in text:
        field = "price"
      
      if field:
        if '降序' in text or '倒序' in text or 'DESC' in text.upper():
          return f"{field} DESC"
        else:
          return f"{field} ASC"
    
    return ""

  def _build_limit_clause(self, text: str) -> str:
    """构建LIMIT子句"""
    limit_match = re.search(r'前(\d+)', text)
    if limit_match:
      return limit_match.group(1)
    
    limit_match = re.search(r'(\d+)条', text)
    if limit_match:
      return limit_match.group(1)
    
    return ""

