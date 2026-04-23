import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, 'backend')

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.utils.schema import ensure_database_schema


if __name__ == '__main__':
    try:
        ensure_database_schema()
        print('MySQL 数据库和表结构初始化完成')
    except Exception as error:
        print(f'初始化失败: {error}')
        sys.exit(1)
