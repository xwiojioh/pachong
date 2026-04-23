from flask import Blueprint, jsonify, request

from app.models.task import CrawledData, Task, TaskLog
from app.services.task_runner import task_runner
from app.utils.auth import get_session_user, login_required
from app.utils.export import build_export_response
from app.utils.task_presets import (
    apply_max_items_to_selector_config,
    detect_task_preset,
    merge_request_config,
    normalize_request_config_for_form,
    normalize_request_config_from_form,
)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


def _get_owned_task(task_id, user_id):
    task = Task.get_by_id(task_id)
    if not task or task['user_id'] != user_id:
        return None
    return task


@tasks_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    user = get_session_user()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    keyword = request.args.get('keyword', '').strip() or None
    status = request.args.get('status', '').strip() or None
    result = Task.get_by_user(user['user_id'], page, page_size, keyword=keyword, status=status)
    return jsonify({'code': 200, 'data': result})


@tasks_bp.route('', methods=['POST'])
@login_required
def create_task():
    user = get_session_user()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    url = (data.get('url') or '').strip()
    max_items = data.get('max_items')
    selector_config = data.get('selector_config') or {}
    request_config = normalize_request_config_from_form(data.get('request_config') or {})

    if not url:
        return jsonify({'code': 400, 'message': '目标URL不能为空'}), 400

    preset = detect_task_preset(url)
    fields = selector_config.get('fields') or []
    has_manual_fields = bool(fields)

    if not has_manual_fields:
        if not preset.get('supported', True):
            warning = preset.get('warning') or '当前网址暂不支持简易模式'
            return jsonify({'code': 400, 'message': warning, 'data': {'recommended_url': preset.get('recommended_url', '')}}), 400
        selector_config = preset.get('selector_config') or {}
        request_config = merge_request_config(preset.get('request_config'), request_config)

    selector_config = apply_max_items_to_selector_config(
        selector_config,
        max_items,
        override_detail_max=not has_manual_fields,
    )

    if not name:
        name = preset.get('name') or '网页抓取任务'

    try:
        task_id = Task.create(user['user_id'], name, url, selector_config, request_config)
        return jsonify({'code': 200, 'message': '创建成功', 'data': {'task_id': task_id}})
    except Exception as error:
        return jsonify({'code': 500, 'message': f'创建失败: {str(error)}'}), 500


@tasks_bp.route('/detect', methods=['POST'])
@login_required
def detect_task():
    data = request.get_json() or {}
    url = (data.get('url') or '').strip()
    preset = detect_task_preset(url)
    preset['request_config_form'] = normalize_request_config_for_form(preset.get('request_config'))
    return jsonify({'code': 200, 'data': preset})


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404
    return jsonify({'code': 200, 'data': task})


@tasks_bp.route('/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    success, message = task_runner.start(task_id)
    status_code = 200 if success else 400
    return jsonify({'code': status_code, 'message': message}), status_code


@tasks_bp.route('/<int:task_id>/stop', methods=['POST'])
@login_required
def stop_task(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    success, message = task_runner.stop(task_id, task)
    status_code = 200 if success else 400
    return jsonify({'code': status_code, 'message': message}), status_code


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    if task['status'] == 'running':
        return jsonify({'code': 400, 'message': '请先停止运行中的任务'}), 400

    TaskLog.delete_by_task(task_id)
    CrawledData.delete_by_task(task_id)
    Task.delete(task_id)
    return jsonify({'code': 200, 'message': '删除成功'})


@tasks_bp.route('/<int:task_id>/data', methods=['GET'])
@login_required
def get_task_data(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    keyword = request.args.get('keyword', '').strip() or None
    result = CrawledData.get_by_task(task_id, page, page_size, keyword=keyword)
    return jsonify({'code': 200, 'data': result})


@tasks_bp.route('/<int:task_id>/logs', methods=['GET'])
@login_required
def get_task_logs(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 50))
    result = TaskLog.get_by_task(task_id, page, page_size)
    return jsonify({'code': 200, 'data': result})


@tasks_bp.route('/<int:task_id>/export', methods=['GET'])
@login_required
def export_task_data(task_id):
    user = get_session_user()
    task = _get_owned_task(task_id, user['user_id'])
    if not task:
        return jsonify({'code': 404, 'message': '任务不存在'}), 404

    keyword = request.args.get('keyword', '').strip() or None
    export_format = (request.args.get('format') or 'excel').lower()
    if export_format not in {'excel', 'csv'}:
        return jsonify({'code': 400, 'message': '仅支持导出 csv 或 excel 格式'}), 400

    rows = CrawledData.export_by_user(user['user_id'], keyword=keyword, task_id=task_id)
    safe_name = task['name'].replace(' ', '_')
    return build_export_response(rows, export_format, f'{safe_name}_data')
