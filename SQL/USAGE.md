# 使用指南

## 快速开始

### 1. 准备Excel文件

在 `data/` 目录下创建 `database_schema.xlsx` 文件，包含以下列：

| 表名 | 表含义 | 字段名 | 字段类型 | 字段含义 |
|------|--------|--------|----------|----------|
| users | 用户表 | id | INT | 用户ID |
| users | 用户表 | name | VARCHAR | 用户姓名 |
| users | 用户表 | email | VARCHAR | 用户邮箱 |

### 2. 准备样例数据

编辑 `examples/examples.json`，添加问题和SQL的对应关系：

```json
[
  {
    "question": "查询所有用户的姓名和邮箱",
    "sql": "SELECT name, email FROM users",
    "description": "简单查询示例"
  }
]
```

### 2.5. 配置业务规则（可选但推荐）

编辑 `examples/rules.json`，定义数据库的业务规则和约定：

```json
{
  "table_naming": [
    {
      "pattern": "以 _1h 结尾",
      "meaning": "小时表",
      "usage": "查询小时数据时使用",
      "examples": ["user_stats_1h"]
    }
  ],
  "field_values": [
    {
      "table_name": "",
      "field_name": "info_ind",
      "value": 2,
      "meaning": "保障用户"
    }
  ]
}
```

详细配置说明请参考 `RULES_GUIDE.md`

### 3. 配置API密钥

创建 `.env` 文件（参考 `.env.example`），填入你的API密钥：

```bash
OPENAI_API_KEY=sk-...
# 或
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. 运行程序

#### 交互式模式
```bash
python main.py data/database_schema.xlsx
```

#### 命令行模式
```bash
python main.py data/database_schema.xlsx -q "查询所有用户"
```

## 样例扩展

### 为什么需要格式化输入？

大模型生成SQL的质量很大程度上取决于：
1. **数据库schema的清晰描述**：让模型理解表结构和字段含义
2. **Few-shot learning**：提供高质量的样例，让模型学习正确的SQL模式
3. **Prompt结构**：清晰的指令和格式要求

### Prompt格式化策略

本系统采用以下Prompt结构：

```
1. 系统提示词（角色定义和任务说明）
2. 数据库表结构定义（格式化展示）
3. Few-shot examples（参考样例）
4. 用户问题
5. 输出要求（格式规范）
```

### 如何扩展样例？

#### 方法1：使用样例扩展工具（推荐）

```bash
python example_expander.py data/database_schema.xlsx 2
```

这会：
- 读取现有样例
- 为每个样例生成多样化的变体（包括改写、相似问题、不同风格、不同角度等）
- 自动生成对应的SQL
- 保存到 `examples/examples.json`

**多样性策略**：
- `paraphrase`: 语义相同但表达完全不同
- `similar`: 相似但略有不同（改变条件、范围等）
- `different_style`: 不同表达风格（口语化/正式/技术性等）
- `different_angle`: 不同查询角度（时间维度/统计维度等）

详细提示词编写指南请参考 `PROMPT_GUIDE.md`

#### 方法2：手动添加

直接编辑 `examples/examples.json`，添加新的样例：

```json
{
  "question": "查询最近7天注册的用户",
  "sql": "SELECT * FROM users WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)",
  "description": "时间范围查询示例"
}
```

#### 方法3：交互式保存

运行交互式模式时，生成SQL后选择保存为样例。

### 样例质量建议

好的样例应该：
1. **覆盖常见查询类型**：
   - 简单查询（SELECT）
   - 条件查询（WHERE）
   - 分组统计（GROUP BY）
   - 多表关联（JOIN）
   - 排序（ORDER BY）
   - 聚合函数（COUNT, SUM, AVG等）

2. **问题表达多样化**：
   - 使用不同的问法表达相同意图
   - 包含口语化表达和正式表达
   - 覆盖不同的业务场景
   - **关键**：确保问题表达方式有足够多样性，不要只是简单替换1-2个词

3. **SQL规范**：
   - 使用标准的MySQL语法
   - 字段名和表名清晰
   - 适当的注释（可选）

### 提示词编写技巧（生成多样性样例）

系统已内置了优化的提示词策略，能够生成多样化的样例。关键要点：

1. **明确多样性要求**：在提示词中明确要求"表达方式完全不同"
2. **提供具体策略**：给出词汇替换、句式变换等具体方法
3. **使用示例引导**：展示好的和不好的示例对比
4. **调整温度参数**：使用较高的temperature（0.7-0.9）增加随机性

详细指南请参考 `PROMPT_GUIDE.md` 文件。

## 高级配置

### 调整Few-shot数量

在 `config.py` 中修改：

```python
MAX_EXAMPLES = 5  # 最多使用5个样例
```

或在运行时指定：

```bash
python main.py data/database_schema.xlsx -q "问题" --max-examples 3
```

### 切换LLM提供商

```bash
# 使用OpenAI
python main.py data/database_schema.xlsx --provider openai

# 使用Anthropic
python main.py data/database_schema.xlsx --provider anthropic
```

### 不使用Few-shot

```bash
python main.py data/database_schema.xlsx -q "问题" --no-examples
```

## 最佳实践

1. **逐步积累样例**：从简单查询开始，逐步添加复杂场景
2. **定期扩展**：使用扩展工具定期生成新样例
3. **验证SQL**：生成后在实际数据库中验证SQL正确性
4. **持续优化**：根据生成效果调整Prompt和样例
