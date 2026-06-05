# 墨香书阁（InkFiction）

基于 Vue3 + Django6 的在线小说阅读平台，提供小说浏览、搜索、收藏、在线阅读等完整功能，支持读者、作者、管理员三种角色，配备 Scrapy 爬虫自动采集数据。

> **技术栈**：Vue3 + TypeScript + Element Plus + Vite5 | Django 6 + DRF + MySQL | Scrapy &nbsp;|&nbsp; **许可证**：All rights reserved

---

## 功能模块

### 读者端功能

| 页面 | 功能说明 |
|------|----------|
| 首页 | 轮播推荐、搜索框、快捷分类入口 |
| 小说列表 | 分类筛选（类型/状态/字数）、排序（最新/最热/完结）、分页浏览 |
| 小说详情 | 封面展示、简介信息、章节目录树、评论区 |
| 章节阅读器 | 翻页/上下章切换、主题切换（护眼/夜间/羊皮纸）、字号调节、书签添加、阅读进度自动保存 |
| 排行榜 | 人气榜、新书榜、完结榜、畅销榜四大维度 |
| 搜索结果 | 关键词搜索、结果高亮展示 |
| 个人中心 | 信息编辑、头像上传、我的收藏、阅读历史 |
| 登录注册 | 用户注册、JWT登录认证 |

### 作者端功能

| 页面 | 功能说明 |
|------|----------|
| 作者中心 | 作品总览、数据统计 |
| 小说编辑 | 基本信息、封面图片上传、状态管理 |
| 章节管理 | 章节列表、拖拽排序、批量操作 |
| 章节编辑 | 富文本编辑、TXT文件导入 |

### 管理后台

| 页面 | 功能说明 |
|------|----------|
| 数据仪表盘 | 用户数/小说数/评论数/今日新增等多维统计图表 |
| 书籍管理 | 高级筛选、批量审核/删除、分页展示 |
| 章节管理 | TXT批量上传、章节内容审核 |
| 广告管理 | 广告位配置、上下架管理 |
| 公告管理 | 系统公告发布与编辑 |
| 分类管理 | 小说分类的增删改查 |
| 违规记录 | 用户举报处理、违规内容查看 |
| 操作日志 | 系统操作审计日志 |

### 数据采集

- **Scrapy爬虫**：自动采集小说元数据和章节内容
- 支持多站点采集、增量更新、去重处理

## 技术栈

- **前端**: Vue 3 + TypeScript 5 + Element Plus 2.5+ + Vite 5 + Vue Router 4 + Pinia 2 + Axios + Less
- **后端**: Django 6 + Django REST Framework + PyMySQL + django-cors-headers
- **数据库**: MySQL 8.0 (utf8mb4)
- **缓存**: Redis (会话/热点数据)
- **认证**: JWT Token (djangorestframework-simplejwt)
- **异步任务**: Celery + Redis (可选)
- **爬虫**: Scrapy框架
- **文件存储**: 本地文件系统 (Pillow图片处理)

## 系统截图

<div align="center">
  <p align="center"><b>首页界面</b></p>
  <img src="screenshots/home.png" width="100%" alt="首页界面" />
  <br/><br/>
  <p align="center"><b>小说详情</b></p>
  <img src="screenshots/novel-detail.png" width="100%" alt="小说详情" />
  <br/><br/>
  <p align="center"><b>章节阅读器</b></p>
  <img src="screenshots/reader.png" width="100%" alt="章节阅读器" />
  <br/><br/>
  <p align="center"><b>管理后台仪表盘</b></p>
  <img src="screenshots/admin-dashboard.png" width="100%" alt="管理后台" />
</div>

## 快速开始

### 环境要求

- Node.js ≥ 18
- Python ≥ 3.10
- MySQL ≥ 8.0
- Redis ≥ 6.0 (推荐)

### 安装与运行

```bash
# 1. 克隆仓库
git clone [仓库地址]
cd inkfiction

# 2. 后端环境配置
cd novel_backend
python -m venv venv
venv\Scripts\activate  # Windows激活虚拟环境
pip install django djangorestframework django-cors-headers Pillow chardet celery redis python-dotenv pymysql

# 3. 配置数据库
# 创建MySQL数据库: CREATE DATABASE inkfiction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# 修改 novel_backend/novels/settings.py 中的 DATABASES 配置

# 4. 运行数据库迁移
python manage.py migrate

# 5. 启动后端服务 (端口8000)
python manage.py runserver

# 6. 新开终端，启动前端开发服务 (端口5173)
cd novel_frontend
npm install
npm run dev
```

打开 `http://localhost:5173`，即可访问墨香书阁在线小说阅读平台。

> 📝 **快速开始必须可执行**：确保MySQL已创建数据库并正确配置settings.py中的连接信息，前后端分别启动后通过CORS互通。

---

## 核心特性

### 阅读体验
- **沉浸式阅读**：支持翻页模式、多种阅读主题切换（默认/护眼/夜间/羊皮纸）、字号自由调节
- **智能书签**：一键添加书签，阅读进度自动保存与恢复，跨设备同步
- **章节导航**：目录树快速跳转、上下章无缝切换、阅读位置记忆

