
from app.utils.db import db_manager
import json


class Task:
    @staticmethod
    def create(user_id, name, url, selector_config=None):
        config_json = json.dumps(selector_config) if selector_config else None
        query = "INSERT INTO tasks (user_id, name, url, selector_config) VALUES (%s, %s, %s, %s)"
        return db_manager.execute_query(query, (user_id, name, url, config_json))
    
    @staticmethod
    def get_by_id(task_id):
        query = "SELECT * FROM tasks WHERE id = %s"
        task = db_manager.fetch_one(query, (task_id,))
        if task and task['selector_config']:
            task['selector_config'] = json.loads(task['selector_config'])
        return task
    
    @staticmethod
    def get_by_user(user_id, page=1, page_size=10):
        offset = (page - 1) * page_size
        query = "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
        tasks = db_manager.fetch_all(query, (user_id, page_size, offset))
        for task in tasks:
            if task['selector_config']:
                task['selector_config'] = json.loads(task['selector_config'])
        return tasks
    
    @staticmethod
    def update_status(task_id, status):
        query = "UPDATE tasks SET status = %s WHERE id = %s"
        return db_manager.execute_query(query, (status, task_id))
    
    @staticmethod
    def delete(task_id):
        query = "DELETE FROM tasks WHERE id = %s"
        return db_manager.execute_query(query, (task_id,))


class CrawledData:
    @staticmethod
    def create(task_id, title=None, content=None, url=None, extra=None):
        extra_json = json.dumps(extra) if extra else None
        query = "INSERT INTO data (task_id, title, content, url, extra) VALUES (%s, %s, %s, %s, %s)"
        return db_manager.execute_query(query, (task_id, title, content, url, extra_json))
    
    @staticmethod
    def get_by_task(task_id, page=1, page_size=20):
        offset = (page - 1) * page_size
        query = "SELECT * FROM data WHERE task_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
        data_list = db_manager.fetch_all(query, (task_id, page_size, offset))
        for data in data_list:
            if data['extra']:
                data['extra'] = json.loads(data['extra'])
        return data_list
    
    @staticmethod
    def count_by_task(task_id):
        query = "SELECT COUNT(*) as total FROM data WHERE task_id = %s"
        result = db_manager.fetch_one(query, (task_id,))
        return result['total'] if result else 0
    
    @staticmethod
    def delete_by_task(task_id):
        query = "DELETE FROM data WHERE task_id = %s"
        return db_manager.execute_query(query, (task_id,))
