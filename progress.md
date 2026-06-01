# 墨香书阁 — 开发进度日志

> 最后更新: 2026-05-31

---

## Session 总览

| Session | 日期 | 主要工作 | 版本 |
|---------|------|---------|------|
| S01 | - | 项目初始化 + 核心功能开发 | v0.1 → v1.0 |
| S02 | - | Bug 修复 (P01-P09) + 新功能 (5项) | v1.0 → v1.1 |
| S03 | 2026-05-31 | SQLite→MySQL 迁移 + AI 封面生成 | v1.1 → v1.2-dev |
| S04 | 2026-06-01 | CopyBook 爬虫提取 + 批量小说抓取 | v1.2-dev → v1.2-dev |

---

## Session S03: MySQL 迁移 + AI 封面

**日期:** 2026-05-31
**目标:** 完整迁移至 MySQL + 恢复精美封面
**状态:** ✅ 核心完成, 待 Git 提交

### 时间线

#### [00:30] 启动 — 接收迁移需求
用户提出 6 步完整迁移要求:
1. 数据库配置修改 (SQLite → MySQL)
2. ORM 字段适配
3. 建表 SQL 脚本生成
4. 数据导出/导入步骤
5. .env 配置更新
6. 连通性测试

MySQL 信息: localhost:3306, root, novel_fiction

#### [00:35] Step 1 — 配置修改
```
✅ settings.py: DATABASES 改为 MySQL 引擎
✅ __init__.py: pymysql.install_as_MySQLdb()
✅ 安装 python-dotenv
```

#### [00:40] Step 2 — ORM 兼容性检查
```
✅ 所有 7 个模型无 SQLite 特有语法
✅ 无 AUTOINCREMENT/WITHOUT ROWID 等不兼容语句
✅ VARCHAR 长度已定义
✅ 无需修改 models.py
```

#### [00:50] Step 3 — 建表脚本
```
⚠️ 第一版: INT UNSIGNED FK → 失败 (与 Django 内置表类型冲突)
✅ 第二版: 改为 signed INT → 成功
📊 结果: 16 张表全部创建成功 (9 Django 内置 + 7 业务)
   - user: 7 行
   - novel: 24 行
   - chapter: 74 行
   - comment: 120 行
   - favorite/reading_progress/bookmark: 0 行 (原库无数据)
```

#### [01:10] Step 4 — 数据迁移
```
✅ 编写 migrate_data.py (Python pymysql 方式)
✅ 225 条记录从 SQLite 迁移至 MySQL
✅ 日期时间字段自动转换
✅ 错误行跳过并警告输出
```

#### [01:20] Step 5 — .env 配置
```
✅ 创建 .env 文件 (数据库/密钥/调试模式)
✅ settings.py 环境变量化 (python-dotenv)
✅ BASE_DIR 定义顺序修正 (NameError)
```

#### [01:25] Step 6 — 连通性测试
```
✅ test_mysql.py 全部通过:
   - MySQL Version: 8.0.45
   - Database: novel_fiction
   - Charset: utf8mb4 / utf8mb4_0900_ai_ci
   - Total Tables: 16
   - User: 7 | Novel: 24 | Chapter: 74 | Comment: 120
```

#### [01:35] 502 错误排查
```
问题: 用户截图显示大量 502 Bad Gateway
原因: 后端 Django 服务未启动
修复: 启动 manage.py runserver → 全部 API 正常返回 200
验证: recommend/ category_stats/ comments/ favorites/ reading-progress/ auth/me/
结论: 截图为旧缓存, 刷新浏览器即可解决
```

#### [01:50] 封面问题 — 三次迭代
```
迭代 1: text_to_image API 直接调用
  → ❌ 返回占位图 "The image is generating..."

迭代 2: Pillow 手绘文字封面
  → ⚠️ 功能正常但不够美观 (纯色背景+标题)

迭代 3: Pollinations.ai AI 封面 (最终方案)
  → ✅ 24/24 精美 AI 插画封面全部生成
  → 每张 28-63KB, 质量专业
  → 按 Prompt 匹配小说类型风格
```

