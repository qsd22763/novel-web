# 墨香书阁 - 后台管理系统开发计划

## 项目概述
为墨香书阁小说阅读平台开发后台管理系统，包含 **广告管理**、**公告管理**、**书籍管理** 三大核心模块。

## 技术栈
| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Element Plus + Pinia |
| 后端 | Django DRF + MySQL |
| 样式 | 深色主题管理后台，Element Plus 组件库 |
| 代理 | Vite proxy → Django 8000 |

## 现有架构
- 前端路由在 `novel_frontend/src/router/index.ts`
- API 在 `novel_frontend/src/api/index.ts`
- 后端 URL 在 `novel_backend/novels/urls.py`
- 模型在 `novel_backend/novels/models.py`
- 数据库名: `novel_fiction`, 密码: `200486qq.`

---

## Phase 1: 后端 - 数据模型与API
### 1.1 广告模型 (Advertisement)
- 字段: title, ad_type(横幅/弹窗/侧边栏), image_url, link_url, position(位置), is_active, start_time, end_time, click_count, view_count, sort_order, created_at
- API: CRUD + 批量操作 + 启用/禁用

### 1.2 公告模型 (Announcement)  
- 字段: title, content, announcement_type(通知/维护/活动), is_pinned, is_active, created_at
- API: CRUD + 置顶 + 发布/撤回

### 1.3 书籍管理增强
- 复用现有Novel模型，增加管理员专用API
- 批量审核、批量分类修改、批量下架

### 1.4 权限控制
- AdminViewSet基类（需要is_staff权限）
- JWT/Session认证复用现有auth系统

**状态**: pending
---

## Phase 2: 前端 - Admin布局框架
### 2.1 Admin Layout
- 侧边栏导航 (折叠/展开)
- 顶部栏 (面包屑/用户信息/退出)
- 深色主题配色方案
- 响应式适配

### 2.2 路由配置
- /admin → Dashboard仪表盘
- /admin/advertisements → 广告管理
- /admin/announcements → 公告管理
- /admin/books → 书籍管理
- 路由守卫 (requiresAdmin)

**状态**: pending

---

## Phase 3: 前端 - Dashboard仪表盘
### 3.1 统计卡片
- 总书籍数、总用户数、今日阅读量、今日新增评论
- 趋势对比 (日环比)

### 3.2 图表区域
- 近7天阅读趋势折线图
- 分类占比饼图
- 热门书籍排行TOP10

### 3.3 最近动态
- 最新注册用户、最新评论、待审核内容

**状态**: pending

---

## Phase 4: 前端 - 广告管理模块
### 4.1 广告列表页
- 表格展示 (缩略图/标题/类型/位置/状态/曝光/点击/操作)
- 筛选 (类型/位置/状态)
- 排序/分页
- 批量操作 (启用/禁用/删除)

### 4.2 广告编辑
- 表单对话框 (创建/编辑)
- 图片上传预览
- 时间范围选择器
- 位置预览示意

**状态**: pending

---

## Phase 5: 前端 - 公告管理模块
### 5.1 公告列表页
- 表格展示 (标题/类型/置顶/状态/时间/操作)
- 筛选 (类型/状态)
- 拖拽排序置顶

### 5.2 公告编辑
- 富文本编辑器 (或Markdown)
- 类型选择
- 置顶开关
- 预览功能

**状态**: pending

---

## Phase 6: 前端 - 书籍管理模块
### 6.1 书籍列表页
- 高级表格 (封面/书名/作者/分类/字数/阅读量/状态/审核状态/操作)
- 多维筛选 (分类/状态/审核状态/字数范围)
- 搜索 (书名/作者)
- 批量操作 (审核通过/驳回/下架/改分类)

### 6.2 书籍详情/编辑
- 完整表单 (基本信息/封面上传/分类标签)
- 章节管理子页面
- 数据统计面板

**状态**: pending

---

## Phase 7: 集成测试与优化
### 7.1 功能联调
- 前后端接口对接
- 错误处理完善
- Loading状态优化

### 7.2 UI打磨
- 动画过渡效果
- 响应式细节调整
- 暗色模式完整适配

**状态**: pending

---

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| (待记录) | | |
