# 更新日志

## [v1.2.0] - 2026-05-31

### MySQL 迁移 + AI 封面 + 爬虫内容采集

---

### 🗄️ 数据库迁移 (SQLite → MySQL)
- **数据库引擎**: SQLite3 → MySQL 8.0 (utf8mb4)
- **驱动**: pymysql (`pymysql.install_as_MySQLdb()`)
- **建表**: 16 张表（Django 内置 9 + 业务表 7）
- **数据迁移**: 225 条记录无损迁移
- **配置文件**: `.env` 环境变量化 + `python-dotenv`
- **连通性测试**: `test_mysql.py` 全部通过

### 🎨 AI 精美封面
- **方案选型**: Trae text_to_image API(不可用) → Pollinations.ai
- **生成结果**: 24/24 本小说全部重新生成 AI 插画封面
- **技术细节**: SDXL 模型, seed 参数保证一致性, 28-63KB/张

### 🕷️ 独立爬虫开发 (ink_crawler.py)
- **源项目**: CopyBook (hahaha108/CopyBook) 剥离改造
- **目标站**: xbiquge.la (quanshuwang.com 被 Cloudflare 屏蔽)
- **架构**: 零框架依赖独立 Python 脚本 (requests + lxml + pymysql)
- **功能**: 分类列表→详情页→章节目录→正文采集→自动入库
- **清洗规则**: 去广告/去乱码/去水印/空章过滤(>50字)
- **爬取成果**: 13 本新小说 × 50 章 = 650+ 章入库
- **最终规模**: 37 本小说 / 1,212 章

### 📁 新增文件
| 文件 | 用途 |
|------|------|
| `.env` | MySQL 连接配置 |
| `ink_crawler.py` | 独立小说爬虫脚本 |
| `gen_ai_covers.py` | AI 封面批量生成 |
| `task_plan.md` | 开发计划文档 |
| `findings.md` | 技术发现记录 |
| `progress.md` | 进度日志 |

### 🔧 修改文件
| 文件 | 变更 |
|------|------|
| `settings.py` | MySQL 配置 + .env 加载 + 环境变量化 |
| `__init__.py` | pymysql 驱动注册 |

---

## [v1.1.0] - 2026-05-29

### v1.0 后首次功能迭代 — Bug 修复 + 新功能 + 基础设施完善

---

### 🐛 Bug 修复（11 项）

#### 接口层修复
| # | 问题 | 根因 | 修复文件 |
|---|------|------|---------|
| 1 | 阅读进度 `TypeError: res.forEach is not a function` | DRF `list` 返回分页对象 `{results:[]}`，非数组 | [NovelDetail.vue](novel_frontend/src/views/NovelDetail.vue) |
| 2 | 阅读进度/书签 `500 Internal Server Error` | `ReadingProgressSerializer` / `BookmarkSerializer` 的 `user` 字段同时声明 read_only + write_only → AssertionError | [user_serializers.py](novel_backend/novels/user_serializers.py) |
| 3 | 作者中心 `Cannot read properties of undefined (reading 'results')` | Axios 拦截器已解包 `.data`，前端又多取一层 → undefined | [AuthorCenter.vue](novel_frontend/src/views/AuthorCenter.vue) |
| 4 | 章节管理同上 `undefined.results` | 同类双重解包 bug | [AuthorChapterList.vue](novel_frontend/src/views/AuthorChapterList.vue) |
| 5 | 章节编辑器 `Cannot read 'title' of undefined` | 同类双重解包（2 处） | [AuthorChapterEdit.vue](novel_frontend/src/views/AuthorChapterEdit.vue) |
| 6 | 作品编辑器路由跳转 id 为 undefined | 同类双重解包 | [AuthorNovelEdit.vue](novel_frontend/src/views/AuthorNovelEdit.vue) |
| 7 | 书签添加 `400 Bad Request` | 前端发送 `novel_id`/`chapter_id`，后端期望 `novel`/`chapter`（DRF ModelSerializer 用模型字段名） | [Reader.vue](novel_frontend/src/views/Reader.vue) + [api/index.ts](novel_frontend/src/api/index.ts) |
| 8 | 小说简介不显示 | `NovelListSerializer` fields 列表缺少 `description` 字段 | [serializers.py](novel_backend/novels/serializers.py) |

