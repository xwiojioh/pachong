
from flask import Blueprint, request, jsonify, session
from app.models.task import Task, CrawledData
from app.spider.crawler import SimpleCrawler
import threading
import pandas as pd
from io import BytesIO

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def login_required(f):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '未登录'}), 401
        return f(*args, **kwargs)
    wrapped.__name__ = f.__name__
    return wrapped


@tasks_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    tasks = Task.get_by_user(session['user_id'], page, page_size)
    
    # 为每个任务添加数据量
    for task in tasks:
        task['data_count'] = CrawledData.count_by_task(task['id'])
    
    return jsonify({'code': 200, 'data': tasks})


@tasks_bp.route('', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    name = data.get('name')
    url = data.get('url')
    selector_config = data.get('selector_config')
    
    if not name or not url:
        return jsonify({'code': 400, 'message': '任务名称和URL不能为空'}), 400
    
    try:
        task_id = Task.create(session['user_id'], name, url, selector_config)
        return jsonify({'code': 200, 'message': '创建成功', 'data': {'task_id': task_id}})
    except Exception as e:
        return jsonify({'code': 500, 'message': f'创建失败: {str(e)}'}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != session['user_id']:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({'code': 200, 'data': task})


@tasks_bp.route('/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != session['user_id']:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    
    def crawler_thread():
        crawler = SimpleCrawler(task_id)
        crawler.run()
    
    thread = threading.Thread(target=crawler_thread)
    thread.start()
    
    return jsonify({'code': 200, 'message': '任务已启动'})


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != session['user_id']:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    
    CrawledData.delete_by_task(task_id)
    Task.delete(task_id)
    
    return jsonify({'code': 200, 'message': '删除成功'})


@tasks_bp.route('/<int:task_id>/data', methods=['GET'])
@login_required
def get_task_data(task_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != session['user_id']:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    data_list = CrawledData.get_by_task(task_id, page, page_size)
    total = CrawledData.count_by_task(task_id)
    
    return jsonify({
        'code': 200,
        'data': {
            'list': data_list,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })


@tasks_bp.route('/<int:task_id>/export', methods=['GET'])
@login_required
def export_data(task_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != session['user_id']:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    
    data_list = CrawledData.get_by_task(task_id, page=1, page_size=10000)
    
    df = pd.DataFrame(data_list)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    output.seek(0)
    
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={task["name"]}_data.xlsx'
    
    return response