### 内容发现
- **多维排行**：人气榜、新书榜、完结榜、畅销榜实时更新
- **智能搜索**：关键词全文检索、搜索结果高亮展示
- **个性化推荐**：首页轮播推荐、热门分类快捷入口

### 社交互动
- **评论系统**：小说级评论、点赞互动、违规举报
- **收藏管理**：一键收藏、收藏列表快速访问
- **阅读历史**：自动记录阅读轨迹、续读入口

### 创作工具
- **作者工作台**：作品管理、数据看板、收益概览
- **富文本编辑**：章节内容可视化编辑、TXT批量导入
- **封面上传**：支持JPG/PNG格式、自动压缩优化

### 运营管理
- **后台仪表盘**：多维度数据统计、趋势图表可视化
- **内容审核**：书籍/章节批量操作、违规记录追踪
- **运营工具**：广告管理、公告发布、分类维护、操作日志审计

### 技术架构
- **前后端分离**：Vue3 SPA + DRF RESTful API，独立部署扩展性强
- **JWT认证**：无状态Token认证，安全可靠
- **响应式设计**：适配桌面端与移动端浏览器
- **自动化采集**：Scrapy爬虫定时抓取，数据持续更新

> 📝 **写法提示**：每个特性用 **加粗关键词** 开头，后跟一句话说明用户能得到什么价值。

---

## 项目结构

```
inkfiction/
├── novel_frontend/                  # Vue3前端项目
│   ├── src/
│   │   ├── api/                    # API接口封装
│   │   ├── assets/                 # 静态资源
│   │   ├── components/             # 公共组件
│   │   ├── router/                 # Vue Router路由配置
│   │   ├── stores/                 # Pinia状态管理
│   │   ├── utils/                  # 工具函数
│   │   └── views/                  # 页面组件
│   │       ├── Home.vue            # 首页(轮播/搜索/快捷入口)
│   │       ├── NovelDetail.vue     # 小说详情(封面/简介/目录/评论)
│   │       ├── Reader.vue          # 章节阅读器(翻页/主题/字号/书签)
│   │       ├── NovelList.vue       # 小说列表(筛选/排序/分页)
│   │       ├── Rankings.vue        # 排行榜(人气/新书/完结/畅销)
│   │       ├── Search.vue          # 搜索结果
│   │       ├── UserCenter.vue      # 个人中心(信息/头像/收藏/历史)
│   │       ├── Login.vue           # 登录注册
│   │       ├── AuthorCenter.vue    # 作者中心
│   │       ├── AuthorNovelEdit.vue # 小说编辑
│   │       ├── AuthorChapterList.vue # 章节管理
│   │       ├── AuthorChapterEdit.vue # 章节编辑
│   │       └── admin/              # 管理后台页面
│   │           ├── AdminLayout.vue    # 后台布局
│   │           ├── Dashboard.vue      # 数据仪表盘
│   │           ├── Books.vue          # 书籍管理
│   │           ├── Chapters.vue       # 章节管理
│   │           ├── Advertisements.vue # 广告管理
│   │           ├── Announcements.vue  # 公告管理
│   │           ├── Categories.vue     # 分类管理
│   │           ├── Violations.vue     # 违规记录
│   │           └── Logs.vue           # 操作日志
│   ├── package.json
│   └── vite.config.ts
├── novel_backend/                   # Django后端项目
│   ├── novels/                      # 主应用模块
│   │   ├── models.py               # 数据模型(User/Novel/Chapter/Comment等)
│   │   ├── views.py                # 公开API(小说列表/详情/章节/评论/搜索/排行)
│   │   ├── user_views.py           # 用户API(注册/登录/个人信息/收藏/书签)
│   │   ├── author_views.py         # 作者API(小说CRUD/章节管理/封面上传/TXT上传)
│   │   ├── admin_views.py          # 后台管理API(全部CRUD/批量操作/统计/日志)
│   │   ├── auth.py                 # JWT认证逻辑
│   │   ├── urls.py                 # 路由配置
│   │   ├── admin.py                # Django Admin配置
│   │   ├── apps.py                 # 应用配置
│   │   └── migrations/             # 数据库迁移文件
│   ├── manage.py                   # Django管理脚本
│   ├── requirements.txt            # Python依赖
│   └── settings.py                 # 项目配置
├── CopyBook/
│   └── copyBook-master/
│       └── bookspider/             # Scrapy爬虫项目
│           ├── spiders/            # 爬虫脚本
│           ├── items.py            # 数据模型
│           ├── pipelines.py        # 数据处理管道
│           └── settings.py         # 爬虫配置
├── docs/                           # 项目文档(14份)
│   ├── 01-项目建议书.md            # 项目概述、背景、目标与范围
│   ├── 02-可行性研究报告.md        # 技术、经济、运营可行性分析
│   ├── 03-需求分析报告.md          # 功能需求、非功能需求、用例分析
│   ├── 04-项目计划书.md            # WBS分解、甘特图、资源配置
│   ├── 05-技术架构设计.md          # 系统架构图、技术选型、部署方案
│   ├── 06-数据库设计.md            # ER图、表结构、索引策略
│   ├── 07-API接口文档.md           # RESTful API规范、请求响应示例
│   ├── 08-UI原型设计.md            # 页面线框图、交互流程说明
│   ├── 09-测试计划与用例.md        # 测试策略、用例设计、验收标准
│   ├── 10-开发阶段文档.md          # 迭代记录、里程碑、问题跟踪
│   ├── 11-AI辅助开发报告.md        # AI工具使用情况、效率提升分析
│   ├── 12-README.md               # 项目说明文档(本文件)
│   ├── 13-演示视频脚本.md          # 功能演示流程、讲解要点
│   └── 14-总结与反思.md           # 项目复盘、经验教训、改进方向
└── screenshots/                    # 系统截图
```