#### UI / 体验修复
| # | 问题 | 修复 |
|---|------|------|
| 9 | Google Fonts 超时 `ERR_CONNECTION_TIMED_OUT` | 8 个 Vue 组件字体源从 `fonts.googleapis.com` 替换为国内镜像 `fonts.loli.net` |
| 10 | 评论提交按钮过于透明看不见 | 加深背景色、加粗字重、加大尺寸、加阴影、disabled 态优化 |
| 11 | IDE 内置浏览器 React Error #185 | Trae IDE 预览面板内部问题，非项目代码问题 |

---

### ✨ 新功能（5 项）

#### 1. 404 专用页面
- **文件**：[NotFound.vue](novel_frontend/src/views/NotFound.vue)（新建）
- **内容**：浮动书本 SVG 动画 + 返回首页/搜索入口 + 分类推荐链接
- **路由**：`/:pathMatch(.*)*` 从 Home.vue 改为 NotFound.vue
- **适配**：480px 移动端断点

#### 2. 评论删除功能
- **位置**：[NovelDetail.vue](novel_frontend/src/views/NovelDetail.vue) 评论区
- **逻辑**：
  - 仅评论作者本人可见删除按钮（✕ 图标）
  - 点击弹出 `ElMessageBox` 确认框
  - 调用 `commentApi.remove(id)` → 列表即时移除
  - 后端已有权限校验（`request.user == comment.user`）
- **样式**：hover 变红色，圆角按钮

#### 3. 修改密码功能
- **后端**：[user_views.py](novel_backend/novels/user_views.py) 新增 `change_password` action
  - 校验旧密码正确性（`check_password`）
  - 新密码 ≥ 6 位
  - `update_session_authhash` 保持登录态不丢失
- **前端 API**：[api/index.ts](novel_frontend/src/api/index.ts) 新增 `authApi.changePassword()`
- **前端 UI**：[UserCenter.vue](novel_frontend/src/views/UserCenter.vue)
  - 个人信息区新增「修改密码」按钮（带锁图标）
  - 弹窗表单：旧密码 / 新密码 / 确认密码
  - 字段级错误提示提取（DRF 错误格式兼容）
  - 二次确认一致性校验

#### 4. 小说标签展示
- **详情页** [NovelDetail.vue](novel_frontend/src/views/NovelDetail.vue)：Hero 区域分类标签旁展示自定义标签胶囊（灰色边框）
- **首页** [Home.vue](novel_frontend/src/views/Home.vue)：卡片作者名下方显示小标签（圆角药丸样式）
- **数据源**：`novel.tags` 字段（逗号分隔字符串），通过 `parsedTags` 计算属性解析
- **序列化器**：`NovelListSerializer` 已包含 `tags` 字段

#### 5. 作者页面响应式适配
以下 4 个页面新增 `@media (max-width:768px)` 和 `(max-width:480px)` 断点：

| 页面 | 768px 适配 | 480px 适配 |
|------|----------|----------|
| [AuthorCenter.vue](novel_frontend/src/views/AuthorCenter.vue) | 数据看板 2×2 网格、作品列表压缩、按钮全宽 | 标题缩小 |
| [AuthorNovelEdit.vue](novel_frontend/src/views/AuthorNovelEdit.vue) | 表单单列、封面区缩小、按钮纵向排列 | 标题缩小 |
| [AuthorChapterList.vue](novel_frontend/src/views/AuthorChapterList.vue) | 章节项 2 列→紧凑、操作按钮纵向 | 标题缩小 |
| [AuthorChapterEdit.vue](novel_frontend/src/views/AuthorChapterEdit.vue) | 编辑区 padding 压缩、工具栏换行、字号放大 | 内容区高度调整 |

---

### 🔧 数据库变更

| 迁移 | 文件 | 说明 |
|------|------|------|
| `0006_add_bookmark_position` | [models.py](novel_backend/novels/models.py) | Bookmark 模型新增 `position = IntegerField(default=0)` 字段，记录阅读位置百分比 |

---

### 🏗 基础设施

| 项目 | 文件 | 说明 |
|------|------|------|
| `.gitignore` | [.gitignore](/.gitignore) | 排除 `__pycache__/`, `db.sqlite3`, `node_modules/`, `media/`, `.venv/` 等 |
| Git 提交 | commit `5cbb2ba` | 128 文件变更，+13351/-3009 行，打标签 `v1.0.0` |
| 版本日志 | [CHANGELOG.md](/CHANGELOG.md) | v1.0.0 完整发布说明 |
| 版本日志 | [docs/版本更新日志.md](docs/版本更新日志.md) | v0.1~v1.1 全版本历史 |

