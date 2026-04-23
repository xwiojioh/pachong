
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
ENV_FILE = os.path.join(BACKEND_DIR, '.env')

load_dotenv(ENV_FILE)


class DBManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._local = threading.local()
        return cls._instance
    
    def get_connection(self):
        connection = getattr(self._local, 'connection', None)
        if connection is None or not connection.open:
            connection = pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'crawler_system'),
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            self._local.connection = connection
        else:
            connection.ping(reconnect=True)
        return connection
    
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
        connection = getattr(self._local, 'connection', None)
        if connection and connection.open:
            connection.close()
            self._local.connection = None


db_manager = DBManager()
