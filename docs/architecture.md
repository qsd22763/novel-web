# 免费小说网站技术架构文档

## 一、架构概述

### 1.1 架构风格
采用**前后端分离**架构，前端负责页面展示和用户交互，后端负责业务逻辑和数据处理。

### 1.2 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CDN / Nginx                           │
│                    (静态资源 + 反向代理)                      │
└─────────────────────────────────────────────────────────────┘
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐     ┌───────────────────┐
        │    前端Vue3       │     │   后端Django       │
        │   (localhost)    │────▶│   (localhost)      │
        │   :5173          │◀────│   :8000            │
        └───────────────────┘     └───────────────────┘
                                          │
                                          ▼
                                ┌───────────────────┐
                                │      MySQL        │
                                │    :3306          │
                                └───────────────────┘
                                          │
                                          ▼
                                ┌───────────────────┐
                                │      Redis        │
                                │    :6379          │
                                └───────────────────┘
```

---

## 二、技术栈选型

### 2.1 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue3 | 3.4+ | 核心框架 |
| Vite | 5.0+ | 构建工具 |
| TypeScript | 5.0+ | 类型检查 |
| Vue Router | 4.0+ | 路由管理 |
| Pinia | 2.0+ | 状态管理 |
| Element Plus | 2.5+ | UI组件库 |
| Axios | 1.6+ | HTTP客户端 |
| Less | 4.0+ | CSS预处理器 |

### 2.2 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| Django | 4.2+ | Web框架 |
| Django REST Framework | 3.14+ | REST API |
| MySQLclient | 2.1+ | MySQL驱动 |
| PyMySQL | 1.1+ | MySQL驱动备选 |
| Redis | 4.0+ | 缓存 |
| Gunicorn | 21.0+ | WSGI服务器 |

### 2.3 开发工具
| 工具 | 用途 |
|------|------|
| VSCode | 代码编辑器 |
| Git | 版本控制 |
| Navicat | 数据库管理 |
| Postman | API测试 |

---

## 三、前端架构

### 3.1 项目结构
```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口
│   │   └── index.js       # 接口定义
│   ├── assets/            # 资源文件
│   │   └── images/        # 图片
│   ├── components/        # 公共组件
│   │   ├── Header.vue
│   │   ├── Footer.vue
│   │   └── NovelCard.vue
│   ├── router/            # 路由配置
│   │   └── index.ts
│   ├── stores/            # 状态管理
│   │   └── user.ts
│   ├── utils/             # 工具函数
│   │   └── request.ts    # Axios封装
│   ├── views/             # 页面组件
│   │   ├── Home.vue
│   │   ├── NovelList.vue
│   │   ├── NovelDetail.vue
│   │   ├── Reader.vue
│   │   └── Search.vue
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 3.2 路由设计
| 路径 | 组件 | 说明 |
|------|------|------|
| / | Home | 首页 |
| /novels | NovelList | 小说列表 |
| /novels/:id | NovelDetail | 小说详情 |
| /novels/:id/read/:chapterId | Reader | 阅读器 |
| /search | Search | 搜索页 |
| /login | Login | 登录页 |
| /register | Register | 注册页 |
| /user/favorites | Favorites | 收藏页 |

### 3.3 状态管理
采用Pinia进行状态管理，主要状态：
| Store | 用途 |
|-------|------|
| userStore | 用户信息、登录状态 |
| novelStore | 小说缓存 |
| readStore | 阅读进度 |

---

## 四、后端架构

### 4.1 项目结构
```
backend/
├── project/               # 项目配置
│   ├── __init__.py
│   ├── settings.py        # 配置文件
│   ├── urls.py            # 根路由
│   └── wsgi.py            # WSGI入口
├── app/                   # 主应用
│   ├── __init__.py
│   ├── admin.py           # 管理后台
│   ├── apps.py            # 应用配置
│   ├── models.py          # 数据模型
│   ├── serializers.py     # 序列化器
│   ├── urls.py            # 路由
│   └── views.py           # 视图
├── manage.py              # 管理脚本
└── requirements.txt      # 依赖
```

### 4.2 应用模块
| 模块 | 用途 |
|------|------|
| app.novels | 小说管理 |
| app.chapters | 章节管理 |
| app.users | 用户管理 |
| app.favorites | 收藏管理 |

### 4.3 中间件
| 中间件 | 用途 |
|--------|------|
| SessionMiddleware | 会话管理 |
| CommonMiddleware | 通用处理 |
| CORS | 跨域处理 |

---

## 五、部署架构

### 5.1 开发环境
| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| MySQL | localhost:3306 |
| Redis | localhost:6379 |

### 5.2 生产环境
| 服务 | 配置 |
|------|------|
| Nginx | 静态文件托管、反向代理 |
| Gunicorn | WSGI服务器 |
| MySQL | 云数据库 |
| Redis | 云缓存 |

### 5.3 部署流程
```
1. 前端构建 → npm run build
2. 后端部署 → gunicorn project.wsgi
3. Nginx配置 → 静态文件 + 代理
4. 域名解析 → DNS配置
```

---

## 六、安全架构

### 6.1 安全措施
| 措施 | 说明 |
|------|------|
| CORS | 限制跨域访问 |
| CSRF | 防跨站请求伪造 |
| SQL注入 | ORM自动防护 |
| XSS | 转义用户输入 |
| 密码加密 | MD5存储 |

### 6.2 接口安全
| 措施 | 说明 |
|------|------|
| 限流 | 防止恶意请求 |
| 认证 | Token验证（可选） |
| 日志 | 记录访问日志 |

---

## 七、性能优化

### 7.1 前端优化
| 优化点 | 方案 |
|--------|------|
| 代码分割 | 路由懒加载 |
| 图片懒加载 | IntersectionObserver |
| 缓存 | 组件缓存、接口缓存 |
| 打包优化 | Tree Shaking、压缩 |

### 7.2 后端优化
| 优化点 | 方案 |
|--------|------|
| 数据库索引 | 关键字段加索引 |
| 查询优化 | select_related、prefetch_related |
| 缓存 | Redis缓存热点数据 |
| 分页 | 大数据量分页 |

---

## 八、监控与运维

### 8.1 监控指标
| 类型 | 指标 |
|------|------|
| 可用性 | 接口成功率 |
| 性能 | 响应时间 |
| 业务 | UV、PV |

### 8.2 备份策略
| 类型 | 周期 |
|------|------|
| 数据库 | 每日全量 |
| 代码 | Git仓库 |
| 日志 | 定期清理 |
