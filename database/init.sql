-- AI报表生成系统数据库初始化脚本 (SQLite版本)

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    city VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name VARCHAR(100),
    amount REAL,
    order_date DATE,
    status VARCHAR(20) DEFAULT '待处理',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price REAL,
    stock INTEGER DEFAULT 0
);

-- 表名映射表
CREATE TABLE IF NOT EXISTS table_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    natural_name VARCHAR(100) NOT NULL UNIQUE,
    db_table_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 字段映射表
CREATE TABLE IF NOT EXISTS column_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_id INTEGER NOT NULL,
    natural_name VARCHAR(100) NOT NULL,
    db_column_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50),
    FOREIGN KEY (table_id) REFERENCES table_mapping(id) ON DELETE CASCADE,
    UNIQUE(table_id, natural_name)
);

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
CREATE INDEX IF NOT EXISTS idx_users_age ON users(age);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- 插入表名映射数据
INSERT OR REPLACE INTO table_mapping (id, natural_name, db_table_name, description) VALUES
(1, '用户', 'users', '用户信息表'),
(2, '用户表', 'users', '用户信息表'),
(3, '订单', 'orders', '订单表'),
(4, '订单表', 'orders', '订单表'),
(5, '产品', 'products', '产品表'),
(6, '产品表', 'products', '产品表'),
(7, '客户', 'users', '用户信息表'),
(8, '客户表', 'users', '用户信息表'),
(9, '购买记录', 'orders', '订单表'),
(10, '销售记录', 'orders', '订单表'),
(11, '商品', 'products', '产品表'),
(12, '商品表', 'products', '产品表');

-- 插入用户表字段映射
INSERT OR REPLACE INTO column_mapping (table_id, natural_name, db_column_name, data_type) 
SELECT tm.id, cm.natural_name, cm.db_column_name, cm.data_type
FROM table_mapping tm
CROSS JOIN (
    SELECT '编号' as natural_name, 'id' as db_column_name, 'INTEGER' as data_type
    UNION ALL SELECT 'ID', 'id', 'INTEGER'
    UNION ALL SELECT '用户编号', 'id', 'INTEGER'
    UNION ALL SELECT '用户ID', 'id', 'INTEGER'
    UNION ALL SELECT '姓名', 'name', 'VARCHAR'
    UNION ALL SELECT '名字', 'name', 'VARCHAR'
    UNION ALL SELECT '用户名', 'name', 'VARCHAR'
    UNION ALL SELECT '客户姓名', 'name', 'VARCHAR'
    UNION ALL SELECT '年龄', 'age', 'INTEGER'
    UNION ALL SELECT '岁数', 'age', 'INTEGER'
    UNION ALL SELECT '城市', 'city', 'VARCHAR'
    UNION ALL SELECT '所在城市', 'city', 'VARCHAR'
    UNION ALL SELECT '居住城市', 'city', 'VARCHAR'
    UNION ALL SELECT '创建时间', 'created_at', 'DATETIME'
    UNION ALL SELECT '注册时间', 'created_at', 'DATETIME'
    UNION ALL SELECT '加入时间', 'created_at', 'DATETIME'
) cm
WHERE tm.db_table_name = 'users';

-- 插入订单表字段映射
INSERT OR REPLACE INTO column_mapping (table_id, natural_name, db_column_name, data_type) 
SELECT tm.id, cm.natural_name, cm.db_column_name, cm.data_type
FROM table_mapping tm
CROSS JOIN (
    SELECT '编号' as natural_name, 'id' as db_column_name, 'INTEGER' as data_type
    UNION ALL SELECT 'ID', 'id', 'INTEGER'
    UNION ALL SELECT '订单编号', 'id', 'INTEGER'
    UNION ALL SELECT '订单ID', 'id', 'INTEGER'
    UNION ALL SELECT '用户编号', 'user_id', 'INTEGER'
    UNION ALL SELECT '用户ID', 'user_id', 'INTEGER'
    UNION ALL SELECT '客户编号', 'user_id', 'INTEGER'
    UNION ALL SELECT '产品名称', 'product_name', 'VARCHAR'
    UNION ALL SELECT '商品名称', 'product_name', 'VARCHAR'
    UNION ALL SELECT '产品', 'product_name', 'VARCHAR'
    UNION ALL SELECT '商品', 'product_name', 'VARCHAR'
    UNION ALL SELECT '金额', 'amount', 'REAL'
    UNION ALL SELECT '订单金额', 'amount', 'REAL'
    UNION ALL SELECT '总金额', 'amount', 'REAL'
    UNION ALL SELECT '价格', 'amount', 'REAL'
    UNION ALL SELECT '费用', 'amount', 'REAL'
    UNION ALL SELECT '订单日期', 'order_date', 'DATE'
    UNION ALL SELECT '日期', 'order_date', 'DATE'
    UNION ALL SELECT '下单日期', 'order_date', 'DATE'
    UNION ALL SELECT '购买日期', 'order_date', 'DATE'
    UNION ALL SELECT '状态', 'status', 'VARCHAR'
    UNION ALL SELECT '订单状态', 'status', 'VARCHAR'
    UNION ALL SELECT '处理状态', 'status', 'VARCHAR'
) cm
WHERE tm.db_table_name = 'orders';

