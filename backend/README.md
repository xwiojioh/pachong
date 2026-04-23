# Python爬虫系统 - 后端

## 功能概览

- 用户注册、登录、登出、会话校验
- 爬虫任务创建、列表、详情、运行、停止、删除
- 支持 `GET/POST` 请求
- 支持 Playwright 动态渲染抓取
- 支持自定义请求头、Cookie、请求体
- 支持 `CSS/XPath` 提取规则
- 支持任务进度、运行日志、失败原因记录
- 抓取数据分页查询、关键词搜索、删除
- 支持 `CSV/Excel` 导出
- 提供统计分析接口，供前端图表页使用

## 目录结构

```text
backend/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # API 路由
│   ├── services/        # 任务执行服务
│   ├── spider/          # 爬虫执行器
│   └── utils/           # 数据库、鉴权、导出、建表工具
├── app.py               # Flask 入口
├── init_db.sql          # MySQL 初始化脚本
├── requirements.txt     # Python 依赖
└── .env.example         # 环境变量示例
```

## 环境要求

- Python 3.9+
- MySQL 8.0+

## 安装与启动

### 1. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
./.venv/bin/pip install -r backend/requirements.txt
./.venv/bin/playwright install chromium
```

### 2. 配置环境变量

复制 `backend/.env.example` 为 `backend/.env`，按实际 MySQL 环境修改：

```env
SECRET_KEY=change-me
SERVER_PORT=5000
FLASK_DEBUG=True

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=crawler_system
```

### 3. 初始化数据库

方式一：执行 SQL 脚本

```bash
mysql -u root -p < backend/init_db.sql
```

方式二：运行仓库根目录脚本

```bash
./.venv/bin/python create_db.py
```

应用启动时也会尝试自动补齐缺失的表和字段。

### 4. 启动服务

```bash
cd backend
../.venv/bin/python app.py
```

服务默认运行在 `http://localhost:5000`

## 主要接口

### 认证

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### 任务管理

- `GET /api/tasks`
- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/run`
- `POST /api/tasks/{task_id}/stop`
- `DELETE /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/data`
- `GET /api/tasks/{task_id}/logs`
- `GET /api/tasks/{task_id}/export?format=excel|csv`

### 数据管理

- `GET /api/data`
- `DELETE /api/data/{data_id}`
- `GET /api/data/export?format=excel|csv`

### 可视化统计

- `GET /api/analytics/overview`
