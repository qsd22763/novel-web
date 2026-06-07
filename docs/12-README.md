# 墨香书阁（InkFiction）

基于 Vue3 + Django 的在线小说阅读平台 v2.0.0，提供小说浏览、搜索、收藏、在线阅读、每日签到、VIP充值等完整功能，支持读者、作者、管理员三种角色，配备 Scrapy 爬虫自动采集数据。

> **技术栈**：Vue3 + TypeScript + Element Plus + Vite | Django 4.2.14 + DRF + MySQL | Scrapy &nbsp;|&nbsp; **许可证**：All rights reserved &nbsp;|&nbsp; **版本**：v2.0.0 (2026-06-06)

---

## 功能模块

### 读者端功能（14页）

| 页面 | 功能说明 |
|------|----------|
| 首页 Home.vue | 12大板块（轮播推荐/人气榜单/新书榜单/专题推荐/改编推荐/总编推荐/分类快捷栏/签约新书/最近更新/完结榜/公告区/广告位） |
| 登录注册 Login.vue | 用户注册、登录认证（Session）、QQ/微信OAuth第三方登录、邮箱验证码 |
| 小说列表 NovelList.vue | 分类筛选（类型/状态/字数）、排序（最新/最热/完结）、分页浏览 |
| 小说详情 NovelDetail.vue | 封面展示、简介信息、章节目录树、评论区、收藏按钮 |
| 章节阅读器 Reader.vue | 翻页/上下章切换、主题切换（护眼/夜间/羊皮纸）、字号调节、书签添加、阅读进度自动保存 |
| 排行榜 Rankings.vue | 人气榜、新书榜、完结榜、畅销榜四大维度 |
| 搜索结果 Search.vue | 关键词搜索、结果高亮展示 |
| 个人中心 UserCenter.vue | 信息编辑、头像上传、我的收藏、阅读历史、书签管理、设置 |
| 每日签到 SignIn.vue | 每日签到领取奖励、连续签到额外奖励、签到历史记录、断签重计 |
| VIP充值 Recharge.vue | 充值套餐展示（月卡/季卡/年卡）、下单支付、订单查看、VIP状态显示 |
| 作者工作台 AuthorCenter.vue | 作品总览、数据统计入口 |

### 作者端功能（4页）

| 页面 | 功能说明 |
|------|----------|
| 作品管理 AuthorNovelEdit.vue | 基本信息、封面图片上传、状态管理、影视改编标记、总编推荐标记 |
| 章节管理 AuthorChapterList.vue | 章节列表、拖拽排序、批量操作 |
| 章节编辑 AuthorChapterEdit.vue | 富文本编辑、TXT文件导入 |
| 作者资料 | 笔名设置、作者简介、收益概览 |

### 管理后台功能（9页）

| 页面 | 功能说明 |
|------|----------|
| 数据仪表盘 Dashboard.vue | 用户数/小说数/评论数/今日新增等多维统计图表 |
| 书籍管理 Books.vue | 高级筛选、批量审核/删除/导出Excel、分页展示、编辑书籍信息 |
| 章节管理 Chapters.vue | TXT批量上传、章节内容审核 |
| 广告管理 Advertisements.vue | 广告位配置、上下架管理 |
| 公告管理 Announcements.vue | 系统公告发布与编辑 |
| 分类管理 Categories.vue | 小说分类的增删改查 |
| 违规记录 Violations.vue | 用户举报处理、违规内容查看 |
| 审核列表 ReviewList.vue | 新书审核队列 |
| 管理布局 AdminLayout.vue | 后台导航、用户下拉菜单、侧边栏路由 |

### 数据采集

- **Scrapy爬虫**：自动采集小说元数据和章节内容
- **封面爬取**：crawl_covers_xbiquge.py 从xbiquge.la真实爬取封面（317个文件，100%覆盖率）
- 支持多站点采集、增量更新、去重处理

---

## 技术栈

