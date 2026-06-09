# 墨香书阁 - 部署指南 (MySQL 版)

## 一、服务器购买（阿里云香港，免备案）

| 配置 | 推荐值 | 价格 |
|------|--------|------|
| 地域 | **中国香港** | - |
| 实例 | 轻量应用服务器 | - |
| 镜像 | **Ubuntu 22.04** (预装 MySQL 更方便) | - |
| 规格 | 2核2G | ~39元/月 |
| 带宽 | 200M峰值 | 含在套餐中 |

> [阿里云轻量服务器购买入口](https://www.aliyun.com/product/swas)

## 二、域名注册（万网）

1. 打开 [wanwang.aliyun.com](https://wanwang.aliyun.com/)
2. 搜索并注册域名（推荐 `.com`）
3. 进入「云解析 DNS」→ 添加 A 记录：
   - 主机记录: `@` → 记录值: `你的服务器IP`
   - 主机记录: `www` → 记录值: `你的服务器IP`

## 三、一键部署

### SSH 连接服务器后执行：

```bash
# 1. 克隆项目
git clone https://github.com/qsd22763/novel-web.git /www/temp_repo

# 2. 编辑部署脚本，设置你的域名
nano /www/temp_repo/deploy/deploy.sh
# 把 DOMAIN="your-domain.com" 改为实际域名
# 如果知道 MySQL root 密码，设置 MYSQL_ROOT_PASS="xxx"（可选）

# 3. 运行部署脚本（自动安装 MySQL + 创建数据库 + 全部配置）
cd /www && bash temp_repo/deploy/deploy.sh

# 4. 设置 Django 密钥和域名
nano /www/novel_backend/.env
# SECRET_KEY 改为随机字符串: python3 -c "import secrets; print(secrets.token_urlsafe(50))"
# ALLOWED_HOSTS 改为: 你的域名.com,www.你的域名.com

# 5. 重启服务使 .env 生效
systemctl restart novel-web

# 6. 创建后台管理员账号
cd /www/novel_backend && source venv/bin/activate && python manage.py createsuperuser
```

### 手动分步操作（如果脚本有问题）：

```bash
# ===== 1. 系统依赖（含 MySQL） =====
apt update && apt install -y nginx python3.8 python3.8-venv git \
    build-essential libmysqlclient-dev curl default-mysql-server nodejs npm

# ===== 2. 创建 MySQL 数据库 =====
mysql -u root <<'SQL'
CREATE DATABASE IF NOT EXISTS novel_fiction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'novel_user'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON novel_fiction.* TO 'novel_user'@'localhost';
FLUSH PRIVILEGES;
SQL

# ===== 3. 后端 =====
cd /www/novel_backend
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt        # 包含 mysqlclient
cp .env.example .env                   # 编辑 .env 填入数据库密码
python manage.py migrate               # 在 MySQL 中建表
python manage.py collectstatic --noinput --clear

# ===== 4. 前端 =====
cd /www/novel_frontend
npm install && npm run build

# ===== 5. Nginx =====
cp deploy/nginx.conf /etc/nginx/sites-available/novel-web.conf
sed -i 's/your-domain.com/你的域名/g' /etc/nginx/sites-available/novel-web.conf
ln -sf /etc/nginx/sites-available/novel-web.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ===== 6. 启动 Gunicorn 服务 =====
chown -R www-data:www-data /www
cp deploy/gunicorn_config.py /www/novel_backend/
cp deploy/novel-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable novel-web
systemctl start novel-web
```

## 四、验证部署

```bash
systemctl status novel-web      # Django/Gunicorn 状态
systemctl status nginx          # Nginx 状态
curl http://127.0.0.1:8000/api/novels/   # 测试 API
journalctl -u novel-web -f      # 实时日志
```

浏览器访问：`http://你的域名`

## 五、SSL 证书（HTTPS）

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 你的域名.com -d www.你的域名.com
certbot renew --dry-run         # 测试自动续期
```

## 六、常用运维命令

| 操作 | 命令 |
|------|------|
| 重启后端 | `systemctl restart novel-web` |
| 重启 Nginx | `systemctl reload nginx` |
| 更新代码+重新部署 | `cd /www/novel_backend && git pull && cd ../novel_frontend && git pull && cd ../deploy && bash deploy.sh` |
| 查看 MySQL | `mysql -u novel_user -p novel_fiction` |
| 数据库备份 | `mysqldump -u novel_user -p novel_fiction > backup_$(date +%Y%m%d).sql` |
| 数据库恢复 | `mysql -u novel_user -p novel_fiction < backup_xxx.sql` |
| Django Shell | `cd /www/novel_backend && source venv/bin/activate && python manage.py shell` |
| 错误日志 | `tail -100 /var/log/novel/gunicorn_error.log` |

## 架构图

```
用户浏览器
    │
    ▼
┌──────────────┐  :80/:443
│    Nginx     │
├──────┬───────┤
│静态文件│API代理│
│(dist/)│      │
└───┬───┴──┬───┘
    │       │
    │ 127.0.0.1:8000
    ▼
┌──────────────┐
│  Gunicorn    │ × 2 workers
│  + Django    │
│  + MySQL     │ ← localhost:3306
└──────────────┘
```

## .env 配置说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | Django 密钥（必改） | 随机50字符字符串 |
| `DEBUG` | 调试模式 | 生产环境设为 False |
| `ALLOWED_HOSTS` | 允许的域名 | `moxiangge.com,www.moxiangge.com` |
| `DB_NAME` | 数据库名 | `novel_fiction` |
| `DB_USER` | 数据库用户 | `novel_user` |
| `DB_PASSWORD` | 数据库密码 | 部署时自动生成或手动设置 |
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `3306` |
