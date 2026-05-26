# 免费小说阅读平台 (NovelReader)

一个基于 Vue3 + Django 的免费小说阅读网站。

## 项目简介

免费小说阅读平台是一个为用户提供海量小说在线阅读服务的 Web 应用，采用前后端分离架构，支持小说浏览、搜索、收藏和在线阅读等功能。

## 技术栈

### 前端
- **框架**: Vue 3.4+
- **构建工具**: Vite 5.0+
- **语言**: TypeScript 5.0+
- **路由**: Vue Router 4.0+
- **状态管理**: Pinia 2.0+
- **UI 组件**: Element Plus 2.5+
- **HTTP 客户端**: Axios 1.6+
- **CSS 预处理器**: Less 4.0+

### 后端
- **框架**: Django 4.2+ / Django REST Framework 3.14+
- **语言**: Python 3.8+
- **数据库**: MySQL 5.7+ / SQLite (开发)
- **缓存**: Redis 4.0+

## 项目结构

```
novel-reader/
├── docs/                   # 项目文档
│   ├── proposal.md        # 项目建议书
│   ├── feasibility.md     # 可行性研究报告
│   ├── requirements.md     # 需求分析报告
│   ├── project_plan.md     # 项目计划书
│   ├── architecture.md     # 技术架构文档
│   ├── database.md         # 数据库设计文档
│   ├── api.md              # 接口定义文档
│   ├── roadmap.md          # 开发阶段文档
│   ├── Agents.md           # AI行为规则
│   └── roadmap.md          # 开发路线图
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/     # 公共组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/         # 状态管理
│   │   ├── views/          # 页面组件
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── backend/               # 后端项目
│   ├── project/           # 项目配置
│   ├── app/               # 应用模块
│   ├── manage.py          # 管理脚本
│   └── requirements.txt   # 依赖
├── testcases.md          # 测试用例
├── devlog.md             # 开发日志
└── README.md             # 项目文档
```

## 功能特性

- [ ] 首页推荐展示
- [ ] 小说分类浏览
- [ ] 小说详情查看
- [ ] 章节在线阅读
- [ ] 关键词搜索
- [ ] 用户注册登录
- [ ] 小说收藏
- [ ] 阅读记录
- [ ] 阅读器设置

## 快速开始

### 环境要求

- Node.js ≥ 16
- Python ≥ 3.8
- MySQL ≥ 5.7 (生产环境)
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd novel-reader
```

### 2. 前端安装

```bash
cd frontend
npm install
```

### 3. 后端安装

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 配置数据库

```bash
# 创建MySQL数据库
mysql -u root -p
CREATE DATABASE novel_reader CHARACTER SET utf8mb4;

# 修改backend/project/settings.py中的数据库配置
```

### 5. 运行迁移

```bash
cd backend
python manage.py migrate
```

### 6. 启动开发服务器

**前端：**
```bash
cd frontend
npm run dev
```

**后端：**
```bash
cd backend
python manage.py runserver
```

### 7. 访问项目

- 前端地址: http://localhost:5173
- 后端地址: http://localhost:8000

## 接口文档

详见 [docs/api.md](./docs/api.md)

## 数据库设计

详见 [docs/database.md](./docs/database.md)

## 开发指南

### 代码规范

- 前端: ESLint + Prettier
- 后端: PEP 8
- Git提交: 中文提交信息

### 分支管理

- `master`: 主分支
- `feature/*`: 功能分支
- `fix/*`: 修复分支

### 提交规范

```
[新增] 新功能
[修改] 功能变更
[修复] bug修复
[文档] 文档更新
```

## 项目文档

| 文档 | 说明 |
|------|------|
| [项目建议书](./docs/proposal.md) | 项目概述、背景、目标 |
| [可行性研究报告](./docs/feasibility.md) | 技术、经济、运营可行性 |
| [需求分析报告](./docs/requirements.md) | 功能需求、数据需求 |
| [项目计划书](./docs/project_plan.md) | 开发计划、资源配置 |
| [技术架构文档](./docs/architecture.md) | 系统架构、技术选型 |
| [数据库设计](./docs/database.md) | 表结构、索引设计 |
| [接口定义](./docs/api.md) | API接口规范 |
| [开发路线图](./docs/roadmap.md) | 版本规划、开发阶段 |
| [测试用例](./testcases.md) | 功能测试用例 |
| [开发日志](./devlog.md) | 开发进度记录 |

## 团队成员

| 角色 | 职责 |
|------|------|
| 产品负责人 | 需求把控、进度管理 |
| 前端开发 | Vue3页面开发 |
| 后端开发 | Django API开发 |
| 测试 | 功能测试、验收 |

## License

MIT License

## 联系方式

- 邮箱: support@novelreader.com
- 问题反馈: [Issues](https://github.com/your-repo/issues)
