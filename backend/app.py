
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# 修复 Windows 下的编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
from app.utils.schema import ensure_database_schema

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)

ensure_database_schema()

from app.routes.auth import auth_bp
from app.routes.analytics import analytics_bp
from app.routes.data import data_bp
from app.routes.tasks import tasks_bp

app.register_blueprint(auth_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(data_bp)
app.register_blueprint(tasks_bp)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'code': 200, 'message': '服务正常运行'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'message': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'code': 500, 'message': '服务器内部错误'}), 500


if __name__ == '__main__':
    port = int(os.getenv('SERVER_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
