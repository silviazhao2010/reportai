"""大模型客户端模块"""
from typing import Optional
from openai import OpenAI
import anthropic
from config import Config


class LLMClient:
    """大模型客户端，支持OpenAI和Anthropic"""
    
    def __init__(self, provider: str = None):
        """
        初始化LLM客户端
        
        Args:
            provider: 提供商名称，'openai' 或 'anthropic'，None则使用配置中的默认值
        """
        self.provider = provider or Config.DEFAULT_LLM_PROVIDER
        
        if self.provider == 'openai':
            if not Config.OPENAI_API_KEY:
                raise ValueError("未配置OPENAI_API_KEY")
            self.client = OpenAI(
                api_key=Config.OPENAI_API_KEY,
                base_url=Config.OPENAI_BASE_URL,
            )
            self.model = Config.OPENAI_MODEL
        
        elif self.provider == 'anthropic':
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("未配置ANTHROPIC_API_KEY")
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.model = Config.ANTHROPIC_MODEL
        
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
    
    def generate_sql(self, prompt: str, temperature: float = 0.1) -> str:
        """
        生成SQL语句
        
        Args:
            prompt: 完整的Prompt文本
            temperature: 温度参数，越低越确定，越高越随机
        
        Returns:
            生成的SQL语句
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                    temperature=temperature,
                )
                sql = response.choices[0].message.content.strip()
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    temperature=temperature,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                )
                sql = response.content[0].text.strip()
            
            # 清理SQL语句（移除可能的markdown代码块标记）
            sql = self._clean_sql(sql)
            
            return sql
        
        except Exception as e:
            raise Exception(f"生成SQL失败: {str(e)}")
    
    def _clean_sql(self, sql: str) -> str:
        """
        清理SQL语句，移除markdown代码块标记等
        
        Args:
            sql: 原始SQL文本
        
        Returns:
            清理后的SQL文本
        """
        # 移除markdown代码块标记
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        # 移除可能的SQL关键字前缀
        prefixes_to_remove = ['SQL:', 'sql:', 'SQL语句:', 'sql语句:']
        for prefix in prefixes_to_remove:
            if sql.startswith(prefix):
                sql = sql[len(prefix):].strip()
        
        return sql
    
    def expand_example(
        self,
        original_question: str,
        original_sql: str,
        schema_text: str,
        variation_type: str = 'paraphrase',
        diversity_hint: str = None,
        rules_text: str = None,
    ) -> dict:
        """
        扩展样例：基于原有样例生成变体
        
        Args:
            original_question: 原始问题
            original_sql: 原始SQL
            schema_text: 数据库schema文本
            variation_type: 变体类型
                - 'paraphrase': 语义相同的改写
                - 'similar': 相似但略有不同的问题
                - 'complex': 更复杂的查询（添加条件、排序、分组等）
                - 'simple': 更简单的查询（简化条件）
                - 'different_style': 不同表达风格（口语化/正式/技术性）
                - 'different_angle': 不同查询角度（从不同维度查询相同数据）
            diversity_hint: 多样性提示，用于指导生成方向
            rules_text: 业务规则文本（可选）
        
        Returns:
            包含新问题和SQL的字典
        """
        # 根据变体类型选择不同的提示词策略
        prompt = self._build_expansion_prompt(
            original_question=original_question,
            original_sql=original_sql,
            schema_text=schema_text,
            variation_type=variation_type,
            diversity_hint=diversity_hint,
            rules_text=rules_text,
        )
        
        try:
            # 使用较高的temperature增加多样性
            temperature = 0.8 if variation_type in ['different_style', 'different_angle'] else 0.7
            new_question = self.generate_sql(prompt, temperature=temperature)
            
            # 为新问题生成SQL
            sql_prompt_parts = [
                "# SQL生成任务",
                "",
                "## 数据库表结构",
                schema_text,
                "",
            ]
            
            # 添加业务规则（如果提供）
            if rules_text:
                sql_prompt_parts.extend([
                    rules_text,
                    "",
                ])
            
            sql_prompt_parts.extend([
                "## 参考样例",
                f"问题: {original_question}",
                f"SQL: {original_sql}",
                "",
                "## 新问题",
                new_question,
                "",
                "请为新问题生成SQL语句，要求：",
                "1. **必须严格遵守业务规则和约定**（如果提供了规则）",
                "2. SQL必须符合MySQL语法规范",
                "3. 确保SQL能够正确执行",
                "4. 只返回SQL语句本身，不要包含markdown代码块标记",
                "5. 如果问题不明确，请根据上下文合理推断",
                "",
                "SQL语句：",
            ])
            
            sql_prompt = "\n".join(sql_prompt_parts)
            
            new_sql = self.generate_sql(sql_prompt, temperature=0.1)
            
            return {
                'question': new_question,
                'sql': new_sql,
                'description': f'由样例扩展生成（{variation_type}）',
            }
        
        except Exception as e:
            raise Exception(f"扩展样例失败: {str(e)}")
    
    def _build_expansion_prompt(
        self,
        original_question: str,
        original_sql: str,
        schema_text: str,
        variation_type: str,
        diversity_hint: str = None,
        rules_text: str = None,
    ) -> str:
        """构建扩展样例的提示词"""
        
        base_context_parts = [
            "## 数据库表结构",
            schema_text,
            "",
        ]
        
        # 添加业务规则（如果提供）
        if rules_text:
            base_context_parts.extend([
                rules_text,
                "",
            ])
        
        base_context_parts.extend([
            "## 原始样例",
            f"问题: {original_question}",
            f"SQL: {original_sql}",
            "",
        ])
        
        base_context = "\n".join(base_context_parts)
        
        if variation_type == 'paraphrase':
            return f"""# 问题改写任务 - 语义相同但表达不同