-- 插入产品表字段映射
INSERT OR REPLACE INTO column_mapping (table_id, natural_name, db_column_name, data_type) 
SELECT tm.id, cm.natural_name, cm.db_column_name, cm.data_type
FROM table_mapping tm
CROSS JOIN (
    SELECT '编号' as natural_name, 'id' as db_column_name, 'INTEGER' as data_type
    UNION ALL SELECT 'ID', 'id', 'INTEGER'
    UNION ALL SELECT '产品编号', 'id', 'INTEGER'
    UNION ALL SELECT '产品ID', 'id', 'INTEGER'
    UNION ALL SELECT '名称', 'name', 'VARCHAR'
    UNION ALL SELECT '产品名称', 'name', 'VARCHAR'
    UNION ALL SELECT '商品名称', 'name', 'VARCHAR'
    UNION ALL SELECT '分类', 'category', 'VARCHAR'
    UNION ALL SELECT '类别', 'category', 'VARCHAR'
    UNION ALL SELECT '产品分类', 'category', 'VARCHAR'
    UNION ALL SELECT '商品分类', 'category', 'VARCHAR'
    UNION ALL SELECT '价格', 'price', 'REAL'
    UNION ALL SELECT '单价', 'price', 'REAL'
    UNION ALL SELECT '售价', 'price', 'REAL'
    UNION ALL SELECT '产品价格', 'price', 'REAL'
    UNION ALL SELECT '库存', 'stock', 'INTEGER'
    UNION ALL SELECT '库存数量', 'stock', 'INTEGER'
    UNION ALL SELECT '库存量', 'stock', 'INTEGER'
    UNION ALL SELECT '数量', 'stock', 'INTEGER'
) cm
WHERE tm.db_table_name = 'products';

-- 插入示例数据
-- 用户数据
INSERT OR REPLACE INTO users (id, name, age, city) VALUES
(1, '张三', 25, '北京'),
(2, '李四', 30, '上海'),
(3, '王五', 28, '广州'),
(4, '赵六', 35, '深圳'),
(5, '钱七', 22, '北京'),
(6, '孙八', 32, '上海'),
(7, '周九', 27, '杭州'),
(8, '吴十', 29, '成都'),
(9, '郑十一', 26, '北京'),
(10, '王十二', 31, '上海'),
(11, '李十三', 24, '广州'),
(12, '张十四', 33, '深圳'),
(13, '刘十五', 28, '杭州'),
(14, '陈十六', 29, '成都'),
(15, '杨十七', 27, '北京'),
(16, '黄十八', 30, '上海'),
(17, '周十九', 25, '广州'),
(18, '吴二十', 32, '深圳'),
(19, '徐二一', 26, '杭州'),
(20, '孙二二', 31, '成都');

