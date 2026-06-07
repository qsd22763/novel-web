# 墨香书阁

企业级高品质小说阅读网站，提供小说浏览、搜索、收藏、在线阅读、关注作者、评分、每日签到、会员等完整功能。基于 Vue 3 + Django 前后端分离架构，配备深蓝首页与金色书库的企业级UI设计，支持响应式三端适配。

> **作者**：qsd22763 &nbsp;\|&nbsp; **版本**：v3.0.0 &nbsp;\|&nbsp; **许可证**：MIT

---

## 功能模块

### 读者端功能（10页）

| 页面 | 功能说明 |
|------|----------|
| 首页 Home.vue | 深蓝主题首页，轮播推荐、人气榜单、新书榜单、分类导航、书单推荐 |
| 书库 NovelList.vue | 金色主题书库，分类筛选（12分类）、排序（最新/最热/完结）、横向拖拽卡片、分页浏览 |
| 小说详情 NovelDetail.vue | 金色主题详情页，封面展示、简介信息、章节目录树、星级评分弹窗、评论区、关注作者按钮 |
| 排行榜 Rankings.vue | Tab榜单切换（人气榜/新书榜/完结榜/畅销榜） |
| 搜索结果 Search.vue | 关键词全文搜索、结果高亮展示 |
| 作者主页 AuthorHome.vue | 作者信息展示、作品列表、关注按钮 |
| 我的关注 Follow.vue | 关注的作者列表、取消关注 |
| 每日签到 SignIn.vue | 每日签到领取奖励、连续签到额外奖励、签到历史记录 |
| 会员中心 Member.vue | 会员套餐展示、会员权益标识 |
| 个人中心 UserCenter.vue | 信息编辑、头像上传、我的收藏、阅读历史、设置 |

### 管理后台功能（6页）

| 页面 | 功能说明 |
|------|----------|
| 数据仪表盘 Dashboard.vue | 用户数/小说数/评论数/今日新增等多维统计图表 |
| 书籍管理 Books.vue | 高级筛选、批量审核/删除/导出Excel、分页展示、编辑书籍信息 |
| 章节管理 Chapters.vue | 章节内容审核与管理 |
| 用户管理 Users.vue | 用户信息查看与管理 |
| 分类管理 Categories.vue | 小说分类的增删改查 |
| 管理布局 AdminLayout.vue | 后台导航、用户下拉菜单、侧边栏路由 |

---

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Vue Router 4 + Pinia + Axios
- **后端**: Python 3.8 + Django 4.2 + Django REST Framework (DRF) + PyMySQL
- **数据库**: MySQL (utf8mb4)
- **认证**: Session认证
- **文件存储**: 本地文件系统 (Pillow图片处理)

---

## 系统截图

<div align="center">
  <p align="center"><b>首页界面（深蓝主题 - v3.0.0）</b></p>
  <!-- <img src="screenshots/home.png" width="100%" alt="首页界面" /> -->
  <p><i>（截图待补充）</i></p>
</div>

---

## 快速开始

### 环境要求

- Node.js ≥ 18
- Python ≥ 3.8
- MySQL ≥ 5.7

### 安装与运行

```bash
# 后端
cd novel_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# 前端
cd novel_frontend
npm install
npm run dev
```

打开 `http://localhost:5173`，即可访问墨香书阁 v3.0.0。

---

## 核心特性

### 阅读体验
- **沉浸式阅读**：章节阅读器支持翻页模式、上下章切换、阅读进度自动保存
- **智能书签**：一键添加书签，阅读进度自动保存与恢复
- **章节导航**：目录树快速跳转、上下章无缝切换

### 内容发现
- **多维排行**：Tab榜单切换（人气榜/新书榜/完结榜/畅销榜），数据动态刷新
- **智能搜索**：关键词全文检索、搜索结果高亮展示
- **书单推荐**：首页书单推荐模块，个性化内容发现

