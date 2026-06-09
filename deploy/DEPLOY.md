# 墨香书阁 - 部署指南

## 一、服务器购买（阿里云香港，免备案）

| 配置 | 推荐值 | 价格 |
|------|--------|------|
| 地域 | **中国香港** | - |
| 实例 | 轻量应用服务器 | - |
| 镜像 | **Ubuntu 22.04** | - |
| 规格 | 2核2G | ~39元/月 |
| 带宽 | 200M峰值 | 含在套餐内 |
| 系统盘 | ESSD 40GB | 含在套餐内 |

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

# 2. 运行部署脚本
cd /www && bash temp_repo/deploy/deploy.sh

# 3. 修改域名和密钥
nano /www/novel_backend/.env
# 把 your-domain.com 改为实际域名
# SECRET_KEY 改为随机字符串: python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# 4. 重新部署（改完 .env 后）
bash /www/deploy/deploy.sh
```

### 手动分步操作（如果脚本有问题）：

```bash
# ===== 1. 系统依赖 =====
apt update && apt install -y nginx python3.8 python3.8-venv git curl build-essential nodejs npm

# ===== 2. 后端 =====
cd /www/novel_backend
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # 编辑 .env 设置域名和密钥
python manage.py migrate
python manage.py collectstatic --noinput --clear

# ===== 3. 前端 =====
cd /www/novel_frontend
npm install && npm run build

# ===== 4. Nginx =====
cp deploy/nginx.conf /etc/nginx/sites-available/novel-web.conf
# 编辑 nginx.conf 把 your-domain.com 改为实际域名
sed -i 's/your-domain.com/你的域名/g' /etc/nginx/sites-available/novel-web.conf
ln -sf /etc/nginx/sites-available/novel-web.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ===== 5. 启动服务 =====
chown -R www-data:www-data /www
cp deploy/gunicorn_config.py /www/novel_backend/
cp deploy/novel-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable novel-web
systemctl start novel-web
```

## 四、验证部署

```bash
# 检查各组件状态
systemctl status novel-web      # Django/Gunicorn 状态
systemctl status nginx          # Nginx 状态

# 测试 API
curl http://127.0.0.1:8000/api/novels/

# 查看日志
journalctl -u novel-web -f      # 实时日志
tail -f /var/log/novel/gunicorn_error.log
```

浏览器访问：`http://你的域名`

## 五、SSL 证书（HTTPS，可选）

```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 自动申请证书并配置 Nginx
certbot --nginx -d 你的域名.com -d www.你的域名.com

# 自动续期（已自动配置 cron）
certbot renew --dry-run
```

## 六、常用运维命令

| 操作 | 命令 |
|------|------|
| 重启后端 | `systemctl restart novel-web` |
| 重启 Nginx | `systemctl reload nginx` |
| 更新代码+重新部署 | `cd /www/novel_backend && git pull && cd ../novel_frontend && git pull && cd ../deploy && bash deploy.sh` |
| 查看错误日志 | `tail -100 /var/log/novel/gunicorn_error.log` |
| Django Shell | `cd /www/novel_backend && source venv/bin/activate && python manage.py shell` |
| 创建管理员 | `python manage.py createsuperuser` |

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
│  + SQLite    │
└──────────────┘
```