- **前端**: Vue 3 + TypeScript 5 + Element Plus 2.5+ + Vite 5 + Vue Router 4 + Pinia 2 + Axios + Less
- **后端**: Django 4.2.14 + Django REST Framework + PyMySQL + django-cors-headers
- **数据库**: MySQL (utf8mb4)
- **缓存**: Redis (会话/热点数据)
- **认证**: Session认证 + OAuth2 (QQ/微信)
- **异步任务**: Celery + Redis (可选)
- **爬虫**: Scrapy框架
- **文件存储**: 本地文件系统 (Pillow图片处理)
- **Python**: 3.8

---

## 数据规模（v2.0.0）

| 数据项 | 数量 | 说明 |
|--------|------|------|
| 小说总数 | 81本 | 原37本 + 新增64本 |
| 封面文件 | 317个 | 100%覆盖率，从xbiquge.la真实爬取 |
| 数据库迁移 | 13次 | 0001_initial ~ 0013_add_signin_recharge |
| 数据模型 | 18个 | User/Novel/Chapter/Favorite/ReadingProgress/Bookmark/Comment/AdminUser/EmailVerificationCode/Advertisement/Announcement/OperationLog/BookCategory/ViolationRecord/ChapterUploadLog/SigninReward/SigninRecord/RechargePlan/RechargeOrder |
| 前端页面 | 27个 | 读者端14页 + 作者端4页 + 后台9页 |
| API端点 | 30+ | 认证/公开/用户/作者/后台全覆盖 |

---

## 系统截图

<div align="center">
  <p align="center"><b>首页界面（v2.0.0 - 12大板块）</b></p>
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
  <br/><br/>
  <p align="center"><b>每日签到（v2.0.0新功能）</b></p>
  <img src="screenshots/signin.png" width="100%" alt="每日签到" />
  <br/><br/>
  <p align="center"><b>VIP充值（v2.0.0新功能）</b></p>
  <img src="screenshots/recharge.png" width="100%" alt="VIP充值" />
</div>

---

## 快速开始

### 环境要求

- Node.js ≥ 18
- Python ≥ 3.8 （本项目使用 Python 3.8）
- MySQL ≥ 5.7
- Redis ≥ 6.0 (推荐)

### 安装与运行

```bash
# 1. 克隆仓库
git clone [仓库地址]
cd inkfiction
git checkout v2.0.0

# 2. 后端环境配置
cd novel_backend
python -m venv venv
venv\Scripts\activate  # Windows激活虚拟环境
pip install django==4.2.14 djangorestframework django-cors-headers Pillow chardet celery redis python-dotenv pymysql

# 3. 配置数据库
# 创建MySQL数据库: CREATE DATABASE inkfiction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# 修改 novel_backend/novel_project/settings.py 中的 DATABASES 配置

# 4. 运行数据库迁移（13次迁移）
python manage.py migrate
# 或初始化测试数据
python manage.py seed_all_data  # 导入81本小说数据

# 5. 启动后端服务 (端口8000)
python manage.py runserver

# 6. 新开终端，启动前端开发服务 (端口5173)
cd novel_frontend
npm install
npm run dev
```

打开 `http://localhost:5173`，即可访问墨香书阁在线小说阅读平台 v2.0.0。

> 📝 **快速开始必须可执行**：确保MySQL已创建数据库并正确配置settings.py中的连接信息，前后端分别启动后通过CORS互通。Python版本需≥3.8。

---

## 核心特性

### 阅读体验
- **沉浸式阅读**：支持翻页模式、多种阅读主题切换（默认/护眼/夜间/羊皮纸）、字号自由调节
- **智能书签**：一键添加书签，阅读进度自动保存与恢复，跨设备同步
- **章节导航**：目录树快速跳转、上下章无缝切换、阅读位置记忆

