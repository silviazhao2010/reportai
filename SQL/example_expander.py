"""样例扩展工具"""
import json
from excel_reader import ExcelReader
from example_manager import ExampleManager
from rules_manager import RulesManager
from llm_client import LLMClient
from config import Config


class ExampleExpander:
    """样例扩展工具，用于生成更多训练样例"""
    
    def __init__(self, excel_path: str):
        """
        初始化样例扩展器
        
        Args:
            excel_path: Excel文件路径
        """
        self.excel_reader = ExcelReader(excel_path)
        self.example_manager = ExampleManager()
        self.rules_manager = RulesManager()
        self.llm_client = LLMClient()
    
    def expand_all_examples(
        self,
        variations_per_example: int = 2,
        variation_types: list = None,
        use_diverse_types: bool = True,
    ) -> list:
        """
        扩展所有现有样例
        
        Args:
            variations_per_example: 每个样例生成多少个变体
            variation_types: 变体类型列表，如果为None则自动选择
            use_diverse_types: 是否使用多样化的变体类型，True则自动选择多种类型
        
        Returns:
            新生成的样例列表
        """
        if variation_types is None:
            if use_diverse_types:
                # 使用多样化的变体类型组合
                variation_types = [
                    'paraphrase',      # 语义相同但表达不同
                    'similar',         # 相似但略有不同
                    'different_style', # 不同表达风格
                    'different_angle', # 不同查询角度
                ]
            else:
                variation_types = ['paraphrase', 'similar']
        
        # 读取schema
        schema_text = self.excel_reader.format_schema_for_prompt()
        
        # 读取规则
        rules_text = self.rules_manager.format_rules_for_prompt()
        
        # 获取现有样例
        existing_examples = self.example_manager.get_examples()
        
        if not existing_examples:
            print("没有现有样例可扩展")
            return []
        
        new_examples = []
        
        print(f"开始扩展 {len(existing_examples)} 个样例...")
        
        for i, example in enumerate(existing_examples, 1):
            print(f"\n处理样例 {i}/{len(existing_examples)}: {example['question'][:50]}...")
            
            # 为每个变体类型生成指定数量的变体
            for variation_type in variation_types:
                for j in range(variations_per_example):
                    try:
                        print(f"  生成变体 ({variation_type}) {j+1}/{variations_per_example}...")
                        
                        # 为不同变体添加多样性提示
                        diversity_hint = None
                        if variation_type == 'different_style':
                            styles = ['口语化', '正式商务', '技术性', '简洁', '详细描述']
                            diversity_hint = f"\n提示：请使用'{styles[j % len(styles)]}'风格"
                        elif variation_type == 'different_angle':
                            angles = ['时间维度', '统计维度', '筛选维度', '排序维度', '业务视角']
                            diversity_hint = f"\n提示：请从'{angles[j % len(angles)]}'角度思考"
                        
                        new_example = self.llm_client.expand_example(
                            original_question=example['question'],
                            original_sql=example['sql'],
                            schema_text=schema_text,
                            variation_type=variation_type,
                            diversity_hint=diversity_hint,
                            rules_text=rules_text if rules_text else None,
                        )
                        new_examples.append(new_example)
                        print(f"  ✓ 生成成功: {new_example['question'][:50]}...")
                    
                    except Exception as e:
                        print(f"  ✗ 生成失败: {str(e)}")
        
        return new_examples
    
    def save_expanded_examples(self, new_examples: list, merge: bool = True):
        """
        保存扩展后的样例
        
        Args:
            new_examples: 新生成的样例列表
            merge: 是否合并到现有样例中，True则合并，False则替换
        """
        if merge:
            existing_examples = self.example_manager.get_examples()
            all_examples = existing_examples + new_examples
        else:
            all_examples = new_examples
        
        self.example_manager.save(all_examples)
        print(f"\n已保存 {len(new_examples)} 个新样例，总计 {len(all_examples)} 个样例")


def main():
    """主函数：交互式扩展样例"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python example_expander.py <excel文件路径> [variations_per_example]")
        print("示例: python example_expander.py data/database_schema.xlsx 2")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    variations_per_example = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    expander = ExampleExpander(excel_path)
    
    print("=" * 60)
    print("样例扩展工具")
    print("=" * 60)
    
    # 显示当前样例数量
    current_count = expander.example_manager.get_count()
    print(f"\n当前样例数量: {current_count}")
    
    if current_count == 0:
        print("\n警告: 当前没有样例，请先添加一些样例到 examples/examples.json")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            return
    
    # 扩展样例
    new_examples = expander.expand_all_examples(
        variations_per_example=variations_per_example,
    )
    
    if new_examples:
        print(f"\n成功生成 {len(new_examples)} 个新样例")
        
        # 预览前几个
        print("\n预览前3个新样例:")
        for i, example in enumerate(new_examples[:3], 1):
            print(f"\n{i}. 问题: {example['question']}")
            print(f"   SQL: {example['sql']}")
        
        # 确认保存
        response = input(f"\n是否保存这 {len(new_examples)} 个新样例？(y/n): ")
        if response.lower() == 'y':
            expander.save_expanded_examples(new_examples, merge=True)
            print("保存成功！")
        else:
            print("已取消保存")
    else:
        print("\n没有生成新样例")


if __name__ == '__main__':
    main()