{base_context}## 任务要求
请生成一个**语义完全相同**但**表达方式完全不同**的问题。

### 多样性要求（重要！）
为了确保生成的问题具有多样性，请遵循以下策略：

1. **词汇替换**：
   - 使用同义词、近义词替换关键词
   - 例如："查询" → "找出"、"获取"、"列出"、"显示"
   - 例如："用户" → "客户"、"会员"、"账户"

2. **句式变换**：
   - 改变语序和句式结构
   - 例如：陈述句 ↔ 疑问句
   - 例如：主动语态 ↔ 被动语态
   - 例如："查询X的Y" → "Y属于X的有哪些"

3. **表达风格**：
   - 可以尝试不同的表达风格（正式/口语/技术性）
   - 但保持语义不变

4. **避免重复**：
   - 不要只是简单替换1-2个词
   - 要彻底改变表达方式，让人感觉是完全不同的问题

### 输出要求
- 只返回改写后的问题，不要返回SQL
- 问题应该自然流畅，符合中文表达习惯
- 确保语义与原问题完全一致

改写后的问题："""
        
        elif variation_type == 'similar':
            return f"""# 相似问题生成任务 - 相关但略有不同

{base_context}## 任务要求
请生成一个**相似但略有不同**的问题，查询**相同或相关**的数据。

### 多样性要求（重要！）
可以通过以下方式创造多样性：

1. **条件变化**：
   - 添加或修改查询条件
   - 改变数值范围（如：最近7天 → 最近30天）
   - 改变筛选条件（如：状态、类型等）

2. **查询范围变化**：
   - 扩大或缩小查询范围
   - 例如："所有用户" → "活跃用户"、"VIP用户"
   - 例如："本月" → "本季度"、"今年"

3. **查询维度变化**：
   - 从不同角度查询相同数据
   - 例如：按时间查询 → 按地区查询
   - 例如：统计总数 → 统计平均值

4. **复杂度调整**：
   - 可以稍微增加或减少查询复杂度
   - 但不要完全改变查询意图

### 输出要求
- 只返回新问题，不要返回SQL
- 问题应该与原问题相关但明显不同
- 确保问题在数据库schema范围内

新问题："""
        
        elif variation_type == 'complex':
            return f"""# 复杂化问题生成任务

{base_context}## 任务要求
请生成一个**更复杂**的问题，基于原问题添加更多查询要求。

### 复杂度提升策略
可以通过以下方式增加复杂度：

1. **添加条件**：
   - 添加WHERE条件（时间范围、状态筛选等）
   - 添加多个AND/OR条件

