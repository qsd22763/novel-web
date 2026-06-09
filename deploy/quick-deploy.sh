# ============================================================
#   墨香书阁 - 华为云服务器一键部署命令
#   服务器 IP: 121.37.169.132
#   系统: Ubuntu (华为云默认)
#   数据库: MySQL
#   复制以下全部命令，粘贴到服务器终端执行
# ============================================================

# ===== 第1步：安装基础依赖 =====
apt-get update && apt-get install -y nginx python3 python3-venv python3-pip git build-essential libmysqlclient-dev curl default-mysql-server nodejs npm

# ===== 第2步：安装 MySQL 并创建数据库 =====
service mysql start || systemctl start mysql
mysql -u root <<'SQL'
CREATE DATABASE IF NOT EXISTS novel_fiction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'novel_user'@'localhost' IDENTIFIED BY 'Mxsg2024Secure!';
GRANT ALL PRIVILEGES ON novel_fiction.* TO 'novel_user'@'localhost';
FLUSH PRIVILEGES;
SQL

# ===== 第3步：克隆项目代码 =====
mkdir -p /www
cd /www
git clone https://github.com/qsd22763/novel-web.git temp_repo
mv temp_repo/novel_backend .
mv temp_repo/novel_frontend .
cp -r temp_repo/deploy . 2>/dev/null || mkdir -p deploy
rm -rf temp_repo

# ===== 第4步：Python 环境 + 后端依赖 =====
cd /www/novel_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# ===== 第5步：配置 Django .env =====
cat > .env <<'EOF'
SECRET_KEY=mxsg-production-2024-key-change-in-prod-$(openssl rand -hex 24)
DEBUG=False
ALLOWED_HOSTS=121.37.169.132,localhost,127.0.0.1
DB_ENGINE=django.db.backends.mysql
DB_NAME=novel_fiction
DB_USER=novel_user
DB_PASSWORD=Mxsg2024Secure!
DB_HOST=localhost
DB_PORT=3306
EOF

# ===== 第6步：数据库迁移 + 收集静态文件 =====
python manage.py migrate
python manage.py collectstatic --noinput --clear

# ===== 第7步：构建前端 =====
cd /www/novel_frontend
npm install && npm run build

# ===== 第8步：配置 Nginx =====
sed 's|your-domain.com|121.37.169.132|g' /www/deploy/nginx.conf > /etc/nginx/sites-available/novel-web.conf
ln -sf /etc/nginx/sites-available/novel-web.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ===== 第9步：配置 Gunicorn + Systemd 服务 =====
cp /www/deploy/gunicorn_config.py /www/novel_backend/
cp /www/deploy/novel-web.service /etc/systemd/system/
chown -R www-data:www-data /www
chmod -R 755 /www
systemctl daemon-reload
systemctl enable novel-web
systemctl start novel-web

# ===== 第10步：创建管理员账号 =====
cd /www/novel_backend && source venv/bin/activate && echo "=== 创建后台管理员 ===" && python manage.py createsuperuser

echo ""
echo "============================================="
echo "   部署完成！"
echo "   访问地址: http://121.37.169.132"
echo "   后台管理: http://121.37.169.132/admin/"
echo "============================================="

# ===== 查看状态 =====
echo ""
echo "--- Gunicorn 状态 ---"
systemctl status novel-web --no-pager | head -10
echo ""
echo "--- Nginx 状态 ---"
systemctl status nginx --no-pager | head -5
