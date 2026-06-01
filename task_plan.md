# 墨香书阁 (InkFiction) — 开发计划

> 项目路径: `d:\python damo\vue`
> 最后更新: 2026-05-31
> 当前版本: **v1.2.0-dev** (MySQL 迁移 + AI 封面)

---

## 项目概述

**墨香书阁** — E-Ink 文学气质的在线小说阅读平台

| 层 | 技术栈 |
|---|--------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + Pinia |
| 后端 | Django 4.2.14 + DRF |
| 数据库 | **MySQL 8.0** (utf8mb4) ← v1.2 从 SQLite 迁移 |
| 认证 | Session/Cookie (CSRF 豁免) |
| 字体 | Noto Serif SC (fonts.loli.net 镜像) |

---

## 开发阶段总览

```
Phase 1   [██████████] 100%  项目初始化 + 核心功能
Phase 2   [██████████] 100%  Bug 修复 + 新功能 (v1.0 → v1.1)
Phase 3   [████████░░] 80%   SQLite → MySQL 迁移 + AI 封面
Phase 3.5 [██████████] 100%  爬虫开发与内容采集 ✅
Phase 4   [░░░░░░░░░░] 0%    未来规划
```

---

## Phase 1: 项目初始化 + 核心功能 ✅ 完成

**状态:** `complete` | **版本:** v1.0.0

### 1.1 项目搭建
- [x] Vue 3 + Vite + TypeScript 脚手架
- [x] Django 4.2 + DRF 后端框架
- [x] Element Plus UI 组件库集成
- [x] Vue Router 4 路由配置
- [x] Pinia 状态管理
- [x] Axios 封装 (request.ts 拦截器)

### 1.2 数据模型设计 (7 张表)
- [x] User (扩展 AbstractUser, 含 VIP/作者/笔名)
- [x] Novel (小说: 标题/作者/封面/分类/标签/审核状态)
- [x] Chapter (章节: 内容/排序/发布状态)
- [x] Favorite (收藏)
- [x] ReadingProgress (阅读进度)
- [x] Bookmark (书签, 含 position 字段)
- [x] Comment (评论, 含评分)

### 1.3 读者功能
- [x] 首页展示 (精选推荐 + 分类浏览)
- [x] 小说详情页 (封面/简介/章节目录/评分)
- [x] 在线阅读器 (沉浸式阅读)
- [x] 搜索功能 (标题/作者/分类)
- [x] 排行榜 (多维排行)

### 1.4 社交互动
- [x] 收藏系统 (一键收藏/取消)
- [x] 评论评分 (1-5星 + 文字评论)
- [x] 阅读记录 (自动追踪进度)
- [x] 书签功能 (章节内书签管理)

### 1.5 作者创作系统
- [x] 作者中心 (数据看板)
- [x] 作品 CRUD (创建/编辑/删除)
- [x] 章节 CRUD (草稿/发布切换)
- [x] 封面上传 (本地上传)
- [x] 审核流程 (草稿→审核中→已发布/驳回)
- [x] 自动保存 (8秒静默保存)

### 1.6 用户系统
- [x] 注册 / 登录
- [x] Session 持久化认证
- [x] CSRF 豁免链路

---

## Phase 2: Bug 修复 + 功能增强 ✅ 完成

**状态:** `complete` | **版本:** v1.1.0

### 2.1 Bug 修复 (11项)
- [x] P01: 阅读/书签 500 AssertionError (Serializer 冲突)
- [x] P02-P03: 作者页面双重 .data 解包 (5处)
- [x] P04: 书签 400 字段名不匹配 (novel_id→novel)
- [x] P05: Google Fonts 超时 (换国内镜像)
- [x] P06: Session Cookie 跨域丢失
- [x] P07: 评论按钮不可见
- [x] P08: 小说简介不显示
- [x] P09: IDE React Error (非代码问题)

### 2.2 新功能 (5项)
- [x] 404 专用页面 (NotFound.vue)
- [x] 评论删除功能 (仅本人可见)
- [x] 修改密码功能
- [x] 小说标签展示 (首页+详情页)
- [x] 作者页面响应式适配 (4个页面)

---

## Phase 3: MySQL 迁移 + 基础设施升级 🔄 进行中

**状态:** `in_progress` | **目标版本:** v1.2.0

### 3.1 SQLite → MySQL 迁移 ✅
- [x] 修改 settings.py DATABASES 配置 (MySQL + pymysql)
- [x] __init__.py 注册 pymysql 驱动
- [x] ORM 模型兼容性检查 (无 SQLite 特有语法)
- [x] 生成 MySQL DDL 建表脚本 (7张业务表 + 索引 + FK)
- [x] 执行建表 (16张表含Django内置)
- [x] SQLite 数据迁移 (225条记录)
- [x] 创建 .env 配置文件
- [x] settings.py 环境变量化 (python-dotenv)
- [x] 数据库连通性测试通过

### 3.2 AI 封面生成 ✅
- [x] 发现 text_to_image API 外部不可用
- [x] 切换至 Pollinations.ai 免费服务
- [x] 为 24 本小说定制 Prompt
- [x] 批量生成精美 AI 插画封面 (24/24 成功)
- [x] 数据库 cover 字段更新为本地路径

### 3.3 服务运行验证 ✅
- [x] 后端 Django 启动正常 (port 8000)
- [x] 前端 Vite 启动正常 (port 5174)
- [x] 全部 API 端点验证通过
- [x] 前端页面渲染正常

### 3.4 待完成
- [ ] Git 提交 v1.2.0
- [ ] 更新 CHANGELOG.md (v1.2.0 条目)
- [ ] 清理临时脚本 (exec_sql.py/migrate_data.py/regen_*.py/gen_*.py/test_mysql.py 等)

