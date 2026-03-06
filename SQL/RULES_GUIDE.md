# 业务规则配置指南

## 概述

业务规则系统允许你定义数据库的命名约定、字段值含义、查询模式等规则，这些规则会被自动包含在Prompt中，帮助大模型生成更准确的SQL。

## 规则文件位置

规则文件默认位置：`examples/rules.json`

## 规则类型

### 1. 表命名规则（table_naming）

定义表的命名约定和使用场景。

**示例**：
```json
{
  "table_naming": [
    {
      "pattern": "以 _1h 结尾",
      "meaning": "小时表，存储按小时聚合的数据",
      "usage": "当需要查询小时级别的时间范围数据时，应该查询以 _1h 结尾的表",
      "examples": ["user_stats_1h", "order_stats_1h"]
    },
    {
      "pattern": "以 _1d 结尾",
      "meaning": "天表，存储按天聚合的数据",
      "usage": "当需要查询天级别的时间范围数据时，应该查询以 _1d 结尾的表",
      "examples": ["user_stats_1d", "order_stats_1d"]
    }
  ]
}
```

**字段说明**：
- `pattern`: 命名模式描述（如："以 _1h 结尾"、"以 _1d 结尾"）
- `meaning`: 该命名模式的含义
- `usage`: 使用场景说明
- `examples`: 示例表名列表（可选）

### 2. 字段值含义规则（field_values）

定义特定字段值的业务含义。

**示例**：
```json
{
  "field_values": [
    {
      "table_name": "",
      "field_name": "info_ind",
      "value": 2,
      "meaning": "保障用户",
      "usage": "当需要查询保障用户时，使用 WHERE info_ind = 2"
    },
    {
      "table_name": "users",
      "field_name": "status",
      "value": 1,
      "meaning": "活跃用户",
      "usage": "状态为1表示用户处于活跃状态"
    }
  ]
}
```

**字段说明**：
- `table_name`: 表名，空字符串表示通用规则（适用于所有表）
- `field_name`: 字段名
- `value`: 字段值
- `meaning`: 该值的业务含义
- `usage`: 使用说明（可选）

### 3. 查询模式规则（query_patterns）

定义特定的查询模式和对应的SQL模式。

**示例**：
```json
{
  "query_patterns": [
    {
      "pattern": "查询最近N小时的数据",
      "description": "应该使用以 _1h 结尾的小时表，并使用时间范围条件",
      "sql_example": "SELECT * FROM table_1h WHERE time >= DATE_SUB(NOW(), INTERVAL N HOUR)"
    }
  ]
}
```

**字段说明**：
- `pattern`: 查询模式描述
- `description`: 规则说明
- `sql_example`: SQL示例（可选）

### 4. 业务规则（business_rules）

定义其他业务相关的规则和约定。

**示例**：
```json
{
  "business_rules": [
    {
      "rule": "所有时间字段使用UTC时区",
      "description": "数据库中的时间字段都存储为UTC时间，查询时需要根据需要进行时区转换",
      "examples": [
        "查询北京时间需要转换为 UTC+8",
        "使用 CONVERT_TZ() 函数进行时区转换"
      ]
    }
  ]
}
```

**字段说明**：
- `rule`: 规则描述
- `description`: 详细说明
- `examples`: 示例列表（可选）

## 使用Python API添加规则

除了直接编辑JSON文件，你也可以使用Python API添加规则：

