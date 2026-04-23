
from app.utils.db import db_manager
from werkzeug.security import generate_password_hash, check_password_hash
import os


PASSWORD_HASH_METHOD = os.getenv('PASSWORD_HASH_METHOD', 'pbkdf2:sha256')


class User:
    @staticmethod
    def create(username, password):
        hashed_password = generate_password_hash(password, method=PASSWORD_HASH_METHOD)
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        return db_manager.execute_query(query, (username, hashed_password))
    
    @staticmethod
    def get_by_username(username):
        query = "SELECT * FROM users WHERE username = %s"
        return db_manager.fetch_one(query, (username,))
    
    @staticmethod
    def get_by_id(user_id):
        query = "SELECT * FROM users WHERE id = %s"
        return db_manager.fetch_one(query, (user_id,))
    
    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user['password'], password)
