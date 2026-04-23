from datetime import date, timedelta

from flask import Blueprint, jsonify

from app.models.task import CrawledData, Task
from app.utils.auth import get_session_user, login_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    user = get_session_user()
    status_count = Task.count_by_status(user['user_id'])
    task_data_stats = Task.get_task_data_stats(user['user_id'], limit=20)
    total_tasks = sum(status_count.values())
    total_records = CrawledData.count_by_user(user['user_id'])

    raw_daily_counts = CrawledData.get_daily_counts(user['user_id'], days=6)
    daily_map = {
        row['day'].strftime('%Y-%m-%d'): row['total']
        for row in raw_daily_counts
        if row.get('day')
    }
    daily_counts = []
    for offset in range(6, -1, -1):
        current_day = date.today() - timedelta(days=offset)
        key = current_day.strftime('%Y-%m-%d')
        daily_counts.append({'date': key, 'count': daily_map.get(key, 0)})

    return jsonify(
        {
            'code': 200,
            'data': {
                'summary': {
                    'total_tasks': total_tasks,
                    'total_records': total_records,
                    'running_tasks': status_count.get('running', 0),
                    'completed_tasks': status_count.get('completed', 0),
                },
                'status_distribution': [
                    {'status': 'pending', 'count': status_count.get('pending', 0)},
                    {'status': 'running', 'count': status_count.get('running', 0)},
                    {'status': 'stopped', 'count': status_count.get('stopped', 0)},
                    {'status': 'completed', 'count': status_count.get('completed', 0)},
                    {'status': 'failed', 'count': status_count.get('failed', 0)},
                ],
                'task_data_counts': task_data_stats,
                'daily_counts': daily_counts,
            },
        }
    )