### 内容发现
- **多维排行**：人气榜、新书榜、完结榜、畅销榜实时更新
- **智能搜索**：关键词全文检索、搜索结果高亮展示
- **个性化推荐**：首页12大板块（轮播/榜单/专题/改编推荐/总编推荐/分类快捷栏/签约新书/最近更新/完结榜）

### 社交互动
- **评论系统**：小说级评论、点赞互动、违规举报
- **收藏管理**：一键收藏、收藏列表快速访问
- **阅读历史**：自动记录阅读轨迹、续读入口

### 用户运营（v2.0.0新增）
- **每日签到**：连续签到奖励递增、断签重计、签到历史查询
- **VIP充值**：月卡/季卡/年卡套餐、在线下单支付、VIP权益标识、订单管理
- **积分体系**：签到获取金币、金币可用于兑换VIP或虚拟商品

### 创作工具
- **作者工作台**：作品管理、数据看板、收益概览
- **富文本编辑**：章节内容可视化编辑、TXT批量导入
- **封面上传**：支持JPG/PNG格式、自动压缩优化
- **作品标记**：影视改编标记(is_adapted)、总编推荐标记(is_recommended)、专题标签(topic_tag)

### 运营管理
- **后台仪表盘**：多维度数据统计、趋势图表可视化
- **内容审核**：书籍/章节批量操作、违规记录追踪、审核列表(ReviewList)
- **运营工具**：广告管理、公告发布、分类维护、操作日志审计
- **数据导出**：书籍数据Excel导出功能

### 技术架构
- **前后端分离**：Vue3 SPA + DRF RESTful API，独立部署扩展性强
- **Session + OAuth认证**：支持账号密码登录和QQ/微信第三方登录
- **响应式设计**：适配桌面端与移动端浏览器
- **自动化采集**：Scrapy爬虫定时抓取，封面真实爬取（xbiquge.la），数据持续更新
- **18个数据模型**：完整覆盖用户/内容/运营/支付全业务域

> 📝 **写法提示**：每个特性用 **加粗关键词** 开头，后跟一句话说明用户能得到什么价值。

---

## 项目结构

