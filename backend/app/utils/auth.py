from functools import wraps

from flask import jsonify, session


def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        return func(*args, **kwargs)

    return wrapped


def get_session_user():
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
    }
