# 墨香书阁 — 技术发现与决策记录

> 最后更新: 2026-05-31

---

## 架构决策

### AD-01: 前后端分离架构
**决策:** Vue 3 (SPA) + Django DRF (REST API)
**原因:**
- 前后端独立部署、扩展
- 前端可复用 API (未来 App/小程序)
- DRF 自动生成分页/过滤/权限

### AD-02: Session 认证 vs JWT
**决策:** Session/Cookie (CSRF 豁免)
**原因:**
- 简化前端 token 管理逻辑
- CSRF 豁免适配 SPA 代理场景
- `update_session_authhash` 支持改密不登出

### AD-03: Vite Proxy 统一代理
**决策:** baseURL=`/api` → Vite proxy → `127.0.0.1:8000`
**原因:**
- 消除跨域问题 (同源请求)
- Cookie 正常传递
- 开发/生产环境统一

### AD-04: SQLite → MySQL 迁移 (v1.2)
**决策:** 使用 pymysql 驱动, utf8mb4 字符集
**原因:**
- SQLite 并发写入性能瓶颈
- MySQL 生产级可靠性
- InnoDB 事务支持
- **关键发现:** FK 列必须用 signed INT (与 Django 内置 auth 表兼容)

### AD-05: AI 封面方案选型
**决策过程:**
1. **Trae text_to_image API** → ❌ IDE 外部返回占位图
2. **Pillow 手绘封面** → ⚠️ 功能可用但不够精美
3. **Pollinations.ai** → ✅ 免费、无需认证、质量高

---

## 技术发现

### T-01: DRF 分页响应格式
```python
# ModelViewSet.list() 返回的不是数组！
{ "count": 24, "next": "...", "previous": null, "results": [...] }
# 前端必须用 res.results 而非直接 forEach(res)
```

### T-02: Axios 拦截器双重解包陷阱
```typescript
// request.ts 拦截器已解包:
(response) => response.data   // ← 第一次解包

// 如果前端再取 .data 就会得到 undefined:
const data = res.data         // ← 第二次解包 = undefined!
```
**影响范围:** AuthorCenter / AuthorChapterList / AuthorChapterEdit / AuthorNovelEdit (5处)

### T-03: DRF ModelSerializer 字段命名
```python
# 模型外键字段名 vs RESTful 惯例:
Bookmark.novel    # Django 用模型字段名 "novel"
# NOT "novel_id"  # RESTful 惯例外键后缀
```
**修复:** 前端发送 `{ novel: id }` 而非 `{ novel_id: id }`

### T-04: Google Fonts 国内不可达
- `fonts.googleapis.com` / `fonts.gstatic.com` 被 GFW 封锁
- 替代方案: `fonts.loli.net` (国内常用镜像)

### T-05: Django MySQL FK 类型兼容性
```sql
-- Django 内置 auth_user.id 是 signed INT
-- 自定义表 FK 若用 INT UNSIGNED 会报错:
-- ERROR 1832: Cannot change column 'user_id': used in a foreign key constraint 'fk_xxx' and incompatible type
-- 解决: 全部使用 signed INT
```

### T-06: text_to_image API 行为差异
| 环境 | 行为 |
|------|------|
| Trae IDE 内置浏览器 | 返回真实 AI 图片 |
| 外部浏览器/Python requests | 返回占位图 ("The image is generating...") |
| PowerShell Invoke-WebRequest | 返回占位图 (172KB JPEG) |

**根因:** 该 API 可能基于 Session/Cookie/Referer 判断请求来源

### T-07: Pollinations.ai 免费图片生成
```
URL 格式: https://image.pollinations.ai/prompt/{encoded_prompt}?width=400&height=560&nologo=true&seed={seed}
特点:
- 完全免费, 无需 API Key
- 支持 SDXL 模型
- seed 参数保证同一 prompt 产出一致
- 响应时间: 5-30秒 (取决于服务器负载)
- 超时处理: 需要 retry 机制 (90s timeout)
```

### T-08: Python dotenv 加载顺序
```python
# 错误顺序 (NameError):
load_dotenv(BASE_DIR / '.env')  # BASE_DIR 还没定义!

# 正确顺序:
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
```

### T-09: GitHub 访问替代方案
- **问题:** `git clone` 在某些网络环境下不通
- **方案:** 用 PowerShell `Invoke-WebRequest` 下载 ZIP 替代
- **注意仓库地址:** 正确为 `hahaha108/CopyBook` (不是 `hahaha100`)
- **适用场景:** 代码拉取/模板下载等需要 GitHub 资源的场景

### T-10: Cloudflare 反爬保护
- **站点:** quanshuwang.com 返回 HTTP 403
- **尝试:** cloudscraper 库也无法绕过 Cloudflare 防护
- **结论:** 该站不可用, 需更换目标站点

### T-11: xbiquge.la 站点结构
```
分类页:    /xuanhuanxiaoshuo/
书籍列表:  div.l 容器
分页:      /fenlei/{cat_id}_{page}.html
书籍链接:  无 .html 后缀 (章节链接有)
详情页:   /{id}/{id2}/
```
**关键差异:** 书籍列表页链接与章节页链接的后缀规则不同, 解析时需区分处理

