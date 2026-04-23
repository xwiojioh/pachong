from flask import Blueprint, jsonify, request

from app.models.task import CrawledData
from app.utils.auth import get_session_user, login_required
from app.utils.export import build_export_response

data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('', methods=['GET'])
@login_required
def get_data_list():
    user = get_session_user()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    keyword = request.args.get('keyword', '').strip() or None
    task_id = request.args.get('task_id', type=int)
    result = CrawledData.get_all_by_user(user['user_id'], page, page_size, keyword=keyword, task_id=task_id)
    return jsonify({'code': 200, 'data': result})


@data_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    user = get_session_user()
    keyword = request.args.get('keyword', '').strip() or None
    task_id = request.args.get('task_id', type=int)
    export_format = (request.args.get('format') or 'excel').lower()
    if export_format not in {'excel', 'csv'}:
        return jsonify({'code': 400, 'message': '仅支持导出 csv 或 excel 格式'}), 400

    rows = CrawledData.export_by_user(user['user_id'], keyword=keyword, task_id=task_id)
    filename_prefix = 'crawler_data'
    if task_id:
        filename_prefix = f'task_{task_id}_data'
    return build_export_response(rows, export_format, filename_prefix)


@data_bp.route('/<int:data_id>', methods=['DELETE'])
@login_required
def delete_data(data_id):
    user = get_session_user()
    record = CrawledData.get_by_id(data_id, user['user_id'])
    if not record:
        return jsonify({'code': 404, 'message': '数据不存在'}), 404

    CrawledData.delete_by_id(data_id, user['user_id'])
    return jsonify({'code': 200, 'message': '删除成功'})
