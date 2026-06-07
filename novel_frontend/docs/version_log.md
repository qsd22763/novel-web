# 墨香书阁 版本更新日志

---

## v1.5.0 — 2026-06-06 签到系统 & 会员充值

### 新增功能

#### 一、每日签到（用户端）
- **签到入口**：个人中心侧边栏新增「每日签到」入口，跳转独立签到页面 `/user/checkin`
- **签到规则**：每日限签1次，漏签不可补签，签到获得平台虚拟币
- **签到页面** (`CheckIn.vue`)：
  - 虚拟币余额展示（大字金色）
  - 一键签到按钮（未签/已签/签到中 三态）
  - 连续签到天数统计
  - 近30天签到日历网格视图（已签金色标记、今天高亮）
  - 签到规则说明卡片
- **后端接口**：
  - `POST /api/checkin/do_checkin/` — 执行签到，返回奖励+连续天数
  - `GET /api/checkin/status/` — 签到状态（是否已签、连续天数、余额）
  - `GET /api/checkin/records/?days=30` — 签到记录列表

#### 二、充值免广告会员（用户端）
- **充值入口**：个人中心侧边栏新增「充值会员」入口，跳转独立充值页面 `/user/membership`
- **套餐方案**：
  | 套餐 | 价格 | 时长 |
  |------|------|------|
  | 月卡 | 19.9元 | 30天 |
  | 季卡 | 49.9元 | 90天 |
  | 年卡 | 168.0元 | 365天 |
- **会员权益**：全站阅读页 + 首页自动屏蔽开屏/弹窗广告
- **充值页面** (`Membership.vue`)：
  - 会员状态横幅卡（VIP/普通用户切换展示）
  - 3张套餐选择卡片（推荐/超值标签，选中高亮）
  - 支付确认弹窗 → 模拟支付 → 自动开通VIP
  - 我的订单历史列表（订单号、套餐、金额、状态、时间）
- **后端接口**：
  - `GET /api/membership/plans/` — 套餐列表
  - `GET /api/membership/my_status/` — 当前会员状态
  - `POST /api/membership/create_order/` — 创建订单并模拟支付
  - `GET /api/membership/my_orders/` — 我的订单列表

#### 三、管理后台 — 签到管理 (`CheckInManage.vue`)
- 入口：管理后台侧边栏 → 「签到管理」(`/admin/checkins`)
- **统计面板**：今日签到人数、总签到次数、独立用户数、每日奖励配置（可编辑修改）
- **筛选功能**：日期范围 + 用户名搜索
- **数据表格**：ID / 用户名 / 签到日期 / 获得虚拟币 / 签到时间
- **近7天趋势图**：纯CSS柱状图展示每日签到人数
- **后端接口**：
  - `GET /api/admin/checkins/` — 签到记录分页列表（支持日期/搜索筛选）
  - `GET /api/admin/checkins/stats/` — 签到统计数据
  - `PUT /api/admin/checkins/update_reward/` — 修改每日奖励数额

#### 四、管理后台 — 充值订单管理 (`OrderManage.vue`)
- 入口：管理后台侧边栏 → 「充值订单」(`/admin/orders`)
- **统计面板**：总订单数、已支付数、总营收金额、各套餐销量分布
- **筛选功能**：订单状态下拉 / 套餐类型下拉 / 订单号或用户名搜索
- **数据表格**：ID / 订单号 / 用户名 / 套餐类型 / 金额 / 状态标签(彩色) / 支付时间 / 到期时间 / 创建时间
- **后端接口**：
  - `GET /api/admin/orders/` — 订单分页列表（支持状态/套餐/搜索筛选）
  - `GET /api/admin/orders/stats/` — 充值统计数据

### 数据库变更

| 变更类型 | 表/字段 | 说明 |
|---------|---------|------|
| 新增字段 | `user.coins` (INTEGER, default=0) | 用户虚拟币余额 |
| 新增表 | `checkin_config` | 签到奖励全局配置（默认10币/天）|
| 新增表 | `checkin` | 用户签到记录（user + date + reward_coins，唯一约束 user+date）|
| 新增表 | `membership_order` | 充值订单（order_no + plan_type + amount + status + expire_at）|

迁移文件：`novels/migrations/0014_add_checkin_membership.py`

### 文件变更清单

#### 后端
| 文件 | 变更 |
|------|------|
| `novels/models.py` | User 新增 coins 字段；新增 CheckIn、CheckInConfig、MembershipOrder 模型 |
| `novels/user_serializers.py` | UserSerializer 增加 coins 字段；新增 CheckInSerializer、MembershipOrderSerializer |
| `novels/checkin_views.py` | **新建** — CheckInViewSet（签到/状态/记录）、MembershipViewSet（套餐/状态/下单/订单）|
| `novels/admin_views.py` | 新增 AdminCheckInViewSet（签到管理+统计+改奖励）、AdminMembershipOrderViewSet（订单管理+统计）|
| `novels/urls.py` | 注册 4 个新路由：checkin、membership、admin/checkins、admin/orders |

#### 前端
| 文件 | 变更 |
|------|------|
| `src/api/index.ts` | 新增 checkinApi、membershipApi、adminApi.checkin、adminApi.order |
| `src/router/index.ts` | 新增 4 个路由：/user/checkin、/user/membership、/admin/checkins、/admin/orders |
| `src/views/UserCenter.vue` | 侧边栏新增「每日签到」「充值会员」两个外部链接入口 |
| `src/views/CheckIn.vue` | **新建** — 用户签到页面 |
| `src/views/Membership.vue` | **新建** — 用户充值会员页面 |
| `src/views/admin/AdminLayout.vue` | 侧边栏菜单新增「签到管理」「充值订单」两项 |
| `src/views/admin/CheckInManage.vue` | **新建** — 管理后台签到管理页面 |
| `src/views/admin/OrderManage.vue` | **新建** — 管理后台充值订单管理页面 |

---

## v1.4.0 — 2026-06-06 数据导入 & 分页修复

### 修复
- 书籍管理分页硬编码 limit 17 → 标准分页（offset/pageSize 动态计算），81本书正常分页浏览
- 导出 Excel 接口 undefined 参数过滤 + 后端参数兼容
- 收藏删除接口 novel_id 字段名匹配修复
- 个人中心用户名动态渲染（real_name > pen_name > username）
- 管理后台个人信息点击跳转修复

### 新增
- 批量导入 64 本小说数据（种子22 + 热门42），绑定 5 张本地封面
- 书籍管理 Excel 导出功能（按筛选条件导出 9 个字段）

---

## v1.3.0 — 2026-06-05 审核流程 & 权限修复

### 修复
- React #185 报错：audit_status default=2→1（新书默认待审核）
- author_views perform_create 显式设置 audit_status=1
- ReviewList 统计拼写错误 stats.approvedRes → stats.approved
- 用户中心收藏/阅读进度/书签接口 AdminUser 类型兼容（返回空集不报500）

### 新增
- 管理后台「新书审核」模块（ReviewList.vue）：审核通过/驳回、状态筛选、预览弹窗