---

### 📊 当前项目规模

| 维度 | 数值 |
|------|------|
| 总提交数 | 8（含本次迭代） |
| Vue 页面 | **13 个**（原 12 + NotFound） |
| 后端 ViewSet | 8 个（Novel/Chapter/Auth/Favorite/Progress/Bookmark/Comment/Author） |
| API 端点 | 35+ 个 RESTful 接口 |
| 数据库迁移 | 6 次（0001~0006） |
| 文档 | **18 份** |
| 响应式页面 | **12/13**（仅 NotFound 有移动端适配，4 个作者页本版新增） |

---

[v1.1.0]: https://github.com/your-repo/inkfiction/releases/tag/v1.1.0

---

### 🔍 问题诊断记录（Problems & Diagnostics）

> 本节记录 v1.0 → v1.1 迭代中遇到的全部问题、排查过程与根因分析，供后续维护参考。

---

#### P01: 阅读进度接口 500 — `AssertionError`

| 属性 | 详情 |
|------|------|
| **现象** | `POST /api/reading-progress/` 返回 500，控制台 `保存阅读进度失败` |
| **报错** | 后端日志 `AssertionError`（无具体行号） |
| **影响页面** | Reader.vue 阅读器 |

**诊断过程：**
```
1. 前端 request.ts 拦截器只对 ≥500 打 error → 确认是后端崩了
2. 检查 user_views.py ReadingProgressViewSet → 标准 ModelViewSet，无明显问题
3. 检查 user_serializers.py ReadingProgressSerializer:
   ┌─────────────────────────────────────────────┐
   │ read_only_fields = ['id', 'user', ...]     │ ← 声明 user 只读
   │ extra_kwargs = {'user': {'write_only'}}      │ ← 又声明 user 只写
   │                                             │
   │ DRF 断言: 同一字段不能同时 read+write only    │
   └─────────────────────────────────────────────┘
4. 同类检查发现 BookmarkSerializer 也有相同问题
5. 回顾历史: FavoriteSerializer 在更早的迭代中已修复过同类 bug
```

**根因**：DRF `ModelSerializer` 的字段声明冲突。`read_only_fields` 和 `extra_kwargs.write_only` 对同一字段 `user` 同时生效时触发内部 AssertionError。

**修复**：删除两处序列化器的 `extra_kwargs` 块，保留 `read_only_fields` 即可（`perform_create` 中通过 `serializer.save(user=request.user)` 注入）。

**同类问题清单**：
- `FavoriteSerializer` — 已在 v1.0 修复
- `ReadingProgressSerializer` — v1.1 修复 ✅
- `BookmarkSerializer` — v1.1 修复 ✅

---

#### P02: 作者中心 `Cannot read properties of undefined (reading 'results')`

| 属性 | 详情 |
|------|------|
| **现象** | AuthorCenter.vue 加载时报 TypeError，作品列表为空 |
| **报错** | `res.results is not a function` / `Cannot read 'results' of undefined` |
| **影响页面** | AuthorCenter / AuthorChapterList / AuthorChapterEdit / AuthorNovelEdit |

**诊断过程：**
```
1. 错误堆栈指向 AuthorCenter.vue load() 函数
2. 代码: const data = listRes.data; works.value = data.results || []
3. 检查 request.ts 响应拦截器:
   (response) => response.data   ← 已解包一次!
4. listRes 已经是 { count, results: [...] }
5. listRes.data = undefined → undefined.results → 💥
6. 全局搜索 res\.data\. 发现 5 处同类问题
```

**根因**：[request.ts:25](novel_frontend/src/utils/request.ts) Axios 响应拦截器做了 `(response) => response.data` 解包，但作者模块 4 个文件又多取了一层 `.data`。

**修复模式**：
```diff
- const data = listRes.data
- works.value = Array.isArray(data) ? data : (data.results || [])
+ works.value = Array.isArray(listRes) ? listRes : (listRes.results || [])
```

**涉及文件**：AuthorCenter / AuthorChapterList / AuthorChapterEdit(×2) / AuthorNovelEdit

---

#### P03: 小说详情 `TypeError: res.forEach is not a function`

| 属性 | 详情 |
|------|------|
| **现象** | 进入小说详情页控制台报错，已读章节检测失败 |
| **报错** | `TypeError: res.forEach is not a function` at NovelDetail.vue:316 |
| **影响功能** | 已读章节高亮、阅读进度恢复 |