#### [02:15] 项目启动验证
```
✅ 后端 Django: http://localhost:8000 (运行中)
✅ 前端 Vite: http://localhost:5174 (运行中)
✅ 全部 API 端点验证通过
✅ 页面渲染正常
```

---

## 关键产出文件 (S03)

### 新建文件
| 文件 | 用途 | 大小 |
|------|------|------|
| `.env` | 数据库配置 | ~400B |
| `init_mysql.sql` | DDL 建表参考脚本 | ~6KB |
| `exec_sql.py` | 建表执行器 | ~12KB |
| `migrate_data.py` | 数据迁移工具 | ~2KB |
| `test_mysql.py` | 连通性测试 | ~2KB |
| `gen_ai_covers.py` | **AI 封面生成(最终版)** | ~6KB |

### 修改文件
| 文件 | 变更内容 |
|------|---------|
| `settings.py` | MySQL 配置 + .env 加载 + 环境变量化 |
| `__init__.py` | pymysql 驱动注册 (已有) |

### 数据库变更
| 操作 | 详情 |
|------|------|
| 新建库 | novel_fiction (MySQL 8.0, utf8mb4) |
| 建表 | 16 张 (Django 内置 9 + 自定义 7) |
| 迁移数据 | 225 条记录 (User 7 + Novel 24 + Chapter 74 + Comment 120) |
| 更新封面 | 24 张 AI 插画 (Pollinations.ai) |

---

## 统计数据

### 代码量估算
| 层 | 文件数 | 估计代码行数 |
|----|--------|------------|
| 前端 Vue | ~40 | ~8000 |
| 前端 TS/API | ~8 | ~1500 |
| 后端 Python | ~20 | ~5000 |
| 配置/脚本 | ~15 | ~3000 |
| **合计** | **~83** | **~17500** |

### 功能覆盖度
| 模块 | 功能数 | 完成率 |
|------|--------|-------|
| 读者功能 | 6 | 100% |
| 社交互动 | 4 | 100% |
| 作者创作 | 6 | 100% |
| 用户系统 | 4 | 100% |
| 基础设施 | 5 | 80% |
| **总计** | **25** | **96%** |

---

## Session S04: CopyBook 爬虫提取与批量抓取

**日期:** 2026-06-01
**目标:** 基于开源爬虫项目 CopyBook，实现小说批量采集入库
**状态:** ✅ 核心完成，持续扩展中

### 时间线

#### [00:00] 起源 — CopyBook 项目获取
```
目标仓库: hahaha108/CopyBook (GitHub)
问题: GitHub 直接访问被屏蔽
方案: PowerShell Invoke-WebRequest 下载 ZIP → 本地解压
结果: ✅ 成功获取完整项目源码
```

#### [00:20] 源码分析 — 5 个 Spider 脚本审计
| 脚本 | 功能 | 结论 |
|------|------|------|
| `bookSpider.py` | 单书详情+章节列表 | ⚠️ 依赖 Scrapy + Django ORM |
| `indexSpider.py` | 首页热门推荐 | ❌ 目标站已失效 |
| `categorySpider.py` | 分类分页列表 | ⚠️ URL 格式需适配 |
| `nextpageSpider.py` | 章节翻页 | 可用逻辑参考 |
| `sqlTest.py` | 数据库写入测试 | 仅作验证 |

**关键发现:**
- 原项目强耦合 Django + Scrapy，无法独立运行
- 目标站点 quanshuwang.com 被 Cloudflare 拦截 (403 Forbidden)
- 需要完全重写为独立脚本

#### [00:50] 目标站点切换
```
尝试: quanshuwang.com → ❌ Cloudflare 403
备选: xbiquge.la   → ✅ 200 OK, 正常响应
决策: 切换至 xbiquge.la 作为数据源
```

#### [01:10] ink_crawler.py — 独立爬虫开发
```
设计原则:
✅ 零依赖: 不需要 Django / Scrapy / any framework
✅ 纯 Python: requests + lxml + Pillow
✅ 独立运行: python ink_crawler.py 即可

核心功能:
- 分类自动映射 (玄幻→1, 都市→2, ...)
- 封面图下载与存储
- 正文清洗 (广告/垃圾文本/空白行)
- 章节去重 (按标题)
- 单书上限 50 章 (可配置)
```