```python
from rules_manager import RulesManager

# 创建规则管理器
rules_manager = RulesManager()

# 添加表命名规则
rules_manager.add_table_naming_rule(
    pattern="以 _1h 结尾",
    meaning="小时表，存储按小时聚合的数据",
    usage="当需要查询小时级别的时间范围数据时，应该查询以 _1h 结尾的表",
    examples=["user_stats_1h", "order_stats_1h"]
)

# 添加字段值规则
rules_manager.add_field_value_rule(
    table_name="",  # 空字符串表示通用规则
    field_name="info_ind",
    value=2,
    meaning="保障用户",
    usage="当需要查询保障用户时，使用 WHERE info_ind = 2"
)

# 添加查询模式规则
rules_manager.add_query_pattern_rule(
    pattern="查询最近N小时的数据",
    description="应该使用以 _1h 结尾的小时表",
    sql_example="SELECT * FROM table_1h WHERE time >= DATE_SUB(NOW(), INTERVAL N HOUR)"
)

# 添加业务规则
rules_manager.add_business_rule(
    rule="所有时间字段使用UTC时区",
    description="数据库中的时间字段都存储为UTC时间",
    examples=["查询北京时间需要转换为 UTC+8"]
)
```

## 规则在Prompt中的位置

规则会被自动插入到Prompt中，位置在数据库schema之后、few-shot examples之前：

```
1. 系统提示词
2. 数据库表结构定义
3. **业务规则和约定** ← 规则在这里
4. Few-shot examples
5. 用户问题
6. 输出要求
```

## 完整示例

以下是一个完整的规则文件示例：

```json
{
  "table_naming": [
    {
      "pattern": "以 _1h 结尾",
      "meaning": "小时表，存储按小时聚合的数据",
      "usage": "当需要查询小时级别的时间范围数据时，应该查询以 _1h 结尾的表",
      "examples": ["user_stats_1h", "order_stats_1h"]
    },
    {
      "pattern": "以 _1d 结尾",
      "meaning": "天表，存储按天聚合的数据",
      "usage": "当需要查询天级别的时间范围数据时，应该查询以 _1d 结尾的表",
      "examples": ["user_stats_1d", "order_stats_1d"]
    }
  ],
  "field_values": [
    {
      "table_name": "",
      "field_name": "info_ind",
      "value": 2,
      "meaning": "保障用户",
      "usage": "当需要查询保障用户时，使用 WHERE info_ind = 2"
    },
    {
      "table_name": "users",
      "field_name": "status",
      "value": 1,
      "meaning": "活跃用户",
      "usage": "状态为1表示用户处于活跃状态"
    }
  ],
  "query_patterns": [
    {
      "pattern": "查询最近N小时的数据",
      "description": "应该使用以 _1h 结尾的小时表，并使用时间范围条件",
      "sql_example": "SELECT * FROM table_1h WHERE time >= DATE_SUB(NOW(), INTERVAL N HOUR)"
    },
    {
      "pattern": "查询最近N天的数据",
      "description": "应该使用以 _1d 结尾的天表，并使用时间范围条件",
      "sql_example": "SELECT * FROM table_1d WHERE date >= DATE_SUB(CURDATE(), INTERVAL N DAY)"
    }
  ],
  "business_rules": [
    {
      "rule": "所有时间字段使用UTC时区",
      "description": "数据库中的时间字段都存储为UTC时间，查询时需要根据需要进行时区转换",
      "examples": [
        "查询北京时间需要转换为 UTC+8",
        "使用 CONVERT_TZ() 函数进行时区转换"
      ]
    }
  ]
}
```

## 最佳实践

1. **明确性**：规则描述要清晰明确，避免歧义
2. **示例**：提供具体的示例表名、SQL示例等，帮助模型理解
3. **完整性**：覆盖所有重要的业务约定和命名规则
4. **更新**：随着业务变化及时更新规则
5. **验证**：添加规则后，测试生成的SQL是否符合预期

## 规则验证

运行主程序时，会显示当前加载的规则摘要：

```bash
python main.py data/database_schema.xlsx
```

输出示例：
```
数据库表数量: 10
样例数量: 5
业务规则: 表命名规则: 2 条 | 字段值规则: 2 条 | 查询模式规则: 2 条
```

## 注意事项

1. JSON文件必须使用UTF-8编码
2. 规则文件格式错误会导致程序无法加载规则（不会报错，只是不加载）
3. 规则会被包含在每次生成的Prompt中，确保大模型能够看到并遵守这些规则
4. 如果某个规则类型为空数组，该类型不会出现在Prompt中
