# Text-to-SQL 生成系统

基于大模型的SQL生成系统，支持从Excel读取数据库表定义，利用few-shot learning生成SQL语句。

## 功能特性

- 📊 从Excel读取数据库表定义（表名、表含义、字段、字段含义）
- 🤖 支持OpenAI和Anthropic大模型
- 📝 Few-shot learning：利用已有样例提升生成质量
- 🔄 样例扩展工具：自动生成更多训练样例（支持6种变体类型）
- 🎯 智能Prompt格式化：优化大模型输入格式
- 🌈 多样性生成策略：优化的提示词确保生成多样化的样例
- 📋 业务规则系统：支持定义表命名规则、字段值含义等业务约定

## 项目结构

```
SQL/
├── requirements.txt          # 依赖包
├── .env.example            # 环境变量示例
├── config.py               # 配置文件
├── excel_reader.py         # Excel读取模块
├── example_manager.py      # 样例管理模块
├── prompt_formatter.py     # Prompt格式化模块
├── llm_client.py          # 大模型客户端
├── example_expander.py    # 样例扩展工具
├── rules_manager.py       # 业务规则管理模块
├── main.py                # 主程序
├── PROMPT_GUIDE.md        # 提示词编写指南（生成多样性样例）
├── PROMPT_TEMPLATES.md    # 完整提示词模板（可直接使用）
├── GENERATE_NEW_EXAMPLES.md # 生成全新问题和SQL的指南
├── prompt_generate_new_examples.txt # 简化版提示词（可直接复制使用）
├── RULES_GUIDE.md         # 业务规则配置指南
├── examples/              # 样例数据目录
│   ├── examples.json      # 样例数据文件
│   └── rules.json         # 业务规则配置文件
└── data/                  # 数据目录
    └── database_schema.xlsx # 数据库表定义Excel文件
```

## 安装

1. 创建虚拟环境：
```bash
uv venv
```

2. 激活虚拟环境：
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

## 使用方法

### 1. 准备Excel文件

Excel文件应包含以下列：
- `表名`: 数据库表名称
- `表含义`: 表的业务含义说明
- `字段名`: 字段名称
- `字段类型`: 字段数据类型
- `字段含义`: 字段的业务含义说明

### 2. 准备样例数据

在 `examples/examples.json` 中准备问题和SQL的对应关系：

```json
[
  {
    "question": "查询所有用户的姓名和邮箱",
    "sql": "SELECT name, email FROM users",
    "description": "简单查询示例"
  }
]
```

### 3. 运行主程序

```bash
python main.py
```

### 4. 扩展样例

使用样例扩展工具生成更多训练样例：

```bash
python example_expander.py
```

## Excel文件格式示例

| 表名 | 表含义 | 字段名 | 字段类型 | 字段含义 |
|------|--------|--------|----------|----------|
| users | 用户表 | id | INT | 用户ID |
| users | 用户表 | name | VARCHAR | 用户姓名 |
| users | 用户表 | email | VARCHAR | 用户邮箱 |
