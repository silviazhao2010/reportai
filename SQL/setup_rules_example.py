"""设置规则示例脚本"""
from rules_manager import RulesManager


def setup_example_rules():
    """设置示例规则"""
    rules_manager = RulesManager()
    
    print("正在设置示例业务规则...")
    
    # 1. 添加表命名规则
    rules_manager.add_table_naming_rule(
        pattern="以 _1h 结尾",
        meaning="小时表，存储按小时聚合的数据",
        usage="当需要查询小时级别的时间范围数据时，应该查询以 _1h 结尾的表",
        examples=["user_stats_1h", "order_stats_1h", "payment_stats_1h"]
    )
    
    rules_manager.add_table_naming_rule(
        pattern="以 _1d 结尾",
        meaning="天表，存储按天聚合的数据",
        usage="当需要查询天级别的时间范围数据时，应该查询以 _1d 结尾的表",
        examples=["user_stats_1d", "order_stats_1d", "payment_stats_1d"]
    )
    
    # 2. 添加字段值含义规则
    rules_manager.add_field_value_rule(
        table_name="",  # 空字符串表示通用规则，适用于所有表
        field_name="info_ind",
        value=2,
        meaning="保障用户",
        usage="当需要查询保障用户时，使用 WHERE info_ind = 2"
    )
    
    rules_manager.add_field_value_rule(
        table_name="users",
        field_name="status",
        value=1,
        meaning="活跃用户",
        usage="状态为1表示用户处于活跃状态"
    )
    
    rules_manager.add_field_value_rule(
        table_name="users",
        field_name="status",
        value=0,
        meaning="非活跃用户",
        usage="状态为0表示用户处于非活跃状态"
    )
    
    # 3. 添加查询模式规则
    rules_manager.add_query_pattern_rule(
        pattern="查询最近N小时的数据",
        description="应该使用以 _1h 结尾的小时表，并使用时间范围条件",
        sql_example="SELECT * FROM table_1h WHERE time >= DATE_SUB(NOW(), INTERVAL N HOUR)"
    )
    
    rules_manager.add_query_pattern_rule(
        pattern="查询最近N天的数据",
        description="应该使用以 _1d 结尾的天表，并使用时间范围条件",
        sql_example="SELECT * FROM table_1d WHERE date >= DATE_SUB(CURDATE(), INTERVAL N DAY)"
    )
    
    # 4. 添加业务规则
    rules_manager.add_business_rule(
        rule="所有时间字段使用UTC时区",
        description="数据库中的时间字段都存储为UTC时间，查询时需要根据需要进行时区转换",
        examples=[
            "查询北京时间需要转换为 UTC+8",
            "使用 CONVERT_TZ() 函数进行时区转换",
            "示例: CONVERT_TZ(time, '+00:00', '+08:00')"
        ]
    )
    
    print("\n规则设置完成！")
    print(f"\n规则摘要: {rules_manager.get_rules_summary()}")
    print("\n规则已保存到 examples/rules.json")
    print("\n格式化后的规则预览:")
    print("-" * 60)
    print(rules_manager.format_rules_for_prompt())
    print("-" * 60)


if __name__ == '__main__':
    setup_example_rules()
