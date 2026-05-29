# 更新日志

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

### 🔧 关键技术修复（本次迭代）

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
│   ├── user_views.py          # 用户/收藏/阅读进度/书签接口
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
│   ├── Home.vue               # 首页
│   ├── NovelDetail.vue        # 小说详情（含评论区/收藏/评分）
│   ├── Reader.vue             # 在线阅读器
│   ├── NovelList.vue          # 小说列表
│   ├── Rankings.vue           # 排行榜
│   ├── Search.vue             # 搜索
│   ├── Login.vue              # 登录注册
│   ├── UserCenter.vue         # 用户中心（收藏/阅读记录/书签）
│   ├── AuthorCenter.vue       # 作者中心
│   ├── AuthorNovelEdit.vue    # 作品编辑
│   ├── AuthorChapterList.vue  # 章节管理
│   └── AuthorChapterEdit.vue  # 章节编辑器（含自动保存）
├── api/index.ts               # API 封装层
├── utils/request.ts           # Axios 实例（拦截器/错误处理）
├── utils/image.ts             # 图片路径解析工具
└── router/index.ts            # 路由配置（含权限守卫）
```

---

### 📊 数据概览

- 预置小说：**25 本**（玄幻/都市/科幻/言情/悬疑等分类）
- AI 生成封面：**25 张**（SDXL 风格定制 prompt）
- 页面总数：**12 个**（含作者后台 4 个）
- API 接口：**30+ 个** RESTful 端点
- 文档：**16 份**（需求/设计/数据库/接口/路线图等）

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
