import pymysql

# 数据库连接配置
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4'
}

try:
    # 连接到 MySQL（不指定数据库）
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    print('连接 MySQL 成功！')
    
    # 1. 创建数据库
    cursor.execute('CREATE DATABASE IF NOT EXISTS crawler_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    print('✓ 数据库创建成功')
    
    # 2. 使用数据库
    cursor.execute('USE crawler_system')
    print('✓ 选择数据库成功')
    
    # 3. 创建用户表
    create_users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''
    cursor.execute(create_users_table)
    print('✓ 用户表创建成功')
    
    # 4. 创建任务表
    create_tasks_table = '''
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        url VARCHAR(500) NOT NULL,
        selector_config JSON,
        status VARCHAR(20) DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''
    cursor.execute(create_tasks_table)
    print('✓ 任务表创建成功')
    
    # 5. 创建数据表
    create_data_table = '''
    CREATE TABLE IF NOT EXISTS data (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        task_id INT NOT NULL,
        title VARCHAR(500),
        content TEXT,
        url VARCHAR(500),
        extra JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_task_id (task_id),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''
    cursor.execute(create_data_table)
    print('✓ 数据表创建成功')
    
    conn.commit()
    print('\n🎉 所有表创建完成！')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'错误: {e}')