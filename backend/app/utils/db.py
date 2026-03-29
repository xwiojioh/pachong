
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()


class DBManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def get_connection(self):
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'crawler_system'),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
        return self._connection
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
    
    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def close(self):
        if self._connection and self._connection.open:
            self._connection.close()


db_manager = DBManager()
