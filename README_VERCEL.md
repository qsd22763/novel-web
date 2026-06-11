# 墨香书阁 - Vercel 一体化部署指南

## 项目架构对比

| 特性 | 原版 (main 分支) | 一体化版 (vercel-merge 分支) |
|------|-----------------|---------------------------|
| **前端** | Vue 3 + Vite | Vue 3 + Vite（相同） |
| **后端** | Django + DRF | Express.js + sql.js |
| **数据库** | MySQL | SQLite（内嵌） |
| **部署方式** | Nginx + Gunicorn | Vercel / Docker |
| **适用场景** | 本地开发/自有服务器 | Vercel 云端 / Docker 容器 |

## 目录结构

```
d:\python damo\vue/
├── api/                        # Vercel Serverless API 后端
│   ├── index.js                # Express 入口
│   ├── db.js                   # SQLite 数据库层
│   ├── seed.js                 # 种子数据
│   ├── middleware/
│   │   └── auth.js             # 认证中间件
│   └── routes/
│       ├── novels.js           # 小说 API
│       ├── chapters.js         # 章节 API
│       ├── auth.js             # 认证 API
│       ├── favorites.js        # 收藏 API
│       ├── progress.js         # 阅读进度 API
│       ├── bookmarks.js        # 书签 API
│       ├── comments.js         # 评论 API
│       ├── author.js           # 作者中心 API
│       ├── admin.js            # 管理后台 API
│       ├── checkin.js          # 签到 API
│       ├── membership.js       # 会员 API
│       ├── follow.js           # 关注 API
│       ├── rating.js           # 评分 API
│       └── public.js           # 公开 API
├── novel_frontend/             # Vue 前端（已适配）
│   ├── src/
│   ├── dist/                   # 构建产物
│   ├── vite.config.ts          # 已修改代理目标
│   └── package.json
├── vercel.json                 # Vercel 部署配置
├── Dockerfile                  # Docker 构建配置
├── docker-compose.yml          # Docker Compose 编排
├── package.json                # 根依赖（API 后端）
└── README_VERCEL.md            # 本文档
```

---

## 一、本地运行（功能校验）

### 前置要求

- Node.js >= 18
- npm 或 yarn

### 步骤 1: 安装依赖

```bash
# 根目录（API 后端）
npm install

# 前端目录
cd novel_frontend && npm install && cd ..
```

### 步骤 2: 启动后端 API 服务

```bash
# 终端 1: 启动 Express API（端口 3000）
npm run dev
# 或
node api/index.js
```

启动成功后会看到：
```
🚀 墨香书阁 API 服务已启动
   本地地址: http://localhost:3000
   API 地址:   http://localhost:3000/api/
   健康检查:   http://localhost:3000/api/health/

📚 测试账号:
   普通用户: reader / 123456
   管理员:   admin / admin123
```

### 步骤 3: 启动前端开发服务器

```bash
# 终端 2: 启动 Vue 开发服务器（端口 5173）
cd novel_frontend
npm run dev
```

### 步骤 4: 功能验证清单

打开浏览器访问 `http://localhost:5173`，验证以下功能：

#### 公开页面
- [ ] 首页 - 小说推荐列表展示
- [ ] 小说列表 - 分类筛选、搜索、排序、分页
- [ ] 小说详情 - 基本信息、章节列表、评论、评分
- [ ] 阅读器 - 章节内容、上下章切换
- [ ] 搜索 - 关键词搜索小说
- [ ] 排行榜 - 按热度/更新等排行

#### 用户功能
- [ ] 登录 - 使用 reader / 123456
- [ ] 注册 - 新用户注册
- [ ] 个人中心 - 资料查看与修改
- [ ] 收藏 - 添加/取消收藏
- [ ] 阅读进度 - 自动记录与恢复
- [ ] 书签 - 添加/删除书签
- [ ] 评论 - 发表评论与评分
- [ ] 签到 - 每日签到
- [ ] 会员 - 查看套餐与状态
- [ ] 关注 - 关注/取关作者