### 社交互动
- **关注作者系统**：6个API实现完整的关注/取关流程，作者主页展示粉丝数
- **评分系统**：3个API实现星级评分功能，星级评分弹窗交互
- **评论系统**：小说级评论、互动交流

### 用户运营
- **每日签到**：连续签到奖励递增、断签重计、签到历史查询
- **会员中心**：会员套餐、会员权益标识

### 企业级UI设计
- **深蓝首页**：专业沉稳的深蓝色调首页设计
- **金色书库/详情**：高端大气的金色主题书库和详情页
- **横向拖拽卡片**：书库页面支持横向拖拽浏览，交互流畅
- **Tab榜单**：排行榜页面Tab切换，操作便捷
- **响应式三端适配**：完美适配桌面端、平板端、移动端

### 运营管理
- **后台仪表盘**：多维度数据统计、趋势图表可视化
- **内容管理**：书籍/章节/用户/分类全流程管理
- **数据导出**：书籍数据Excel导出功能

### 技术架构
- **前后端分离**：Vue3 SPA + DRF RESTful API，独立部署扩展性强
- **TypeScript零错误**：前端TypeScript严格类型检查，编译零错误
- **9项Bug修复**：经过全面测试与修复，系统稳定性高
- **81本小说数据**：2381章节 / 12分类 / 完整数据模型

---

## 项目结构

```
墨香书阁/
├── novel_backend/                  # Django 后端
│   └── novels/
│       ├── models.py               # 数据模型
│       ├── views.py                # 公开API视图
│       ├── user_views.py           # 用户API视图
│       ├── follow_views.py         # 关注作者API(6个)
│       ├── rating_views.py         # 评分API(3个)
│       ├── checkin_views.py        # 签到API
│       ├── admin_views.py          # 管理后台API
│       ├── serializers.py          # 序列化器
│       ├── user_serializers.py     # 用户序列化器
│       ├── urls.py                 # 路由配置
│       └── migrations/             # 数据库迁移(0014~0016)
├── novel_frontend/                 # Vue 3 前端
│   └── src/
│       ├── api/index.ts            # API封装
│       ├── router/index.ts         # 路由配置
│       ├── utils/                  # 工具函数
│       └── views/                  # Vue组件(20个)
│           ├── Home.vue            # 首页(深蓝主题)
│           ├── NovelList.vue       # 书库(金色主题+横向拖拽)
│           ├── NovelDetail.vue     # 详情(金色主题+星级评分)
│           ├── Rankings.vue        # 排行(Tab榜单)
│           ├── Search.vue          # 搜索
│           ├── AuthorHome.vue      # 作者主页
│           ├── Follow.vue          # 我的关注
│           ├── SignIn.vue          # 签到
│           ├── Member.vue          # 会员
│           ├── UserCenter.vue      # 个人中心
│           └── admin/              # 管理后台(6页)
│               ├── AdminLayout.vue
│               ├── Dashboard.vue
│               ├── Books.vue
│               ├── Chapters.vue
│               ├── Users.vue
│               └── Categories.vue
├── docs/                           # 项目文档(14份)
└── 实验报告文档/                    # 模板+示范案例
```

---

## 版本

**v3.0.0** (正式版, 2026-06-07)

主要更新：
- ✅ 新增关注作者系统（6个API + AuthorHome.vue + Follow.vue）
- ✅ 新增评分系统（3个API + 星级评分弹窗）
- ✅ 新增签到会员功能（SignIn.vue + Member.vue）
- ✅ 企业级UI升级（深蓝首页 + 金色书库/详情）
- ✅ 响应式三端适配（桌面/平板/移动）
- ✅ 横向拖拽卡片 / Tab榜单 / 书单推荐
- ✅ 数据扩展至81本小说 / 2381章节 / 12分类
- ✅ 数据库新表3张（0014~0016迁移）
- ✅ TypeScript零错误编译
- ✅ 9项Bug修复

详见 [CHANGELOG.md](7-版本更新日志.md)

---

© 2026 墨香书阁. All rights reserved.
