"""主程序：Text-to-SQL生成系统"""
import sys
import os
from excel_reader import ExcelReader
from example_manager import ExampleManager
from rules_manager import RulesManager
from prompt_formatter import PromptFormatter
from llm_client import LLMClient
from config import Config


class TextToSQL:
    """Text-to-SQL主类"""
    
    def __init__(self, excel_path: str, llm_provider: str = None):
        """
        初始化Text-to-SQL系统
        
        Args:
            excel_path: Excel文件路径
            llm_provider: LLM提供商，None则使用配置中的默认值
        """
        self.excel_reader = ExcelReader(excel_path)
        self.example_manager = ExampleManager()
        self.rules_manager = RulesManager()
        self.prompt_formatter = PromptFormatter(
            excel_reader=self.excel_reader,
            example_manager=self.example_manager,
            rules_manager=self.rules_manager,
        )
        self.llm_client = LLMClient(provider=llm_provider)
        
        # 读取schema
        self.excel_reader.read()
    
    def generate_sql(
        self,
        question: str,
        use_examples: bool = True,
        max_examples: int = None,
    ) -> str:
        """
        根据用户问题生成SQL
        
        Args:
            question: 用户问题
            use_examples: 是否使用few-shot examples
            max_examples: 最多使用的样例数量
        
        Returns:
            生成的SQL语句
        """
        # 格式化Prompt
        prompt = self.prompt_formatter.format_prompt(
            user_question=question,
            use_examples=use_examples,
            max_examples=max_examples,
        )
        
        # 生成SQL
        sql = self.llm_client.generate_sql(prompt)
        
        return sql
    
    def interactive_mode(self):
        """交互式模式"""
        print("=" * 60)
        print("Text-to-SQL 生成系统")
        print("=" * 60)
        print(f"\n数据库表数量: {len(self.excel_reader.get_table_names())}")
        print(f"样例数量: {self.example_manager.get_count()}")
        rules_summary = self.rules_manager.get_rules_summary()
        if rules_summary != "无规则":
            print(f"业务规则: {rules_summary}")
        print("\n输入问题生成SQL，输入 'quit' 或 'exit' 退出")
        print("-" * 60)
        
        while True:
            try:
                question = input("\n问题: ").strip()
                
                if question.lower() in ['quit', 'exit', '退出']:
                    print("再见！")
                    break
                
                if not question:
                    continue
                
                print("\n正在生成SQL...")
                sql = self.generate_sql(question)
                
                print(f"\n生成的SQL:")
                print("-" * 60)
                print(sql)
                print("-" * 60)
                
                # 询问是否保存为样例
                save = input("\n是否保存为样例？(y/n): ").strip().lower()
                if save == 'y':
                    self.example_manager.add_example(
                        question=question,
                        sql=sql,
                        description="交互式生成",
                    )
                    print("已保存为样例")
            
            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"\n错误: {str(e)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Text-to-SQL 生成系统')
    parser.add_argument(
        'excel_path',
        nargs='?',
        default='data/database_schema.xlsx',
        help='Excel文件路径（默认: data/database_schema.xlsx）',
    )
    parser.add_argument(
        '--question',
        '-q',
        help='直接输入问题（非交互模式）',
    )
    parser.add_argument(
        '--provider',
        '-p',
        choices=['openai', 'anthropic'],
        help='LLM提供商（覆盖配置中的默认值）',
    )
    parser.add_argument(
        '--no-examples',
        action='store_true',
        help='不使用few-shot examples',
    )
    parser.add_argument(
        '--max-examples',
        type=int,
        help='最多使用的样例数量',
    )
    
    args = parser.parse_args()
    
    # 检查Excel文件是否存在
    if not os.path.exists(args.excel_path):
        print(f"错误: Excel文件不存在: {args.excel_path}")
        sys.exit(1)
    
    # 创建Text-to-SQL实例
    try:
        text_to_sql = TextToSQL(args.excel_path, llm_provider=args.provider)
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        sys.exit(1)
    
    # 如果提供了问题，直接生成SQL
    if args.question:
        try:
            sql = text_to_sql.generate_sql(
                question=args.question,
                use_examples=not args.no_examples,
                max_examples=args.max_examples,
            )
            print("\n生成的SQL:")
            print("-" * 60)
            print(sql)
            print("-" * 60)
        except Exception as e:
            print(f"生成SQL失败: {str(e)}")
            sys.exit(1)
    else:
        # 交互式模式
        try:
            text_to_sql.interactive_mode()
        except Exception as e:
            print(f"运行失败: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