#### 作者功能
- [ ] 作者中心 - 小说管理列表
- [ ] 创建小说 - 填写信息并提交
- [ ] 编辑小说 - 修改小说信息
- [ ] 章节管理 - 创建/编辑/发布章节
- [ ] 上传封面 - 封面上传功能

#### 管理后台
- [ ] 登录 - 使用 admin / admin123
- [ ] 仪表盘 - 统计数据展示
- [ ] 书籍管理 - 查看/审核/批量操作
- [ ] 广告管理 - CRUD 操作
- [ ] 公告管理 - 发布/置顶/撤回
- [ ] 分类管理 - 树形分类管理
- [ ] 签到管理 - 设置奖励
- [ ] 订单管理 - 充值订单查看

### API 接口测试

```bash
# 健康检查
curl http://localhost:3000/api/health/

# 小说列表
curl "http://localhost:3000/api/novels/?page=1&page_size=5"

# 用户登录
curl -X POST http://localhost:3000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"reader","password":"123456"}'

# 管理员登录
curl -X POST http://localhost:3000/api/auth/admin_login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 二、Vercel 部署

### 方式 A: 通过 Vercel CLI 部署（推荐）

#### 1. 安装 Vercel CLI

```bash
npm install -g vercel
```

#### 2. 登录 Vercel

```bash
vercel login
```

#### 3. 部署项目

```bash
# 在项目根目录执行
vercel

# 按照提示：
# - Set up and deploy? → Yes
# - Which scope? → 选择你的账号
# - Link to existing project? → No（首次）或选择已有项目
# - Project name? → moxiang-shuge
# - Directory? → ./
```

#### 4. 生产环境部署

```bash
vercel --prod
```

### 方式 B: 通过 GitHub 自动部署

#### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "feat: 添加 Vercel 一体化部署版本"
git push origin vercel-merge
```

#### 2. 在 Vercel 控制台配置

1. 打开 https://vercel.com/new
2. 选择 Import Git Repository
3. 选择你的 GitHub 仓库
4. 配置：
   - **Framework Preset**: Other
   - **Root Directory**: `./`（或保持默认）
   - **Build Command**: 空（Vercel 会自动使用 vercel.json）
   - **Output Directory**: 留空
5. 点击 Deploy

#### 3. 配置环境变量（如需要）

在 Vercel Dashboard → Settings → Environment Variables：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NODE_ENV` | `production` | 生产模式 |

### 方式 C: 自定义域名（可选）

```bash
# 添加自定义域名
vercel domains add your-domain.com

# 或在 Vercel Dashboard → Settings → Domains 中添加
```

---

## 三、Docker 部署

### 1. 构建镜像

```bash
docker build -t moxiang-shuge:latest .
```

### 2. 运行容器

```bash
# 简单运行
docker run -d -p 3000:3000 --name moxiang-shuge moxiang-shuge:latest

# 使用 Docker Compose（推荐，支持数据持久化）
docker-compose up -d
```

### 3. 验证服务

```bash
# 检查容器状态
docker ps | grep moxiang

# 查看日志
docker logs -f moxiang-shuge

# 测试 API
curl http://localhost:3000/api/health/

# 浏览器访问
# http://localhost:3000
```

### 4. 常用运维命令

```bash
# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 查看资源占用
docker stats moxiang-shuge

# 进入容器调试
docker exec -it moxiang-shuge sh
```

### 5. 数据备份（SQLite）

```bash
# 备份数据库文件
docker cp moxiang-shuge:/app/data/novel.db ./backup_$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup_xxx.db moxiang-shuge:/app/data/novel.db
docker restart moxiang-shuge
```

---

## 四、Git 工作流

### 分支策略

```
main                    ← 原版前后端分离（Vue + Django + MySQL），仅本地使用
  └── vercel-merge      ← 一体化版本（Vue + Express + SQLite），用于 Vercel/Docker 部署
```

### 常用 Git 命令

```bash
# ===== 初始化 =====

# 查看当前分支
git branch -a

# 切换到原版（本地分离版本）
git checkout main

# 切换到一体化版本
git checkout vercel-merge

# ===== 开发流程 =====

