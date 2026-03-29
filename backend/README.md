
# Python爬虫系统 - 后端

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── models/          # 数据模型
│   │   ├── user.py
│   │   └── task.py
│   ├── routes/          # API路由
│   │   ├── auth.py      # 用户认证
│   │   └── tasks.py     # 任务管理
│   ├── spider/          # 爬虫模块
│   │   └── crawler.py
│   └── utils/           # 工具类
│       └── db.py        # 数据库管理
├── app.py                # Flask主应用
├── requirements.txt      # 依赖包
├── .env                  # 环境配置
├── init_db.sql           # 数据库初始化脚本
└── logs/                 # 日志目录
```

## 安装步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

1. 确保MySQL已安装并运行
2. 修改`.env`文件中的数据库配置：
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=crawler_system
   ```

### 3. 初始化数据库

使用MySQL客户端执行`init_db.sql`脚本：

```bash
mysql -u root -p < init_db.sql
```

或者在MySQL命令行中：

```sql
source d:/爬虫开发/backend/init_db.sql
```

### 4. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

## API文档

### 认证接口

#### 注册
- POST `/api/auth/register`
- Body: `{"username": "test", "password": "123456"}`

#### 登录
- POST `/api/auth/login`
- Body: `{"username": "test", "password": "123456"}`

#### 登出
- POST `/api/auth/logout`

#### 获取当前用户
- GET `/api/auth/me`

### 任务管理接口

#### 获取任务列表
- GET `/api/tasks?page=1&page_size=10`

#### 创建任务
- POST `/api/tasks`
- Body:
  ```json
  {
    "name": "测试任务",
    "url": "https://example.com",
    "selector_config": {
      "list_selector": ".item",
      "fields": {
        "title": {"type": "text", "selector": "h3"},
        "url": {"type": "attr", "selector": "a", "attr": "href"}
      }
    }
  }
  ```

#### 获取任务详情
- GET `/api/tasks/{task_id}`

#### 运行任务
- POST `/api/tasks/{task_id}/run`

#### 删除任务
- DELETE `/api/tasks/{task_id}`

#### 获取任务数据
- GET `/api/tasks/{task_id}/data?page=1&page_size=20`

#### 导出数据
- GET `/api/tasks/{task_id}/export`

## 技术栈

- Flask 2.3.3
- PyMySQL
- requests + BeautifulSoup4
- pandas + openpyxl
