# Python爬虫系统 - 前端

## 技术栈

- Vue 3
- Vue Router 4
- Pinia
- Element Plus
- ECharts
- Axios
- Vite

## 已实现页面

- 登录/注册页
- 响应式主布局
- 任务管理页
- 任务详情页
- 数据管理页
- 可视化分析页

## 已实现能力

- 任务创建、运行、停止、删除
- 可视化配置抓取规则
- 任务进度与执行日志展示
- 数据搜索、删除、CSV/Excel 导出
- 任务状态分布、任务数据量、近 7 天抓取趋势图

## 本地运行

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:3001`

## 生产构建

```bash
npm run build
```

## 联调说明

- 前端开发服务器已代理 `/api` 到 `http://localhost:5000`
- 启动前请确保 Flask 后端和 MySQL 已经可用