# 在 vercel-merge 分支上进行修改后
git add .
git commit -m "type: 描述"

# 推送到远程
git push origin vercel-merge
git push --set-upstream origin vercel-merge  # 首次推送

# 同步 main 分支的改动到 vercel-merge
git checkout vercel-merge
git merge main

# ===== 版本标签 =====

# 创建版本标签
git tag v1.0.0-vercel
git push origin v1.0.0-vercel

# ===== 对比差异 =====

# 查看 vercel-merge 与 main 的差异
git diff main...vercel-merge --stat

# 查看具体文件差异
git diff main...vercel-merge -- novel_frontend/src/api/index.ts

# ===== 回滚 =====

# 回退到上一个版本
git reset --soft HEAD~1

# 放弃本地修改
git checkout -- .
```

### Commit 规范

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加评分功能 API` |
| `fix` | Bug 修复 | `fix: 修复分页参数边界问题` |
| `docs` | 文档更新 | `docs: 更新部署说明` |
| `style` | 格式调整 | `style: 统一 API 返回格式` |
| `refactor` | 重构 | `refactor: 优化数据库查询` |
| `test` | 测试相关 | `test: 添加接口测试用例` |
| `chore` | 构建/工具 | `chore: 更新依赖版本` |

---

## 五、技术栈详情

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Node.js | 20 LTS | 运行时 |
| Express | 4.18.x | Web 框架 |
| sql.js | 1.10.x | SQLite 数据库（纯 JS，无需编译） |
| bcryptjs | 2.4.x | 密码哈希 |
| uuid | 9.0.x | ID 生成 |
| cors | 2.8.x | 跨域处理 |
| cookie-parser | 1.4.x | Cookie 解析 |
| @vercel/node | 3.0.x | Vercel 适配器 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.x | 前端框架 |
| Vite | 8.0.x | 构建工具 |
| Element Plus | 2.14.x | UI 组件库 |
| Pinia | 3.0.x | 状态管理 |
| Vue Router | 4.6.x | 路由管理 |
| Axios | 1.16.x | HTTP 客户端 |
| TypeScript | 6.0.x | 类型系统 |

---

## 六、注意事项

### 1. 数据持久化

- **Vercel**: Serverless 环境是无状态的，每次请求可能在不同实例。生产环境建议外接云数据库（PlanetScale、Turso 等）
- **Docker**: 使用 Docker Volume 持久化 SQLite 文件，重启不丢失数据
- **本地开发**: 数据存储在内存中，进程结束即清空

### 2. 性能优化

- Vercel Edge Network 自动 CDN 加速静态资源
- API 响应启用 gzip 压缩
- 前端代码分割和懒加载已配置

### 3. 安全建议

- 生产环境务必修改测试账号密码
- 设置强随机 SECRET_KEY
- 启用 HTTPS（Vercel 自动提供）
- 定期备份数据库

### 4. 与原版的兼容性

- API 接口路径完全一致（`/api/*`）
- 前端代码无需修改即可切换后端
- 两套代码可并行维护，通过 Git 分支隔离

---

## 七、故障排查

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| API 返回 404 | 路由未匹配 | 检查 vercel.json routes 配置 |
| CORS 错误 | 跨域配置问题 | 检查 API 的 cors 中间件 |
| 登录失败 | 密码错误或用户不存在 | 使用测试账号：reader/123456 或 admin/admin123 |
| 数据为空 | 未执行种子数据 | 运行 `npm run seed` |
| Docker 启动失败 | 端口被占用 | 修改 docker-compose.yml 端口映射 |
| Vercel 构建失败 | 依赖安装问题 | 检查 package.json 依赖版本 |

---

## 八、快速开始总结

```bash
# === 本地开发（3步启动） ===
npm install && cd novel_frontend && npm install && cd ..
node api/index.js              # 终端 1：API 服务 :3000
cd novel_frontend && npm run dev  # 终端 2：前端 :5173

# === Docker 部署（2条命令） ===
docker-compose up -d
open http://localhost:3000

# === Vercel 部署（3条命令） ===
npm i -g vercel
vercel login
vercel --prod
```