```
inkfiction/
├── novel_frontend/                  # Vue3前端项目
│   ├── src/
│   │   ├── api/                    # API接口封装 (index.ts)
│   │   ├── assets/                 # 静态资源 (hero.png/vite.svg/vue.svg)
│   │   ├── components/             # 公共组件 (HelloWorld.vue)
│   │   ├── directives/             # 自定义指令 (lazy.ts 图片懒加载)
│   │   ├── router/                 # Vue Router路由配置 (index.ts)
│   │   ├── stores/                 # Pinia状态管理 (user.ts)
│   │   ├── utils/                  # 工具函数 (request.ts/image.ts)
│   │   └── views/                  # 页面组件 (27个页面)
│   │       ├── Home.vue            # 首页(12大板块)
│   │       ├── Login.vue           # 登录注册(OAuth/邮箱验证码)
│   │       ├── Register.vue        # 用户注册
│   │       ├── NovelList.vue       # 小说列表(筛选/排序/分页)
│   │       ├── NovelDetail.vue     # 小说详情(封面/简介/目录/评论)
│   │       ├── Reader.vue          # 章节阅读器(翻页/主题/字号/书签)
│   │       ├── Rankings.vue        # 排行榜(人气/新书/完结/畅销)
│   │       ├── Search.vue          # 搜索结果
│   │       ├── UserCenter.vue      # 个人中心(信息/头像/收藏/历史/书签/设置)
│   │       ├── SignIn.vue          # 每日签到(v2.0.0新增)
│   │       ├── Recharge.vue        # VIP充值(v2.0.0新增)
│   │       ├── AuthorCenter.vue    # 作者工作台
│   │       ├── AuthorNovelEdit.vue # 作品管理(含改编/推荐标记)
│   │       ├── AuthorChapterList.vue # 章节管理
│   │       ├── AuthorChapterEdit.vue # 章节编辑(TXT导入)
│   │       ├── NotFound.vue        # 404页面
│   │       └── admin/              # 管理后台页面(9个)
│   │           ├── AdminLayout.vue    # 后台布局(导航/用户下拉)
│   │           ├── Dashboard.vue      # 数据仪表盘
│   │           ├── Books.vue          # 书籍管理(CRUD/导出Excel/筛选)
│   │           ├── Categories.vue     # 分类管理
│   │           ├── Advertisements.vue # 广告管理
│   │           ├── Announcements.vue  # 公告管理
│   │           ├── Violations.vue     # 违规记录
│   │           └── ReviewList.vue     # 审核列表
│   ├── App.vue
│   ├── main.ts
│   ├── style.css
│   ├── package.json
│   └── vite.config.ts
├── novel_backend/                   # Django后端项目
│   ├── novel_project/              # Django项目配置
│   │   ├── settings.py            # 项目配置
│   │   ├── urls.py                # 根路由配置
│   │   ├── wsgi.py                # WSGI部署
│   │   └── asgi.py                # ASGI部署
│   ├── novels/                     # 主应用模块
│   │   ├── models.py              # 数据模型(18个:User/Novel/Chapter/SigninReward/RechargePlan等)
│   │   ├── views.py               # 公开API(小说列表/详情/章节/评论/搜索/排行/首页12板块)
│   │   ├── user_views.py          # 用户API(注册/登录/个人信息/收藏/书签/签到/充值/OAuth)
│   │   ├── author_views.py        # 作者API(小说CRUD/章节管理/封面上传/TXT上传)
│   │   ├── admin_views.py         # 后台管理API(全部CRUD/批量操作/统计/日志/审核)
│   │   ├── comment_views.py       # 评论API
│   │   ├── auth.py                # 认证逻辑
│   │   ├── urls.py                # 路由配置(30+端点)
│   │   ├── serializers.py         # 序列化器
│   │   ├── user_serializers.py    # 用户序列化器(含签到/充值)
│   │   ├── author_serializers.py  # 作者序列化器
│   │   ├── comment_serializers.py # 评论序列化器
│   │   ├── admin_serializers.py   # 管理后台序列化器
│   │   ├── oauth_utils.py         # OAuth工具(QQ/微信)
│   │   ├── email_utils.py         # 邮件发送工具
│   │   ├── admin.py               # Django Admin配置
│   │   ├── apps.py                # 应用配置
│   │   └── migrations/            # 数据库迁移文件(13次:0001~0013)
│   │       ├── 0001_initial.py
│   │       ├── 0002_*.py
│   │       ├── ...
│   │       ├── 0012_novel_is_adapted_novel_is_recommended_and_more.py
│   │       └── 0013_add_signin_recharge.py
│   ├── manage.py                   # Django管理脚本
│   ├── requirements.txt            # Python依赖
│   ├── crawl_covers_xbiquge.py     # 封面爬虫(xbiquge.la, v2.0.0新增)
│   ├── seed_signin_recharge.py     # 签到/充值初始数据
│   └── manage_commands/            # 自定义管理命令
│       ├── seed_data.py            # 数据种子
│       ├── check_chapters.py       # 检查章节
│       ├── fix_comment_dates.py    # 修复评论日期
│       └── ...
├── CopyBook/
│   └── copyBook-master/
│       └── bookspider/             # Scrapy爬虫项目
│           ├── spiders/            # 爬虫脚本
│           ├── items.py            # 数据模型
│           ├── pipelines.py        # 数据处理管道
│           └── settings.py         # 爬虫配置
├── docs/                           # 项目文档(14份)
│   ├── 1-项目建议书.md             # 项目概述、背景、目标与范围
│   ├── 2-可行性分析报告.md         # 技术、经济、运营可行性分析
│   ├── 3-需求规格说明书.md         # 功能需求、非功能需求、用例分析
│   ├── 4-项目计划书.md             # WBS分解、甘特图、资源配置
│   ├── 5-Agent文档.md              # AI辅助开发规范
│   ├── 6-项目开发日志.md           # 迭代记录、里程碑、问题跟踪
│   ├── 7-版本更新日志.md           # 版本变更记录
│   ├── 8-项目质量计划书.md         # 质量目标和标准定义
│   ├── 9-项目质量检查报告.md       # 质量检查结果
│   ├── 10-代码评审报告.md          # 代码质量评审
│   ├── 11-安全审查报告.md          # 安全审查
│   ├── 12-README.md               # 项目说明文档(本文件)
│   ├── 13-测试用例与测试报告.md     # 测试验证
│   └── 14-项目验收报告.md          # 最终验收确认
└── screenshots/                    # 系统截图(v2.0.0)
```

