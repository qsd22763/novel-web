# 免费小说网站接口定义文档

## 一、接口规范

### 1.1 基本规范
| 项目 | 规范 |
|------|------|
| 协议 | HTTP/HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 认证方式 | Session (可选Token) |

### 1.2 请求规范
```javascript
// 请求头
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}

// 分页参数
{
  "page": 1,       // 页码，默认1
  "page_size": 20  // 每页数量，默认20
}
```

### 1.3 响应规范
```javascript
// 成功响应
{
  "code": 200,
  "message": "success",
  "data": { ... }
}

// 分页响应
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 100,      // 总数
    "page": 1,         // 当前页
    "page_size": 20,   // 每页数量
    "results": [ ... ] // 数据列表
  }
}

// 错误响应
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 1.4 状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 二、小说接口

### 2.1 小说列表
```
GET /api/novels/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 分类筛选 |
| status | int | 否 | 状态筛选 |
| ordering | string | 否 | 排序字段：-updated_at,-view_count,-created_at |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 100,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "title": "斗破苍穹",
        "author": "天蚕土豆",
        "cover": "/media/covers/1.jpg",
        "category": "玄幻",
        "status": 1,
        "word_count": 500000,
        "view_count": 1000000,
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 2.2 小说详情
```
GET /api/novels/{id}/
```

**路径参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 小说ID |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "斗破苍穹",
    "author": "天蚕土豆",
    "cover": "/media/covers/1.jpg",
    "description": "这里是小说简介...",
    "category": "玄幻",
    "status": 1,
    "word_count": 500000,
    "view_count": 1000000,
    "chapter_count": 1500,
    "created_at": "2020-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2.3 小说章节列表
```
GET /api/novels/{id}/chapters/
```

**路径参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 小说ID |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "novel_id": 1,
    "novel_title": "斗破苍穹",
    "chapter_count": 1500,
    "chapters": [
      {
        "id": 1001,
        "title": "第一章 陨落的天才",
        "chapter_order": 1,
        "word_count": 3000,
        "created_at": "2020-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 2.4 小说搜索
```
GET /api/novels/search/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 搜索关键词 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 50,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "title": "斗破苍穹",
        "author": "天蚕土豆",
        "cover": "/media/covers/1.jpg",
        "category": "玄幻"
      }
    ]
  }
}
```

### 2.5 小说推荐/排行榜
```
GET /api/novels/recommend/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 类型：hot(热门)/new(新作)/rank(排行) |
| limit | int | 否 | 返回数量，默认10 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "斗破苍穹",
      "author": "天蚕土豆",
      "cover": "/media/covers/1.jpg",
      "view_count": 1000000
    }
  ]
}
```

---

## 三、章节接口

### 3.1 章节内容
```
GET /api/chapters/{id}/
```

**路径参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 章节ID |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1001,
    "novel_id": 1,
    "novel_title": "斗破苍穹",
    "title": "第一章 陨落的天才",
    "content": "这里是章节正文...",
    "chapter_order": 1,
    "word_count": 3000,
    "prev_chapter": null,
    "next_chapter": {
      "id": 1002,
      "title": "第二章 筑基丹"
    }
  }
}
```

---

## 四、用户接口

### 4.1 用户注册
```
POST /api/auth/register/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名(6-20位) |
| password | string | 是 | 密码(6-20位) |
| email | string | 否 | 邮箱 |

**请求示例**
```json
{
  "username": "reader001",
  "password": "password123",
  "email": "reader@example.com"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "reader001"
  }
}
```

### 4.2 用户登录
```
POST /api/auth/login/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应示例**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "id": 1,
    "username": "reader001",
    "token": "abc123..."
  }
}
```

### 4.3 用户登出
```
POST /api/auth/logout/
```

**响应示例**
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 4.4 获取用户信息
```
GET /api/user/profile/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "reader001",
    "email": "reader@example.com",
    "avatar": "/media/avatars/1.jpg",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

---

## 五、收藏接口

### 5.1 添加收藏
```
POST /api/user/favorites/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| novel_id | int | 是 | 小说ID |

**请求示例**
```json
{
  "novel_id": 1
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "收藏成功",
  "data": {
    "id": 1,
    "novel_id": 1,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 5.2 取消收藏
```
DELETE /api/user/favorites/{novel_id}/
```

**路径参数**
| 参数 | 类型 | 说明 |
|------|------|------|
| novel_id | int | 小说ID |

**响应示例**
```json
{
  "code": 200,
  "message": "取消收藏成功",
  "data": null
}
```

### 5.3 收藏列表
```
GET /api/user/favorites/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 10,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "novel": {
          "id": 1,
          "title": "斗破苍穹",
          "author": "天蚕土豆",
          "cover": "/media/covers/1.jpg",
          "category": "玄幻"
        },
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

## 六、阅读记录接口

### 6.1 更新阅读记录
```
POST /api/user/read-progress/
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| novel_id | int | 是 | 小说ID |
| chapter_id | int | 是 | 章节ID |
| progress | int | 否 | 阅读进度(0-100) |

**请求示例**
```json
{
  "novel_id": 1,
  "chapter_id": 1001,
  "progress": 50
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 6.2 获取阅读记录
```
GET /api/user/read-progress/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 5,
    "results": [
      {
        "novel_id": 1,
        "novel_title": "斗破苍穹",
        "chapter_id": 1001,
        "chapter_title": "第一章 陨落的天才",
        "progress": 50,
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

---

## 七、分类接口

### 7.1 分类列表
```
GET /api/categories/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {"id": 1, "name": "玄幻", "code": "xuanhuan", "count": 200},
    {"id": 2, "name": "都市", "code": "dushi", "count": 150},
    {"id": 3, "name": "穿越", "code": "chuanyue", "count": 100}
  ]
}
```

---

## 八、公共接口

### 8.1 热门搜索词
```
GET /api/hot-search/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "斗破苍穹",
    "完美世界",
    "全职高手",
    "庆余年",
    "凡人修仙传"
  ]
}
```

### 8.2 首页数据
```
GET /api/home/
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "recommend": [...],
    "hot": [...],
    "new": [...],
    "categories": [...]
  }
}
```