### T-12: Python requests 代理问题
```python
# Windows 系统代理设置会干扰 requests 行为
# 解决方案:
session = requests.Session()
session.trust_env = False          # 忽略系统代理
os.environ.pop('HTTP_PROXY', None) # 清除环境变量
os.environ.pop('HTTPS_PROXY', None)
```
**症状:** 请求超时、连接被重置、SSL 错误等不明原因的网络异常

### T-13: lxml FutureWarning
```python
# 触发警告的写法:
if not html:   # 新版 lxml 会触发 FutureWarning

# 推荐改法:
if len(html) == 0 or html is None:
```
**影响版本:** lxml >= 5.0

### T-14: 爬虫内容清洗规则
| 清洗项 | 处理方式 |
|--------|----------|
| 空白字符 | 去除 `\xa0` (NBSP)、`\u3000` (全角空格) |
| 广告 URL | 正则移除 http/https 链接 |
| 结束标记 | 去除 "本章完" 等文本 |
| 站点水印 | 去除 "笔趣阁" 等站点名称文字 |
| 空章过滤 | 每章 >50 字才入库 |

### AD-06: 爬虫架构决策
**决策:** 独立 Python 脚本 (非 Django 集成)
**原因:**
1. **解耦性:** 爬虫逻辑与 Web 服务独立, 故障互不影响
2. **灵活性:** 可单独调度 (cron/手动), 不依赖 Django 进程
3. **调试方便:** 独立运行, 无需启动完整 Django 服务
4. **部署简单:** 单文件/单模块即可执行, 降低复杂度
5. **扩展性:** 未来可迁移到 Scrapy 框架无需改动 Django 代码

---

## 数据模型设计笔记

### Novel 模型关键字段
| 字段 | 类型 | 说明 |
|------|------|------|
| status | SmallInt | 0=连载 1=完结 2=停更 |
| audit_status | SmallInt | 0=草稿 1=审核中 2=已发布 3=驳回 |
| tags | VARCHAR(200) | 逗号分隔字符串 |
| cover | VARCHAR(500) | URL 或本地路径 |
| author_user_id | FK→User | 关联作者用户(可为空) |

### Bookmark 的 position 字段
- 类型: IntegerField(default=0)
- 含义: 阅读位置百分比 (0-100)
- v1.1 新增, 解决书签无位置信息问题

---

## 前端组件依赖关系

```
App.vue
├── Router (router/index.ts)
│   ├── Home.vue          ← 首页 (推荐/分类/统计)
│   ├── NovelDetail.vue   ← 详情 (章节/评论/收藏)
│   ├── Reader.vue        ← 阅读器 (进度/书签)
│   ├── Login.vue         ← 登录注册
│   ├── UserCenter.vue    ← 个人中心 (改密码)
│   ├── AuthorCenter.vue  ← 作者后台入口
│   │   ├── AuthorNovelEdit.vue   ← 作品编辑
│   │   ├── AuthorChapterList.vue ← 章节列表
│   │   └── AuthorChapterEdit.vue ← 章节编辑器
│   ├── NovelList.vue     ← 分类列表
│   ├── Rankings.vue      ← 排行榜
│   ├── Search.vue        ← 搜索
│   └── NotFound.vue      ← 404 页面
└── request.ts            ← Axios 全局配置
    └── api/index.ts      ← API 封装层
```

---

## 后端 API 路由结构

```
/api/
├── novels/           → NovelViewSet (ReadOnly)
│   ├── {id}/        → retrieve
│   ├── {id}/chapters/     → chapters action
│   ├── search/             → search action
│   ├── recommend/          → recommend action
│   └── category_stats/     → category_stats action
├── chapters/        → ChapterViewSet (ReadOnly)
│   └── {id}/        → retrieve (含上/下章)
├── auth/            → AuthViewSet
│   ├── login/              → POST 登录
│   ├── register/           → POST 注册
│   ├── logout/             → POST 登出
│   ├── me/                 → GET 当前用户
│   ├── update_profile/     → PUT 修改资料
│   └── change_password/    → POST 改密码
├── favorites/       → FavoriteViewSet
│   ├── POST         → 添加收藏
│   ├── delete_by_novel/    → DELETE 按小说删
│   └── check/             → GET 是否已收藏
├── reading-progress/ → ReadingProgressViewSet
│   ├── list/               → GET 列表
│   ├── get_progress/       → GET 单本进度
│   └── update_progress/    → POST 更新进度
├── bookmarks/       → BookmarkViewSet
│   ├── {id}/        → DELETE 删除
│   └── by_chapter/         → GET 按章节查
├── comments/        → CommentViewSet
│   ├── GET          → 列表 (支持 ?novel= 过滤)
│   ├── POST         → 发评论
│   ├── {id}/        → DELETE 删评论
│   └── stats/              → GET 评分统计
├── author/novels/   → AuthorNovelViewSet
│   ├── stats/              → GET 作者统计
│   ├── {id}/publish/       → POST 发布
│   ├── {id}/take_down/     → POST 下架
│   └── upload_cover/       → POST 上传封面
└── author/chapters/ → AuthorChapterViewSet
    ├── {id}/publish/       → POST 发布章节
    └── {id}/take_down/     → POST 下架章节
```