---

## 核心API端点（30+）

### 认证模块
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录(Session认证)
- `POST /api/auth/logout/` - 退出登录
- `GET /api/auth/me/` - 获取当前用户信息
- `PUT /api/auth/update_profile/` - 更新个人资料
- `POST /api/auth/send_verification_code/` - 发送邮箱验证码

### 小说公开API
- `GET /api/novels/` - 获取小说列表(支持筛选/排序/分页)
- `GET /api/novels/{id}/` - 获取小说详情
- `GET /api/novels/{id}/chapters/` - 获取章节列表
- `GET /api/novels/home_data/` - 首页12大板块数据
- `GET /api/comments/` - 获取评论列表
- `POST /api/comments/` - 发表评论
- `GET /api/rankings/` - 获取排行榜数据
- `GET /api/search/` - 关键词搜索

### 用户API
- `GET /api/favorites/` - 获取收藏列表
- `POST /api/favorites/` - 添加收藏
- `DELETE /api/favorites/{id}/` - 取消收藏
- `GET /api/reading-progress/` - 获取阅读进度
- `PUT /api/reading-progress/` - 更新阅读进度
- `GET /api/bookmarks/` - 获取书签列表
- `POST /api/bookmarks/` - 添加书签
- `DELETE /api/bookmarks/{id}/` - 删除书签
- `POST /api/signin/today/` - 每日签到
- `GET /api/signin/history/` - 签到历史记录
- `GET /api/signin/rewards/` - 签到奖励配置
- `GET /api/recharge/plans/` - 获取充值套餐列表
- `POST /api/recharge/orders/` - 创建充值订单
- `GET /api/recharge/orders/` - 获取我的订单列表

### 作者API
- `GET /api/author/novels/` - 获取作者作品列表
- `POST /api/author/novels/` - 创建新小说
- `PUT /api/author/novels/{id}/` - 更新小说信息
- `DELETE /api/author/novels/{id}/` - 删除小说
- `POST /api/author/novels/upload_cover/` - 上传小说封面
- `GET /api/author/chapters/?novel_id={id}` - 获取章节列表
- `POST /api/author/chapters/` - 创建章节
- `PUT /api/author/chapters/{id}/` - 更新章节内容
- `DELETE /api/author/chapters/{id}/` - 删除章节
- `POST /api/author/chapters/upload_txt/` - TXT批量导入章节

### 管理后台API
- `GET /api/admin/dashboard-stats/` - 仪表盘统计数据
- `GET /api/admin/books/` - 书籍列表(高级筛选)
- `PUT /api/admin/books/{id}/` - 编辑书籍
- `DELETE /api/admin/books/{id}/` - 删除书籍
- `GET /api/admin/books/export/` - Excel导出书籍数据
- `PUT /api/admin/books/{id}/audit/` - 审核书籍
- `DELETE /api/admin/books/batch_delete/` - 批量删除书籍
- `GET /api/admin/categories/` - 分类列表
- `POST /api/admin/categories/` - 创建分类
- `PUT /api/admin/categories/{id}/` - 编辑分类
- `DELETE /api/admin/categories/{id}/` - 删除分类
- `GET /api/admin/advertisements/` - 广告列表
- `POST /api/admin/advertisements/` - 创建广告
- `PUT /api/admin/advertisements/{id}/` - 编辑广告
- `GET /api/admin/announcements/` - 公告列表
- `POST /api/admin/announcements/` - 创建公告
- `PUT /api/admin/announcements/{id}/` - 编辑公告
- `GET /api/admin/violations/` - 违规记录
- `PUT /api/admin/violations/{id}/handle/` - 处理违规
- `GET /api/public/announcements/` - 公开公告列表
- `GET /api/public/advertisements/` - 公开广告列表