-- 产品数据
INSERT OR REPLACE INTO products (id, name, category, price, stock) VALUES
(1, '笔记本电脑', '电子产品', 5999.00, 50),
(2, '智能手机', '电子产品', 3999.00, 100),
(3, '无线耳机', '电子产品', 299.00, 200),
(4, '办公桌', '家具', 899.00, 30),
(5, '人体工学椅', '家具', 1299.00, 25),
(6, '咖啡机', '家电', 1999.00, 40),
(7, '空气净化器', '家电', 1599.00, 35),
(8, '运动鞋', '服装', 599.00, 150),
(9, '平板电脑', '电子产品', 3299.00, 60),
(10, '智能手表', '电子产品', 1999.00, 80),
(11, '机械键盘', '电子产品', 599.00, 120),
(12, '显示器', '电子产品', 1899.00, 45),
(13, '书桌', '家具', 699.00, 35),
(14, '沙发', '家具', 2999.00, 15),
(15, '冰箱', '家电', 3999.00, 20),
(16, '洗衣机', '家电', 2499.00, 25),
(17, 'T恤', '服装', 99.00, 300),
(18, '牛仔裤', '服装', 299.00, 200),
(19, '羽绒服', '服装', 899.00, 100),
(20, '运动裤', '服装', 199.00, 250);

-- 订单数据
INSERT OR REPLACE INTO orders (id, user_id, product_name, amount, order_date, status) VALUES
(1, 1, '笔记本电脑', 5999.00, '2024-01-15', '已完成'),
(2, 1, '无线耳机', 299.00, '2024-01-20', '已完成'),
(3, 2, '智能手机', 3999.00, '2024-02-01', '已完成'),
(4, 2, '咖啡机', 1999.00, '2024-02-10', '待处理'),
(5, 3, '办公桌', 899.00, '2024-02-15', '已完成'),
(6, 3, '人体工学椅', 1299.00, '2024-02-20', '已完成'),
(7, 4, '空气净化器', 1599.00, '2024-03-01', '已完成'),
(8, 4, '运动鞋', 599.00, '2024-03-05', '待处理'),
(9, 5, '智能手机', 3999.00, '2024-03-10', '已完成'),
(10, 5, '无线耳机', 299.00, '2024-03-12', '已完成'),
(11, 6, '笔记本电脑', 5999.00, '2024-03-15', '待处理'),
(12, 6, '办公桌', 899.00, '2024-03-18', '已完成'),
(13, 7, '咖啡机', 1999.00, '2024-03-20', '已完成'),
(14, 7, '运动鞋', 599.00, '2024-03-22', '待处理'),
(15, 8, '空气净化器', 1599.00, '2024-03-25', '已完成'),
(16, 8, '人体工学椅', 1299.00, '2024-03-28', '已完成'),
(17, 9, '平板电脑', 3299.00, '2024-04-01', '已完成'),
(18, 9, '机械键盘', 599.00, '2024-04-05', '已完成'),
(19, 10, '智能手表', 1999.00, '2024-04-10', '已完成'),
(20, 10, '显示器', 1899.00, '2024-04-12', '待处理'),
(21, 11, '书桌', 699.00, '2024-04-15', '已完成'),
(22, 11, 'T恤', 99.00, '2024-04-18', '已完成'),
(23, 12, '沙发', 2999.00, '2024-04-20', '待处理'),
(24, 12, '冰箱', 3999.00, '2024-04-22', '已完成'),
(25, 13, '洗衣机', 2499.00, '2024-04-25', '已完成'),
(26, 13, '牛仔裤', 299.00, '2024-04-28', '已完成'),
(27, 14, '羽绒服', 899.00, '2024-05-01', '已完成'),
(28, 14, '运动裤', 199.00, '2024-05-05', '待处理'),
(29, 15, '智能手机', 3999.00, '2024-05-10', '已完成'),
(30, 15, '无线耳机', 299.00, '2024-05-12', '已完成'),
(31, 16, '笔记本电脑', 5999.00, '2024-05-15', '待处理'),
(32, 16, '显示器', 1899.00, '2024-05-18', '已完成'),
(33, 17, '平板电脑', 3299.00, '2024-05-20', '已完成'),
(34, 17, '机械键盘', 599.00, '2024-05-22', '已完成'),
(35, 18, '智能手表', 1999.00, '2024-05-25', '已完成'),
(36, 18, 'T恤', 99.00, '2024-05-28', '待处理'),
(37, 19, '书桌', 699.00, '2024-06-01', '已完成'),
(38, 19, '牛仔裤', 299.00, '2024-06-05', '已完成'),
(39, 20, '沙发', 2999.00, '2024-06-10', '待处理'),
(40, 20, '冰箱', 3999.00, '2024-06-12', '已完成');