---

## 核心API端点

### 认证模块
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录(返回JWT Token)
- `GET /api/auth/userinfo/` - 获取当前用户信息
- `PUT /api/auth/update_profile/` - 更新个人资料

### 小说公开API
- `GET /api/novels/` - 获取小说列表(支持筛选/排序/分页)
- `GET /api/novels/{id}/` - 获取小说详情
- `GET /api/novels/{id}/chapters/` - 获取章节列表
- `GET /api/comments/` - 获取评论列表
- `POST /api/comments/` - 发表评论
- `GET /api/rankings/` - 获取排行榜数据
- `GET /api/search/` - 关键词搜索

### 作者API
- `GET /api/author/novels/` - 获取作者作品列表
- `POST /api/author/novels/` - 创建新小说
- `PUT /api/author/novels/{id}/` - 更新小说信息
- `POST /api/author/novels/upload_cover/` - 上传小说封面
- `GET /api/author/chapters/?novel_id={id}` - 获取章节列表
- `POST /api/author/chapters/` - 创建章节
- `PUT /api/author/chapters/{id}/` - 更新章节内容
- `POST /api/author/chapters/upload_txt/` - TXT批量导入章节

### 管理后台API
- `GET /api/admin/dashboard/stats/` - 仪表盘统计数据
- `GET /api/admin/books/` - 书籍列表(高级筛选)
- `PUT /api/admin/books/{id}/audit/` - 审核书籍
- `DELETE /api/admin/books/batch_delete/` - 批量删除书籍
- `GET /api/admin/chapters/` - 章节列表
- `POST /api/admin/chapters/upload_txt/` - TXT批量上传章节
- `GET /api/admin/advertisements/` - 广告列表
- `GET /api/admin/announcements/` - 公告列表
- `GET /api/admin/categories/` - 分类列表
- `GET /api/admin/violations/` - 违规记录
- `GET /api/admin/logs/` - 操作日志

---

## 版本

v1.0，详见 [10-开发阶段文档.md](./docs/10-开发阶段文档.md)

---

## 项目文档索引

| 序号 | 文档名称 | 文件路径 | 说明 |
|------|----------|----------|------|
| 01 | 项目建议书 | [docs/01-项目建议书.md](./docs/01-项目建议书.md) | 项目背景、目标、范围界定 |
| 02 | 可行性研究报告 | [docs/02-可行性研究报告.md](./docs/02-可行性研究报告.md) | 技术/经济/运营可行性论证 |
| 03 | 需求分析报告 | [docs/03-需求分析报告.md](./docs/03-需求分析报告.md) | 功能/非功能需求、用例建模 |
| 04 | 项目计划书 | [docs/04-项目计划书.md](./docs/04-项目计划书.md) | WBS分解、进度安排、资源规划 |
| 05 | 技术架构设计 | [docs/05-技术架构设计.md](./docs/05-技术架构设计.md) | 系统架构、技术选型、部署方案 |
| 06 | 数据库设计 | [docs/06-数据库设计.md](./docs/06-数据库设计.md) | ER模型、表结构、索引策略 |
| 07 | API接口文档 | [docs/07-API接口文档.md](./docs/07-API接口文档.md) | RESTful规范、请求响应示例 |
| 08 | UI原型设计 | [docs/08-UI原型设计.md](./docs/08-UI原型设计.md) | 页面原型、交互流程 |
| 09 | 测试计划与用例 | [docs/09-测试计划与用例.md](./docs/09-测试计划与用例.md) | 测试策略、用例设计、验收标准 |
| 10 | 开发阶段文档 | [docs/10-开发阶段文档.md](./docs/10-开发阶段文档.md) | 迭代记录、里程碑、问题跟踪 |
| 11 | AI辅助开发报告 | [docs/11-AI辅助开发报告.md](./docs/11-AI辅助开发报告.md) | AI工具使用、效率提升分析 |
| 12 | README文档 | [docs/12-README.md](./docs/12-README.md) | 项目说明、快速开始指南 |
| 13 | 演示视频脚本 | [docs/13-演示视频脚本.md](./docs/13-演示视频脚本.md) | 功能演示流程、讲解要点 |
| 14 | 总结与反思 | [docs/14-总结与反思.md](./docs/14-总结与反思.md) | 项目复盘、经验教训、改进方向 |

---

© 2026 墨香书阁（InkFiction）团队. All rights reserved.
