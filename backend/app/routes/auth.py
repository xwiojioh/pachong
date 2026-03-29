
from flask import Blueprint, request, jsonify, session
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    if User.get_by_username(username):
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400
    
    try:
        user_id = User.create(username, password)
        return jsonify({'code': 200, 'message': '注册成功', 'data': {'user_id': user_id}})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user = User.get_by_username(username)
    if not user or not User.verify_password(user, password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401
    
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user_id': user['id'],
            'username': user['username']
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'code': 200, 'message': '登出成功'})


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'code': 401, 'message': '未登录'}), 401
    
    return jsonify({
        'code': 200,
        'data': {
            'user_id': session['user_id'],
            'username': session['username']
        }
    })
