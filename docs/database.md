# 免费小说网站数据库设计文档

## 一、数据库概述

### 1.1 数据库选型
- **开发环境**：SQLite（轻量级、免配置）
- **生产环境**：MySQL 5.7+（成熟稳定、支持全文检索）

### 1.2 命名规范
| 规范 | 示例 |
|------|------|
| 库名 | novel_reader |
| 表名单数 | novel, chapter |
| 字段全小写下划线 | novel_title, created_at |
| 索引名 | idx_novel_category |

---

## 二、数据库模型

### 2.1 ER图
```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   User   │       │  Novel   │       │ Chapter  │
├──────────┤       ├──────────┤       ├──────────┤
│ id       │◀──┐   │ id       │◀──────│ id       │
│ username │   │   │ title    │       │ novel_id │
│ password │   │   │ author   │       │ title    │
│ email    │   └───│ author_id│       │ content  │
│ created  │       │ status   │       │ order    │
└──────────┘       └──────────┘       └──────────┘
       │                                   │
       │           ┌──────────┐           │
       └──────────▶│ Favorite │◀──────────┘
                   ├──────────┤
                   │ id       │
                   │ user_id  │
                   │ novel_id │
                   │ created  │
                   └──────────┘
```

---

## 三、表结构设计

### 3.1 小说表 (novel)
```sql
CREATE TABLE novel (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '小说ID',
    title           VARCHAR(100) NOT NULL COMMENT '书名',
    author          VARCHAR(50) NOT NULL COMMENT '作者',
    cover           VARCHAR(255) DEFAULT '' COMMENT '封面URL',
    description     TEXT COMMENT '简介',
    category        VARCHAR(20) NOT NULL COMMENT '分类',
    status          TINYINT DEFAULT 0 COMMENT '状态(0连载/1完结)',
    word_count      INT DEFAULT 0 COMMENT '总字数',
    view_count      INT DEFAULT 0 COMMENT '阅读量',
    recommend       INT DEFAULT 0 COMMENT '推荐票',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (category),
    INDEX idx_author (author),
    FULLTEXT idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说表';
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| title | VARCHAR(100) | 书名，最多100字符 |
| author | VARCHAR(50) | 作者名 |
| cover | VARCHAR(255) | 封面图片URL |
| description | TEXT | 小说简介 |
| category | VARCHAR(20) | 分类：玄幻、都市、穿越等 |
| status | TINYINT | 0-连载中，1-已完结 |
| word_count | INT | 总字数 |
| view_count | INT | 阅读次数 |
| recommend | INT | 推荐票数 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 最后更新时间 |

### 3.2 章节表 (chapter)
```sql
CREATE TABLE chapter (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '章节ID',
    novel_id        INT NOT NULL COMMENT '所属小说ID',
    title           VARCHAR(100) NOT NULL COMMENT '章节标题',
    content         LONGTEXT COMMENT '章节内容',
    chapter_order   INT NOT NULL COMMENT '章节序号',
    word_count      INT DEFAULT 0 COMMENT '章节字数',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_novel_id (novel_id),
    INDEX idx_novel_order (novel_id, chapter_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='章节表';
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| novel_id | INT | 关联小说ID |
| title | VARCHAR(100) | 章节标题 |
| content | LONGTEXT | 章节正文 |
| chapter_order | INT | 章节序号（用于排序） |
| word_count | INT | 本章字数 |
| created_at | DATETIME | 创建时间 |

### 3.3 用户表 (user)
```sql
CREATE TABLE user (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username        VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password        VARCHAR(32) NOT NULL COMMENT '密码(MD5)',
    email           VARCHAR(100) DEFAULT '' COMMENT '邮箱',
    avatar          VARCHAR(255) DEFAULT '' COMMENT '头像URL',
    status          TINYINT DEFAULT 1 COMMENT '状态(0禁用/1正常)',
    last_login      DATETIME DEFAULT NULL COMMENT '最后登录时间',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| username | VARCHAR(50) | 用户名，唯一 |
| password | VARCHAR(32) | 密码（MD5加密） |
| email | VARCHAR(100) | 邮箱 |
| avatar | VARCHAR(255) | 头像URL |
| status | TINYINT | 0-禁用，1-正常 |
| last_login | DATETIME | 最后登录时间 |
| created_at | DATETIME | 注册时间 |

### 3.4 收藏表 (favorite)
```sql
CREATE TABLE favorite (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏ID',
    user_id         INT NOT NULL COMMENT '用户ID',
    novel_id        INT NOT NULL COMMENT '小说ID',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    UNIQUE KEY uk_user_novel (user_id, novel_id),
    INDEX idx_user_id (user_id),
    INDEX idx_novel_id (novel_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID |
| novel_id | INT | 小说ID |
| created_at | DATETIME | 收藏时间 |

**唯一约束**：(user_id, novel_id) 防止重复收藏

### 3.5 阅读记录表 (read_record)
```sql
CREATE TABLE read_record (
    id              INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id         INT NOT NULL COMMENT '用户ID',
    novel_id        INT NOT NULL COMMENT '小说ID',
    chapter_id      INT NOT NULL COMMENT '阅读章节ID',
    read_progress   INT DEFAULT 0 COMMENT '阅读进度(百分比)',
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_user_novel (user_id, novel_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='阅读记录表';
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| user_id | INT | 用户ID |
| novel_id | INT | 小说ID |
| chapter_id | INT | 最后阅读的章节ID |
| read_progress | INT | 阅读进度百分比 |
| updated_at | DATETIME | 最后更新时间 |

---

## 四、索引设计

### 4.1 索引汇总
| 表名 | 索引名 | 字段 | 类型 | 用途 |
|------|--------|------|------|------|
| novel | idx_category | category | 普通 | 分类筛选 |
| novel | idx_author | author | 普通 | 作者搜索 |
| novel | idx_title | title | 全文 | 标题搜索 |
| chapter | idx_novel_id | novel_id | 普通 | 关联查询 |
| chapter | idx_novel_order | novel_id, order | 复合 | 章节排序 |
| user | idx_username | username | 普通 | 用户登录 |
| favorite | idx_user_id | user_id | 普通 | 用户收藏 |
| favorite | idx_novel_id | novel_id | 普通 | 小说收藏数 |
| read_record | idx_user_id | user_id | 普通 | 阅读历史 |

---

## 五、数据字典

### 5.1 小说分类 (category)
| 分类 | 代码 | 说明 |
|------|------|------|
| 玄幻 | xuanhuan | 东方玄幻、异世大陆 |
| 都市 | dushi | 都市生活、恩怨情仇 |
| 穿越 | chuanyue | 穿越时空、历史架空 |
| 科幻 | kehuan | 星际文明、未来世界 |
| 游戏 | youxi | 游戏世界、电子竞技 |
| 悬疑 | xuanyi | 推理悬疑、恐怖灵异 |

### 5.2 小说状态 (status)
| 状态码 | 名称 | 说明 |
|--------|------|------|
| 0 | 连载中 | 正在更新 |
| 1 | 已完结 | 已完本 |

---

## 六、初始化数据

### 6.1 小说分类数据
```sql
INSERT INTO category (name, code) VALUES
('玄幻', 'xuanhuan'),
('都市', 'dushi'),
('穿越', 'chuanyue'),
('科幻', 'kehuan'),
('游戏', 'youxi'),
('悬疑', 'xuanyi');
```

---

## 七、数据库维护

### 7.1 备份策略
| 类型 | 周期 | 保留时间 |
|------|------|----------|
| 全量备份 | 每日 | 7天 |
| 增量备份 | 每小时 | 24小时 |

### 7.2 清理策略
| 数据 | 清理规则 |
|------|----------|
| 日志 | 30天 |
| 缓存 | TTL过期 |
| 无效会话 | 7天未活跃 |