---

## 版本

**v2.0.0** (正式版, 2026-06-06) — Git tag v2.0.0 (c84abc5), branch main

主要更新：
- ✅ 新增每日签到系统（SigninReward/SigninRecord模型 + SignIn.vue页面）
- ✅ 新增VIP充值系统（RechargePlan/RechargeOrder模型 + Recharge.vue页面）
- ✅ 首页升级为12大板块（轮播/榜单/专题/改编推荐/总编推荐/分类快捷栏/签约新书/最近更新/完结榜）
- ✅ Novel模型新增4个字段（is_adapted/is_recommended/recommend_comment/topic_tag）
- ✅ 小说数据扩展至81本（原37本 + 新增64本）
- ✅ 封面100%覆盖率（317个文件，从xbiquge.la真实爬取）
- ✅ 数据库迁移至13次（0001~0013）
- ✅ 新增OAuth第三方登录（QQ/微信）
- ✅ 新增邮箱验证码功能
- ✅ 后台新增Excel导出功能
- ✅ 后台新增审核列表(ReviewList.vue)

详见 [7-版本更新日志.md](./docs/7-版本更新日志.md)

---

## 项目文档索引

| 序号 | 文档名称 | 文件路径 | 说明 |
|------|----------|----------|------|
| 01 | 项目建议书 | [docs/1-项目建议书.md](./docs/1-项目建议书.md) | 项目背景、目标、范围界定 |
| 02 | 可行性研究报告 | [docs/2-可行性分析报告.md](./docs/2-可行性分析报告.md) | 技术/经济/运营可行性论证 |
| 03 | 需求规格说明书 | [docs/3-需求规格说明书.md](./docs/3-需求规格说明书.md) | 功能/非功能需求、用例建模 |
| 04 | 项目计划书 | [docs/4-项目计划书.md](./docs/4-项目计划书.md) | WBS分解、进度安排、资源规划 |
| 05 | Agent文档 | [docs/5-Agent文档.md](./docs/5-Agent文档.md) | AI辅助开发规范 |
| 06 | 项目开发日志 | [docs/6-项目开发日志.md](./docs/6-项目开发日志.md) | 迭代记录、里程碑、问题跟踪 |
| 07 | 版本更新日志 | [docs/7-版本更新日志.md](./docs/7-版本更新日志.md) | 版本变更记录 |
| 08 | 项目质量计划书 | [docs/8-项目质量计划书.md](./docs/8-项目质量计划书.md) | 质量目标和标准定义 |
| 09 | 项目质量检查报告 | [docs/9-项目质量检查报告.md](./docs/9-项目质量检查报告.md) | 质量检查结果 |
| 10 | 代码评审报告 | [docs/10-代码评审报告.md](./docs/10-代码评审报告.md) | 代码质量评审 |
| 11 | 安全审查报告 | [docs/11-安全审查报告.md](./docs/11-安全审查报告.md) | 安全审查 |
| 12 | README文档 | [docs/12-README.md](./docs/12-README.md) | 项目说明、快速开始指南（本文件） |
| 13 | 测试用例与测试报告 | [docs/13-测试用例与测试报告.md](./docs/13-测试用例与测试报告.md) | 测试策略、用例设计、验收标准 |
| 14 | 项目验收报告 | [docs/14-项目验收报告.md](./docs/14-项目验收报告.md) | 最终验收确认 |

---

© 2026 墨香书阁（InkFiction）团队. All rights reserved.
