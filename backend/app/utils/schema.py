import os

import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
ENV_FILE = os.path.join(BACKEND_DIR, '.env')

load_dotenv(ENV_FILE)


def _base_connection(database=None):
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
        'cursorclass': DictCursor,
    }
    if database:
        config['database'] = database
    return pymysql.connect(**config)


def _ensure_column(cursor, table_name, column_name, ddl):
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (os.getenv('DB_NAME', 'crawler_system'), table_name, column_name),
    )
    exists = cursor.fetchone()['total'] > 0
    if not exists:
        cursor.execute(ddl)


def _ensure_index(cursor, table_name, index_name, ddl):
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
        """,
        (os.getenv('DB_NAME', 'crawler_system'), table_name, index_name),
    )
    exists = cursor.fetchone()['total'] > 0
    if not exists:
        cursor.execute(ddl)


def ensure_database_schema():
    db_name = os.getenv('DB_NAME', 'crawler_system')

    server_conn = _base_connection()
    try:
        with server_conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        server_conn.commit()
    finally:
        server_conn.close()

    db_conn = _base_connection(database=db_name)
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_username (username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    url VARCHAR(500) NOT NULL,
                    selector_config JSON NULL,
                    request_config JSON NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    progress INT DEFAULT 0,
                    stop_requested TINYINT(1) DEFAULT 0,
                    last_error TEXT NULL,
                    last_run_at DATETIME NULL,
                    finished_at DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
            cursor.execute(
                """
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
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS task_logs (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    task_id INT NOT NULL,
                    level VARCHAR(20) DEFAULT 'info',
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_task_logs_task_id (task_id),
                    INDEX idx_task_logs_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )

            _ensure_column(cursor, 'tasks', 'selector_config', "ALTER TABLE tasks ADD COLUMN selector_config JSON NULL AFTER url")
            _ensure_column(cursor, 'tasks', 'request_config', "ALTER TABLE tasks ADD COLUMN request_config JSON NULL AFTER selector_config")
            _ensure_column(cursor, 'tasks', 'status', "ALTER TABLE tasks ADD COLUMN status VARCHAR(20) DEFAULT 'pending' AFTER request_config")
            _ensure_column(cursor, 'tasks', 'progress', "ALTER TABLE tasks ADD COLUMN progress INT DEFAULT 0 AFTER status")
            _ensure_column(cursor, 'tasks', 'stop_requested', "ALTER TABLE tasks ADD COLUMN stop_requested TINYINT(1) DEFAULT 0 AFTER progress")
            _ensure_column(cursor, 'tasks', 'last_error', "ALTER TABLE tasks ADD COLUMN last_error TEXT NULL AFTER stop_requested")
            _ensure_column(cursor, 'tasks', 'last_run_at', "ALTER TABLE tasks ADD COLUMN last_run_at DATETIME NULL AFTER last_error")
            _ensure_column(cursor, 'tasks', 'finished_at', "ALTER TABLE tasks ADD COLUMN finished_at DATETIME NULL AFTER last_run_at")

            _ensure_index(cursor, 'tasks', 'idx_user_id', "CREATE INDEX idx_user_id ON tasks (user_id)")
            _ensure_index(cursor, 'tasks', 'idx_status', "CREATE INDEX idx_status ON tasks (status)")
            _ensure_index(cursor, 'data', 'idx_task_id', "CREATE INDEX idx_task_id ON data (task_id)")
            _ensure_index(cursor, 'data', 'idx_created_at', "CREATE INDEX idx_created_at ON data (created_at)")
            _ensure_index(cursor, 'task_logs', 'idx_task_logs_task_id', "CREATE INDEX idx_task_logs_task_id ON task_logs (task_id)")
            _ensure_index(cursor, 'task_logs', 'idx_task_logs_created_at', "CREATE INDEX idx_task_logs_created_at ON task_logs (created_at)")

        db_conn.commit()
    finally:
        db_conn.close()