**诊断过程：**
```
1. NovelDetail.vue loadReadChapters():
   const res = await progressApi.list()
   res.forEach(...)          ← 对对象调 forEach

2. DRF ModelViewSet.list() 默认返回分页响应:
   {
     "count": 10,
     "next": null,
     "previous": null,
     "results": [...]        ← 数据在这里
   }

3. UserCenter.vue 同位置已经做了兼容:
   res.results || []         ← 正确写法

4. NovelDetail.vue 漏掉了这个兼容处理
```

**根因**：DRF 分页响应是对象而非数组，直接 `.forEach()` 报类型错误。

**修复**：`(res.results || []).forEach(...)`，与 UserCenter.vue 保持一致。

---

#### P04: 书签添加 400 Bad Request

| 属性 | 详情 |
|------|------|
| **现象** | 点击书签图标无反应，Network 显示 POST 400 |
| **报错** | `{"novel": ["This field is required."], "chapter": ["This field is required."]}` |
| **影响功能** | 阅读器书签功能完全不可用 |

**诊断过程：**
```
1. 浏览器 Network: POST /api/bookmarks/ → 400
2. 后端直接测试（Python 脚本）→ 201 成功 ❓
3. 对比请求差异:

   浏览器发送:       {"novel_id": 26, "chapter_id": 76, ...}  ← 错误
   Python 测试:     {"novel": 26, "chapter": 76, ...}          ← 正确

4. DRF ModelSerializer 使用模型字段名做反序列化:
   Bookmark.novel   → 字段名 "novel"（不是 "novel_id"）
   Bookmark.chapter  → 字段名 "chapter"（不是 "chapter_id"）

5. 前端 api/index.ts 类型定义也是错的:
   novel_id: number    ← 应为 novel
   chapter_id: number  ← 应为 chapter
```

**根因**：DRF `ModelSerializer` 用 Django 模型字段名（`novel`, `chapter`），但前端按 RESTful 惯例用了外键后缀形式（`novel_id`, `chapter_id`）。两者不匹配导致后端校验失败。

**修复**：前端字段名从 `novel_id`/`chapter_id` 改为 `novel`/`chapter`。

**验证方法**：编写对比测试脚本，分别用正确和错误字段名调用 ViewSet.create()，确认错误字段名返回 400 且错误信息明确。

---

#### P05: Google Fonts `ERR_CONNECTION_TIMED_OUT`

| 属性 | 详情 |
|------|------|
| **现象** | 所有页面加载时控制台报网络超时，字体不显示回退到系统默认 |
| **报错** | `net::ERR_CONNECTION_TIMED_OUT https://fonts.gstatic.com/s/notoserifsc/...woff2` |
| **影响范围** | 8 个 Vue 组件（Home/NovelDetail/Reader/Login/UserCenter/Rankings/Search/NovelList） |

**诊断过程：**
```
1. fonts.googleapis.com 被 GFW 封锁（国内无法访问）
2. CSS @import 引用了 Google Fonts CDN → 浏览器加载字体文件超时
3. 字体文件托管在 fonts.gstatic.com → 同样被墙
4. 影响: Noto Serif SC / Cormorant Garamond / Libre Baskerville / Noto Sans TC
```

**根因**：Google Fonts 服务在国内网络环境不可达。

**修复**：全局替换 CDN 地址 `fonts.googleapis.com` → `fonts.loli.net`（国内常用加速镜像）。8 个文件批量替换。

---

#### P06: Session Cookie 跨域丢失（v1.0 遗留问题）

| 属性 | 详情 |
|------|------|
| **现象** | 登录成功后跳转其他页面变未登录状态，每次点创作都要重新登录 |
| **报错** | 反复出现 401 / 403 错误 |
| **影响范围** | 所有需要认证的 API 接口 |

**诊断过程（多轮迭代）：**
```
第1轮: 发现 CSRF 问题
  → 创建 CsrfExemptSessionAuthentication + CsrfExemptApiMiddleware
  → 结果: 部分接口好了，但 session 仍丢失

第2轮: 发现跨域问题
  → 前端 baseURL: http://localhost:8000/api
  → 后端运行在: 127.0.0.1:8000
  → 浏览器认为这是不同域名 → cookie 不传递
  → 修复: baseURL 改为 /api + Vite proxy

第3轮: Cookie Domain 问题
  → Django 默认 Set-Cookie: Domain=127.0.0.1
  → 但浏览器访问 localhost:5173 → 拒绝存储此 cookie
  → 修复: SESSION_COOKIE_DOMAIN = None + SameSite=Lax
```

