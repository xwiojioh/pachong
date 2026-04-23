
from app.utils.db import db_manager
import json


_UNSET = object()


def _dump_json(value):
    if value in (None, '', [], {}):
        return None
    return json.dumps(value, ensure_ascii=False)


def _load_json(value, default):
    if value in (None, ''):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def _normalize_task(task):
    if not task:
        return task
    task['selector_config'] = _load_json(task.get('selector_config'), {})
    task['request_config'] = _load_json(task.get('request_config'), {})
    task['progress'] = int(task.get('progress') or 0)
    task['stop_requested'] = bool(task.get('stop_requested'))
    task['data_count'] = int(task.get('data_count') or 0)
    return task


def _normalize_data(record):
    if not record:
        return record
    record['extra'] = _load_json(record.get('extra'), {})
    return record


class Task:
    @staticmethod
    def create(user_id, name, url, selector_config=None, request_config=None):
        query = """
            INSERT INTO tasks (user_id, name, url, selector_config, request_config)
            VALUES (%s, %s, %s, %s, %s)
        """
        return db_manager.execute_query(
            query,
            (
                user_id,
                name,
                url,
                _dump_json(selector_config),
                _dump_json(request_config),
            ),
        )
    
    @staticmethod
    def get_by_id(task_id):
        query = """
            SELECT
                t.*,
                (SELECT COUNT(*) FROM data d WHERE d.task_id = t.id) AS data_count
            FROM tasks t
            WHERE t.id = %s
        """
        return _normalize_task(db_manager.fetch_one(query, (task_id,)))
    
    @staticmethod
    def get_by_user(user_id, page=1, page_size=10, keyword=None, status=None):
        offset = (page - 1) * page_size
        conditions = ["t.user_id = %s"]
        params = [user_id]

        if keyword:
            conditions.append("(t.name LIKE %s OR t.url LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword])
        if status:
            conditions.append("t.status = %s")
            params.append(status)

        where_clause = " AND ".join(conditions)
        total_query = f"SELECT COUNT(*) AS total FROM tasks t WHERE {where_clause}"
        total = db_manager.fetch_one(total_query, tuple(params))['total']

        query = f"""
            SELECT
                t.*,
                (SELECT COUNT(*) FROM data d WHERE d.task_id = t.id) AS data_count
            FROM tasks t
            WHERE {where_clause}
            ORDER BY t.updated_at DESC, t.created_at DESC
            LIMIT %s OFFSET %s
        """
        tasks = db_manager.fetch_all(query, tuple(params + [page_size, offset]))
        return {
            'list': [_normalize_task(task) for task in tasks],
            'total': total,
            'page': page,
            'page_size': page_size,
        }
    
    @staticmethod
    def update_runtime(
        task_id,
        *,
        status=_UNSET,
        progress=_UNSET,
        stop_requested=_UNSET,
        last_error=_UNSET,
        last_run_at=_UNSET,
        finished_at=_UNSET,
    ):
        updates = []
        params = []

        if status is not _UNSET:
            updates.append("status = %s")
            params.append(status)
        if progress is not _UNSET:
            updates.append("progress = %s")
            params.append(progress)
        if stop_requested is not _UNSET:
            updates.append("stop_requested = %s")
            params.append(1 if stop_requested else 0)
        if last_error is not _UNSET:
            updates.append("last_error = %s")
            params.append(last_error)
        if last_run_at is not _UNSET:
            updates.append("last_run_at = %s")
            params.append(last_run_at)
        if finished_at is not _UNSET:
            updates.append("finished_at = %s")
            params.append(finished_at)

        if not updates:
            return 0

        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s"
        params.append(task_id)
        return db_manager.execute_query(query, tuple(params))

    @staticmethod
    def request_stop(task_id):
        query = "UPDATE tasks SET stop_requested = 1 WHERE id = %s"
        return db_manager.execute_query(query, (task_id,))

    @staticmethod
    def clear_stop_request(task_id):
        query = "UPDATE tasks SET stop_requested = 0 WHERE id = %s"
        return db_manager.execute_query(query, (task_id,))
    
    @staticmethod
    def delete(task_id):
        query = "DELETE FROM tasks WHERE id = %s"
        return db_manager.execute_query(query, (task_id,))

    @staticmethod
    def count_by_status(user_id):
        query = """
            SELECT status, COUNT(*) AS total
            FROM tasks
            WHERE user_id = %s
            GROUP BY status
        """
        rows = db_manager.fetch_all(query, (user_id,))
        return {row['status']: row['total'] for row in rows}

    @staticmethod
    def get_task_data_stats(user_id, limit=20):
        query = """
            SELECT
                t.id,
                t.name,
                COUNT(d.id) AS data_count
            FROM tasks t
            LEFT JOIN data d ON d.task_id = t.id
            WHERE t.user_id = %s
            GROUP BY t.id, t.name
            ORDER BY data_count DESC, t.updated_at DESC
            LIMIT %s
        """
        return db_manager.fetch_all(query, (user_id, limit))


class TaskLog:
    @staticmethod
    def create(task_id, message, level='info'):
        query = "INSERT INTO task_logs (task_id, level, message) VALUES (%s, %s, %s)"
        return db_manager.execute_query(query, (task_id, level, message))

    @staticmethod
    def get_by_task(task_id, page=1, page_size=50):
        offset = (page - 1) * page_size
        total_query = "SELECT COUNT(*) AS total FROM task_logs WHERE task_id = %s"
        total = db_manager.fetch_one(total_query, (task_id,))['total']
        query = """
            SELECT *
            FROM task_logs
            WHERE task_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT %s OFFSET %s
        """
        logs = db_manager.fetch_all(query, (task_id, page_size, offset))
        return {
            'list': logs,
            'total': total,
            'page': page,
            'page_size': page_size,
        }

    @staticmethod
    def delete_by_task(task_id):
        query = "DELETE FROM task_logs WHERE task_id = %s"
        return db_manager.execute_query(query, (task_id,))


class CrawledData:
    @staticmethod
    def create(task_id, title=None, content=None, url=None, extra=None):
        query = "INSERT INTO data (task_id, title, content, url, extra) VALUES (%s, %s, %s, %s, %s)"
        return db_manager.execute_query(query, (task_id, title, content, url, _dump_json(extra)))
    
    @staticmethod
    def get_by_task(task_id, page=1, page_size=20, keyword=None):
        offset = (page - 1) * page_size
        conditions = ["task_id = %s"]
        params = [task_id]
        if keyword:
            conditions.append("(title LIKE %s OR content LIKE %s OR url LIKE %s OR CAST(extra AS CHAR) LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword, like_keyword, like_keyword])
        where_clause = " AND ".join(conditions)
        total_query = f"SELECT COUNT(*) AS total FROM data WHERE {where_clause}"
        total = db_manager.fetch_one(total_query, tuple(params))['total']
        query = f"""
            SELECT *
            FROM data
            WHERE {where_clause}
            ORDER BY created_at DESC, id DESC
            LIMIT %s OFFSET %s
        """
        data_list = db_manager.fetch_all(query, tuple(params + [page_size, offset]))
        return {
            'list': [_normalize_data(data) for data in data_list],
            'total': total,
            'page': page,
            'page_size': page_size,
        }
    
    @staticmethod
    def count_by_task(task_id):
        query = "SELECT COUNT(*) as total FROM data WHERE task_id = %s"
        result = db_manager.fetch_one(query, (task_id,))
        return result['total'] if result else 0

    @staticmethod
    def count_by_user(user_id):
        query = """
            SELECT COUNT(*) AS total
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE t.user_id = %s
        """
        result = db_manager.fetch_one(query, (user_id,))
        return result['total'] if result else 0
    
    @staticmethod
    def delete_by_task(task_id):
        query = "DELETE FROM data WHERE task_id = %s"
        return db_manager.execute_query(query, (task_id,))

    @staticmethod
    def get_all_by_user(user_id, page=1, page_size=20, keyword=None, task_id=None):
        offset = (page - 1) * page_size
        conditions = ["t.user_id = %s"]
        params = [user_id]

        if task_id:
            conditions.append("d.task_id = %s")
            params.append(task_id)
        if keyword:
            conditions.append("(d.title LIKE %s OR d.content LIKE %s OR d.url LIKE %s OR CAST(d.extra AS CHAR) LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword, like_keyword, like_keyword])

        where_clause = " AND ".join(conditions)
        total_query = f"""
            SELECT COUNT(*) AS total
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE {where_clause}
        """
        total = db_manager.fetch_one(total_query, tuple(params))['total']
        query = f"""
            SELECT d.*, t.name AS task_name
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE {where_clause}
            ORDER BY d.created_at DESC, d.id DESC
            LIMIT %s OFFSET %s
        """
        rows = db_manager.fetch_all(query, tuple(params + [page_size, offset]))
        return {
            'list': [_normalize_data(row) for row in rows],
            'total': total,
            'page': page,
            'page_size': page_size,
        }

    @staticmethod
    def export_by_user(user_id, keyword=None, task_id=None):
        conditions = ["t.user_id = %s"]
        params = [user_id]

        if task_id:
            conditions.append("d.task_id = %s")
            params.append(task_id)
        if keyword:
            conditions.append("(d.title LIKE %s OR d.content LIKE %s OR d.url LIKE %s OR CAST(d.extra AS CHAR) LIKE %s)")
            like_keyword = f"%{keyword}%"
            params.extend([like_keyword, like_keyword, like_keyword, like_keyword])

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT d.*, t.name AS task_name
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE {where_clause}
            ORDER BY d.created_at DESC, d.id DESC
        """
        rows = db_manager.fetch_all(query, tuple(params))
        return [_normalize_data(row) for row in rows]

    @staticmethod
    def delete_by_id(data_id, user_id):
        query = """
            DELETE d
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE d.id = %s AND t.user_id = %s
        """
        return db_manager.execute_query(query, (data_id, user_id))

    @staticmethod
    def get_by_id(data_id, user_id):
        query = """
            SELECT d.*, t.name AS task_name
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE d.id = %s AND t.user_id = %s
        """
        return _normalize_data(db_manager.fetch_one(query, (data_id, user_id)))

    @staticmethod
    def get_daily_counts(user_id, days=7):
        query = """
            SELECT DATE(d.created_at) AS day, COUNT(*) AS total
            FROM data d
            INNER JOIN tasks t ON d.task_id = t.id
            WHERE t.user_id = %s AND d.created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(d.created_at)
            ORDER BY day ASC
        """
        return db_manager.fetch_all(query, (user_id, days))
