# AI报表生成系统

基于自然语言处理技术的智能报表生成平台，用户可以通过自然语言描述需求，系统自动理解用户意图，将自然语言转换为SQL查询语句，执行数据库查询后生成可视化报表。

## 功能特性

- 🎯 **自然语言查询**: 支持使用自然语言描述查询需求
- 🔄 **NL2SQL转换**: 自动将自然语言转换为SQL查询语句
- 📊 **数据可视化**: 支持表格、图表等多种展示方式
- 🔒 **安全防护**: SQL注入防护、查询权限控制
- 🎨 **友好界面**: 基于Ant Design的现代化UI设计

## 技术栈

### 前端
- React 17.0.2
- Ant Design 4.24.13
- React Router DOM 5.3.4
- Axios 1.8.4
- Webpack 4.42.0

### 后端
- Python 3.8+
- Flask 2.3.3
- SQLite 3 (Python内置)
- SQLAlchemy 2.0.23

### 数据库
- SQLite 3

## 项目结构

```
AiReport/
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用入口
│   ├── config.py           # 配置文件
│   └── services/           # 业务服务层
│       ├── database_service.py    # 数据库服务
│       ├── nl2sql_service.py      # NL2SQL转换服务
│       └── query_service.py       # 查询服务
├── src/                    # 前端代码
│   ├── components/         # React组件
│   │   ├── QueryInput.js   # 查询输入组件
│   │   ├── SQLPreview.js   # SQL预览组件
│   │   └── ReportDisplay.js # 报表展示组件
│   ├── pages/              # 页面组件
│   │   └── MainPage.js     # 主页面
│   ├── utils/              # 工具函数
│   │   └── api.js          # API请求封装
│   ├── App.js              # 应用入口组件
│   └── index.js            # 应用启动文件
├── database/               # 数据库脚本
│   └── init.sql            # 数据库初始化脚本
├── public/                 # 静态资源
│   └── index.html          # HTML模板
├── package.json            # 前端依赖配置
├── requirements.txt        # 后端依赖配置
├── webpack.config.js       # Webpack配置
└── README.md               # 项目说明文档
```

## 快速开始

### 环境要求

- Node.js 14+
- Python 3.8+
- SQLite 3 (Python内置，无需单独安装)

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd AiReport
```

#### 2. 配置环境变量（可选）

```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，配置数据库路径（可选，默认使用 database/ai_report.db）
# DB_PATH=database/ai_report.db
```

**注意**: SQLite 数据库会在首次运行时自动创建，无需手动初始化。

#### 4. 安装后端依赖

```bash
pip install -r requirements.txt
```

#### 5. 安装前端依赖

```bash
npm install
```

#### 6. 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://localhost:5000` 启动

#### 7. 启动前端服务

```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 使用说明

### 查询示例

系统支持以下类型的自然语言查询：

1. **简单查询**
   - "查询所有用户"
   - "查询所有订单"

2. **条件查询**
   - "查询年龄大于30的用户"
   - "查询订单金额大于1000的订单"
   - "查询状态为已完成的订单"

3. **聚合查询**
   - "统计每个城市的用户数量"
   - "查询订单总金额"
   - "统计每个用户的订单数量"

4. **排序查询**
   - "按订单金额降序排列"
   - "按年龄升序排列前10条记录"

5. **时间查询**
   - "查询今天的订单"
   - "查询本月的订单"

### API接口

#### 自然语言查询

```http
POST /api/query
Content-Type: application/json

{
  "query": "查询所有用户",
  "showSql": true
}
```

响应示例：

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "张三",
      "age": 25,
      "city": "北京"
    }
  ],
  "sql": "SELECT * FROM users",
  "columns": ["id", "name", "age", "city"],
  "message": "查询成功"
}
```

#### 获取表列表

```http
GET /api/tables
```

#### 获取表字段信息

```http
GET /api/tables/:tableName/columns
```

## 开发说明

### 前端开发

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

### 后端开发

```bash
# 启动开发服务器（自动重载）
python backend/app.py
```

## 安全特性

- ✅ SQL注入防护（参数化查询）
- ✅ SQL白名单验证（仅允许SELECT语句）
- ✅ 禁止执行DDL和DML语句
- ✅ 查询结果集大小限制
- ✅ 查询超时控制

## 注意事项

1. 本系统为Demo版本，NL2SQL转换基于规则模板实现，支持常见的查询模式
2. 生产环境使用建议：
   - 集成更强大的NL2SQL模型（如SQLova、TypeSQL等）
   - 添加用户认证和授权
   - 实现查询历史记录
   - 添加更多图表类型支持
   - 优化错误处理和用户提示

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