2. **添加排序**：
   - 按某个字段排序（升序/降序）
   - 多字段排序

3. **添加分组**：
   - 使用GROUP BY进行分组统计
   - 添加HAVING条件

4. **添加聚合**：
   - COUNT、SUM、AVG、MAX、MIN等聚合函数
   - 多字段聚合

5. **多表关联**：
   - 如果原问题是单表查询，可以改为JOIN多表查询

6. **子查询**：
   - 添加子查询或EXISTS条件

### 输出要求
- 只返回新问题，不要返回SQL
- 问题应该比原问题更复杂，但逻辑清晰
- 确保复杂度提升合理，不要过度复杂

新问题："""
        
        elif variation_type == 'simple':
            return f"""# 简化问题生成任务

{base_context}## 任务要求
请生成一个**更简单**的问题，简化原问题的查询要求。

### 简化策略
可以通过以下方式简化：

1. **减少条件**：
   - 移除部分WHERE条件
   - 只保留核心查询需求

2. **减少字段**：
   - 只查询最核心的字段
   - 移除不必要的字段

3. **移除排序/分组**：
   - 如果原问题有排序，可以移除
   - 如果原问题有分组，可以改为简单查询

4. **简化聚合**：
   - 如果原问题有复杂聚合，可以简化为简单统计

### 输出要求
- 只返回新问题，不要返回SQL
- 问题应该比原问题更简单直接
- 保持核心查询意图不变

新问题："""
        
        elif variation_type == 'different_style':
            return f"""# 不同表达风格问题生成任务

{base_context}## 任务要求
请生成一个**表达风格完全不同**但**语义相同或相似**的问题。

### 风格多样性策略
请选择以下一种风格（随机选择，确保多样性）：

1. **口语化风格**：
   - 使用日常口语表达
   - 例如："给我看看"、"找一下"、"有哪些"
   - 语气更随意、亲切

2. **正式商务风格**：
   - 使用正式、专业的表达
   - 例如："请查询"、"请统计"、"请列出"
   - 语气更正式、严谨

3. **技术性风格**：
   - 使用技术术语和精确表达
   - 例如："检索"、"筛选"、"聚合统计"
   - 更偏向技术文档风格

4. **简洁风格**：
   - 使用最简洁的表达
   - 省略不必要的修饰词
   - 例如："用户列表"、"订单统计"

5. **详细描述风格**：
   - 使用更详细的描述
   - 明确说明查询的目的和范围
   - 例如："我需要查询所有在最近一个月内注册的用户信息，包括他们的姓名和邮箱地址"

### 输出要求
- 只返回新问题，不要返回SQL
- 风格要与原问题明显不同
- 确保问题自然流畅

新问题："""
        
        elif variation_type == 'different_angle':
            return f"""# 不同查询角度问题生成任务

{base_context}## 任务要求
请从**不同的查询角度**生成问题，查询**相同或相关**的数据。

### 角度多样性策略
可以从以下角度思考：

1. **时间维度变化**：
   - 从不同时间范围查询（日/周/月/年）
   - 从不同时间点查询（今天/昨天/本周/本月）

2. **统计维度变化**：
   - 从总数 → 平均值 → 最大值 → 最小值
   - 从整体 → 分组统计

3. **筛选维度变化**：
   - 从不同字段筛选（状态/类型/地区等）
   - 从不同条件筛选（等于/大于/包含等）

4. **排序维度变化**：
   - 按不同字段排序
   - 按不同顺序排序（升序/降序）

5. **关联维度变化**：
   - 从单表查询 → 多表关联查询
   - 从不同表的角度查询

6. **业务视角变化**：
   - 从不同业务角色视角（管理员/用户/运营）
   - 从不同业务场景（分析/报表/监控）

### 输出要求
- 只返回新问题，不要返回SQL
- 角度要与原问题明显不同
- 确保问题在数据库schema范围内
{diversity_hint if diversity_hint else ''}

新问题："""
        
        else:
            raise ValueError(
                f"不支持的变体类型: {variation_type}。"
                f"支持的类型: paraphrase, similar, complex, simple, different_style, different_angle"
            )