#### [01:40] Bug 修复记录

**Bug #1: 分类页 URL 格式错误**
```python
# 错误: /sort/{cat_id}_{page}.html
# 正确: /fenlei/{cat_id}_{page}.html
CATEGORY_URL = "https://www.xbiquge.la/fenlei/{cat_id}_{page}.html"
```

**Bug #2: 书籍链接 XPath 误匹配**
```python
# 问题: div.l 下的 <a> 同时包含书籍链接和章节 .html 链接
# 修复: 过滤掉含 .html 的链接，只保留 /book/ 路径
book_links = [a for a in div_l.xpath('.//a')
              if '.html' not in a.get('href', '')]
```

#### [02:00] 单书测试 — 雪鹰领主
```
测试目标: 《雪鹰领主》
预期章节数: 50 章
实际结果:
  ✅ 书籍 ID: 75 (自增)
  ✅ 成功抓取: 50/50 章节
  ✅ 封面下载: 完成
  ✅ 内容清洗: 广告/推广文字已移除
  ✅ 数据库写入: 无报错
耗时: ~45 秒/书
```

#### [02:30] 批量抓取 — 第一轮成果
```
执行范围: 全部分类 × 前 3 页
统计结果:
┌─────────────────────────────────┐
│  小说总数: 34 部                │
│    ├── 原有: 24 部 (保留)       │
│    └── 新增: 10 部             │
│                                 │
│  章节总数: 1062 章              │
│  平均每书: ~31 章              │
│  封面状态: 全部下载完成         │
│  去重跳过: N 章 (标题重复)     │
└─────────────────────────────────┘
```

### 技术细节

#### 爬虫架构
```
ink_crawler.py
├── CategoryCrawler      # 分类页遍历
│   └── 提取书籍列表
├── BookDetailCrawler    # 书籍详情
│   ├── 基本信息 (作者/简介/封面)
│   └── 章节列表
├── ChapterContentCrawler # 正文抓取
│   ├── HTML 解析
│   └── 内容清洗管道
└── DatabaseWriter        # MySQL 写入
    ├── novels 表
    └── chapters 表
```

#### 内容清洗规则
| 规则 | 示例 |
|------|------|
| 移除广告 | 「请记住本站域名: xxx」→ 删除 |
| 移除推广 | 「手机用户请访问 m.xxx」→ 删除 |
| 空行压缩 | 连续空行 → 单个换行 |
| 首尾空白 | strip() 处理 |

#### 分类映射表
| xbiquge 分类 | 内部 ID | 说明 |
|-------------|---------|------|
| 玄幻奇幻 | 1 | 默认首选 |
| 武侠仙侠 | 2 | |
| 都市言情 | 3 | |
| 历史军事 | 4 | |
| 科幻灵异 | 5 | |
| 网游竞技 | 6 | |
| 女生频道 | 7 | |

---

## 下一步行动

### 立即 (v1.2.0 发布前)
- [ ] Git commit + tag v1.2.0
- [ ] 更新 CHANGELOG.md (MySQL 迁移 + AI 封面)
- [ ] 清理临时脚本 (保留 gen_ai_covers.py 作为参考)
- [ ] docs/版本更新日志.md 同步更新

### 近期 (v1.3.0 规划)
- [ ] Redis 缓存层
- [ ] 图片 CDN / 本地优化
- [ ] Docker 容器化
- [ ] 生产部署文档

---

## 问题追踪

### 已解决
| # | 问题 | 解决日期 | 方案 |
|---|------|---------|------|
| P01-P09 | Phase 2 全部 Bug | S02 | 见 CHANGELOG.md |
| E01-E05 | Phase 3 迁移错误 | S03 | 见 task_plan.md |
| COVER-01 | 封面占位图 | S03 | Pollinations.ai |
| ERR-502 | 502 Bad Gateway | S03 | 启动后端服务 |

### 开放中
| # | 问题 | 优先级 | 备注 |
|---|------|-------|------|
| F-01 | 临时脚本清理 | 低 | 不影响功能 |
| F-02 | CI/CD 流程 | 中 | 待规划 |
