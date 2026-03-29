
# Python爬虫系统 - 前端

## 项目简介

基于 Vue 3 + Element Plus + ECharts 的爬虫系统前端界面

## 技术栈

- Vue 3
- Vue Router 4
- Pinia
- Element Plus
- ECharts
- Axios
- Vite

## 项目结构

```
frontend/
├── public/
├── src/
│   ├── api/              # API接口
│   │   └── index.js
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── stores/           # 状态管理
│   │   └── user.js
│   ├── utils/            # 工具函数
│   │   └── request.js
│   ├── views/            # 页面组件
│   │   ├── Login.vue
│   │   ├── Layout.vue
│   │   ├── Tasks.vue
│   │   ├── TaskDetail.vue
│   │   └── Visualization.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 安装依赖

```bash
cd frontend
npm install
```

## 开发运行

```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

## 构建生产版本

```bash
npm run build
```

## 功能说明

### 1. 用户认证
- 用户注册
- 用户登录
- 用户登出
- 会话管理

### 2. 任务管理
- 创建爬虫任务
- 查看任务列表
- 运行爬虫任务
- 删除爬虫任务
- 查看任务详情

### 3. 数据管理
- 查看抓取数据
- 分页查询
- 导出Excel数据

### 4. 数据可视化
- 任务状态分布（饼图）
- 数据抓取趋势（折线图）
- 任务数据量统计（柱状图）

## 注意事项

1. 确保后端服务已在 `http://localhost:5000` 启动
2. 前端开发服务器已配置代理，无需跨域配置
3. 首次使用请先注册账号