**根因**：三层叠加问题 —— CSRF 校验 → 跨域阻止 Cookie → Domain 不匹配。

**最终修复方案**：
```
Vite proxy (/api → 127.0.0.1:8000)     ← 消除跨域
SESSION_COOKIE_DOMAIN = None             ← 不自动写 Domain
SESSION_COOKIE_SAMESITE = 'Lax'          ← 代理场景兼容
CsrfExemptApiMiddleware                  ← 豁免中间件层
CsrfExemptSessionAuthentication          ← 豁免 DRF 认证层
```

---

#### P07: 评论提交按钮不可见

| 属性 | 详情 |
|------|------|
| **现象** | 用户反馈"发表评论按钮过于透明看不见" |
| **原因** | 按钮 background 使用 `var(--accent)` (#CA8A04)，在白色背景上对比度不足；disabled 时 opacity 0.5 更淡 |
| **修复** | 背景加深 #B7830A、字重 600、加 box-shadow、padding 加大、hover 加深阴影 |

---

#### P08: 小说简介不显示

| 属性 | 详情 |
|------|------|
| **现象** | 首页卡片和小说列表中 description 字段为空 |
| **根因** | `NovelListSerializer.fields` 列表缺少 `description` 字段 |
| **修复** | serializers.py fields 列表中补上 `description` |

---

#### P09: IDE 内置浏览器 React Error #185

| 属性 | 详情 |
|------|------|
| **现象** | Trae IDE 实时预览面板报 Minified React Error #185 |
| **堆栈来源** | `@byted-icuwe/bundled-deps/compiled/react-dom` |
| **结论** | IDE 预览面板内部的 React hydration 不匹配，非项目代码问题。使用外部浏览器访问即可 |

---

### 📋 诊断方法论总结

| 方法 | 适用场景 | 工具 |
|------|---------|------|
| **端到端测试脚本** | 后端接口验证 | Python 直接调用 ViewSet，绕过 HTTP 层 |
| **对比测试** | 定位字段名/格式问题 | 正确 vs 错误参数分别调用，对比 status code |
| **全局搜索** | 找出同类 bug | `Grep res\.data\.` 或 `grep -rn "forEach"` |
| **浏览器 Network 面板** | 分析实际请求/响应 | F12 → Network → 查看 Request Payload + Response |
| **Django Shell 验证** | 序列化器逻辑确认 | `python manage.py shell` 或内联脚本 |
| **Cookie 审查** | 认证问题排查 | Application → Cookies → 检查 Set-Cookie 头部属性 |

---

## [v1.0.0] - 2026-05-29

### 🎉 首个正式版本发布

墨香书阁（InkFiction）—— 一款 E-Ink 文学气质的在线小说阅读平台。

---

### ✨ 核心功能

#### 读者功能
- **首页展示**：精选推荐 + 分类浏览，25 本预设小说数据
- **小说详情**：封面、简介、章节目录、评分、阅读量统计
- **在线阅读器**：沉浸式阅读体验、滚动进度自动保存、已读章节标记
- **搜索功能**：按标题/作者/分类搜索小说
- **排行榜**：按阅读量/字数/更新时间多维排行
- **用户系统**：注册 / 登录 / Session 持久化认证

#### 社交互动
- **收藏系统**：一键收藏/取消收藏，Vue 动画心跳效果
- **评论评分**：1-5 星评分 + 文字评论，支持纯评论模式
- **阅读记录**：自动追踪阅读进度与历史
- **书签功能**：章节内添加/管理书签

#### 作者创作（完整闭环）
- **作者中心**：作品列表 + 数据看板（作品数/总字数/总阅读量/总章节数）
- **作品管理**：创建/编辑小说信息、封面上传（本地上传）
- **章节管理**：创建/编辑/删除章节、草稿与发布状态切换
- **审核流程**：草稿(0) → 审核中(1) → 已发布(2) / 驳回(3)
- **自动保存**：章节编辑器 8 秒静默保存草稿

---

### 🛠 技术架构

| 层 | 技术 |
|---|------|
| 前端框架 | Vue 3 + TypeScript + Vite |
| UI 组件库 | Element Plus |
| 路由 | Vue Router 4 |
| 状态管理 | Pinia |
| 后端框架 | Django 4.2 + Django REST Framework |
| 数据库 | SQLite |
| 认证方式 | Session/Cookie（CSRF 豁免） |
| 字体方案 | Noto Serif SC + Cormorant Garamond（国内镜像加速） |

---

### 🔧 关键技术修复（v1.0 迭代）

1. **跨域 Session 持久化**
   - Vite dev server proxy 统一代理 `/api` 和 `/media`
   - `SESSION_COOKIE_DOMAIN = None` 阻止 Django 自动写 Domain
   - `SameSite=Lax` 策略适配代理场景

2. **CSRF 免除链路**
   - `CsrfExemptApiMiddleware`（Django 中间件层）
   - `CsrfExemptSessionAuthentication`（DRF 认证层）
   - 对所有 `/api/` 路径豁免 CSRF 校验

3. **序列化器冲突修复**
   - `FavoriteSerializer` / `ReadingProgressSerializer` / `BookmarkSerializer`
   - 移除 `user` 字段的 read_only + write_only 冲突声明

4. **前端响应解包统一**
   - 修复 5 处 `res.data.data` 双重解包 bug（AuthorCenter / AuthorChapterList / AuthorChapterEdit / AuthorNovelEdit）
   - 修复 DRF 分页对象 `.forEach` 类型错误（NovelDetail）

5. **Google Fonts 国内访问**
   - 8 个 Vue 组件字体源从 `fonts.googleapis.com` 替换为 `fonts.loli.net`

6. **UI 优化**
   - 首页卡片布局压缩减少留白
   - 评论提交按钮增强可见性（加粗+阴影+加大尺寸）
   - 小说列表序列化器补全 `description` 字段

---

### 📁 项目结构

```
novel_backend/
├── novels/
│   ├── models.py              # 数据模型（User/Novel/Chapter/Comment/Favorite/ReadingProgress/Bookmark）
│   ├── serializers.py         # 公共序列化器
│   ├── views.py               # 小说/章节公开接口
│   ├── user_views.py          # 用户/收藏/阅读进度/书签接口 + 修改密码
│   ├── author_views.py        # 作者创作接口（CRUD/发布/下架/上传封面）
│   ├── comment_views.py       # 评论评分接口
│   ├── author_serializers.py  # 作者模块序列化器
│   ├── comment_serializers.py # 评论模块序列化器
│   ├── user_serializers.py    # 用户模块序列化器
│   ├── auth.py                # CSRF 豁免认证类
│   └── csrf_middleware.py     # API CSRF 豁免中间件
└── novel_project/settings.py  # Django 配置（Cookie/Session/Media）

novel_frontend/src/
├── views/
│   ├── Home.vue               # 首页（含标签展示）
│   ├── NovelDetail.vue        # 小说详情（含评论区/收藏/评分/评论删除/标签）
│   ├── Reader.vue             # 在线阅读器（含书签功能完整修复）
│   ├── NovelList.vue          # 小说列表
│   ├── Rankings.vue           # 排行榜
│   ├── Search.vue             # 搜索
│   ├── Login.vue              # 登录注册
│   ├── UserCenter.vue         # 用户中心（含修改密码弹窗）
│   ├── AuthorCenter.vue       # 作者中心（响应式）
│   ├── AuthorNovelEdit.vue    # 作品编辑（响应式）
│   ├── AuthorChapterList.vue  # 章节管理（响应式）
│   ├── AuthorChapterEdit.vue  # 章节编辑器（响应式+自动保存）
│   └── NotFound.vue           # 404 页面（新建）
├── api/index.ts               # API 封装层
├── utils/request.ts           # Axios 实例（拦截器/错误处理）
├── utils/image.ts             # 图片路径解析工具
└── router/index.ts            # 路由配置（含权限守卫+404）
```

---

### 📊 数据概览

- 预置小说：**25 本**（玄幻/都市/科幻/言情/悬疑等分类）
- AI 生成封面：**25 张**（SDXL 风格定制 prompt）
- 页面总数：**13 个**（含作者后台 4 个 + 404 页面）
- API 接口：**35+ 个** RESTful 端点
- 文档：**18 份**（需求/设计/数据库/接口/路线图等）
- 数据库迁移：**6 次**

---

### 🚀 快速启动

```bash
# 后端
cd novel_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000

# 前端（新终端）
cd novel_frontend
npm install
npm run dev
# 浏览器打开 http://localhost:5173
```

---

[v1.0.0]: https://github.com/your-repo/inkfiction/releases/tag/v1.0.0