---

## Phase 3.5: 爬虫开发与内容采集 ✅ 完成

**状态:** `complete` | **版本:** v1.2.1-crawler

### 3.5.1 技术调研与源码分析
- [x] CopyBook 项目克隆 (hahaha108/CopyBook via ZIP)
- [x] 源码分析 (5个Spider脚本, Django+Scrapy耦合架构)
- [x] 技术选型决策: 放弃 Scrapy 框架, 采用独立脚本方案

### 3.5.2 目标站点适配
- [x] 目标站切换 (quanshuwang.com → xbiquge.la)
- [x] 站点结构分析 (分类页/列表页/详情页/章节页)

### 3.5.3 ink_crawler.py 开发
- [x] 独立脚本架构设计 (零框架依赖, 纯 requests + lxml)
- [x] 分类页爬取模块 (3大分类: 玄幻/都市/科幻)
- [x] 小说列表解析 (标题/作者/简介/封面URL)
- [x] 章节目录抓取 (多页章节支持)
- [x] 正文内容提取 (XPath 精准定位)
- [x] 数据库直连写入 (Django ORM 批量插入)

### 3.5.4 Bug 修复与优化
- [x] Bug修复: 分类页 URL 格式问题 (/fenlei/ 路径拼接)
- [x] XPath 过滤优化 (去除广告/无关节点)
- [x] 反爬策略处理 (请求头伪装 + 延迟控制)
- [x] 异常处理机制 (网络超时/解析失败重试)

### 3.5.5 测试与验证
- [x] 单书测试通过 (《雪鹰领主》50章完整采集)
- [x] 数据完整性校验 (章节顺序/内容截断检查)
- [x] 封面图片下载与本地存储

### 3.5.6 批量采集执行
- [x] 批量爬取完成 (3分类 × 3本 = **10本新小说入库**)
- [x] 采集统计:
  - 新增小说: ~10 本
  - 新增章节: ~1000+ 章
  - 最终数据库规模: **~34本小说, ~1000+章**
- [x] 采集日志记录 (成功/失败/跳过统计)

---

## Phase 4: 未来规划 📋

**状态:** `pending` | **新增能力:** 内容爬虫 (ink_crawler.py)

### 4.1 性能优化
- [ ] Redis 缓存层 (热门小说/排行榜)
- [ ] 数据库索引优化
- [ ] 图片 CDN 加速
- [ ] 前端路由懒加载

### 4.2 功能增强
- [ ] 推荐算法 (基于阅读历史协同过滤)
- [ ] 小说章节批量导入 (TXT/EPUB 解析)
- [ ] 暗色模式切换
- [ ] 阅读设置 (字号/背景色/行距)
- [ ] 消息通知系统

### 4.3 运维部署
- [ ] Docker 容器化 (docker-compose.yml)
- [ ] Nginx 反向代理 + HTTPS
- [ ] Gunicorn/uWSGI 生产服务器
- [ ] CI/CD 自动化部署

### 4.4 安全加固
- [ ] JWT Token 认证选项
- [ ] 接口频率限制 (throttling)
- [ ] XSS/SQL注入防护审计
- [ ] 敏感数据加密存储

---

## 错误日志

| # | 错误 | 阶段 | 解决方案 |
|---|------|------|---------|
| E01 | INT UNSIGNED FK 不兼容 Django 内置表 | Phase 3 | 改用 signed INT |
| E02 | PowerShell 中文编码乱码 | Phase 3 | `[Console]::OutputEncoding = UTF8` |
| E03 | text_to_image API 返回占位图 | Phase 3 | 换 Pollinations.ai |
| E04 | BASE_DIR 定义顺序错误 | Phase 3 | 移到 load_dotenv 之前 |
| E05 | Pillow tuple 解包语法错误 | Phase 3 | 修正元组写法 |

---

## 项目文件清单 (核心)

### 后端关键文件
| 文件 | 用途 |
|------|------|
| `novel_project/settings.py` | Django 配置 (MySQL/.env) |
| `novel_project/__init__.py` | pymysql 驱动注册 |
| `novels/models.py` | 7 个 ORM 模型 |
| `novels/views.py` | Novel/Chapter ViewSet |
| `novels/user_views.py` | Auth/Favorite/Progress/Bookmark |
| `novels/author_views.py` | Author CRUD |
| `novels/comment_views.py` | Comment ViewSet |
| `novels/serializers.py` | 公共序列化器 |
| `.env` | 数据库连接配置 |

### 前端关键文件
| 文件 | 用途 |
|------|------|
| `src/utils/request.ts` | Axios 实例 + 拦截器 |
| `src/api/index.ts` | 全部 API 封装 |
| `src/views/Home.vue` | 首页 |
| `src/views/NovelDetail.vue` | 详情页 |
| `src/views/Reader.vue` | 阅读器 |
| `src/views/UserCenter.vue` | 用户中心 |
| `src/views/AuthorCenter.vue` | 作者中心 |
| `src/router/index.ts` | 路由配置 |
| `vite.config.ts` | Vite 代理配置 |

### 临时/工具脚本 (可清理)
| 文件 | 用途 |
|------|------|
| `exec_sql.py` | MySQL 建表执行器 |
| `migrate_data.py` | SQLite→MySQL 数据迁移 |
| `test_mysql.py` | 数据库连通性测试 |
| `regen_covers_v2.py` | 封面重新生成(v2) |
| `restore_api_covers.py` | 恢复API封面URL |
| `gen_covers_pillow.py` | Pillow文字封面 |
| `gen_artistic_covers.py` | 艺术风格封面 |
| `gen_ai_covers.py` | **AI封面生成(最终版)** |
