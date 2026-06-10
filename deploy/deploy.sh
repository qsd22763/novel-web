#!/bin/bash
# ============================================================
#  墨香书阁 - 云服务器一键部署脚本
#  适用: Ubuntu 22.04+ / 腾讯云/阿里云轻量服务器
#  数据库: Aiven MySQL (远程)
#  用法: bash deploy.sh
# ============================================================

set -e
echo "============================================"
echo "   墨香书阁 - 一键部署脚本 (Aiven MySQL)"
echo "============================================"

# ---- 配置区（按需修改） ----
DOMAIN="your-domain.com"          # ← 改为你的域名或服务器 IP
PROJECT_DIR="/www"
BACKEND_DIR="${PROJECT_DIR}/novel_backend"
FRONTEND_DIR="${PROJECT_DIR}/novel_frontend"
DEPLOY_DIR="${PROJECT_DIR}/deploy"
PYTHON_VER="python3"
VENV_DIR="${BACKEND_DIR}/venv"
GIT_REPO="https://github.com/qsd22763/novel-web.git"

# Aiven MySQL 配置 (从 https://console.aiven.com 获取)
DB_NAME="defaultdb"
DB_USER="avnadmin"
DB_HOST="mysql-29de8d23-novel-web.d.aivencloud.com"
DB_PORT="18683"
# DB_PASSWORD 将在 .env 中设置

# Django SECRET_KEY (请修改!)
SECRET_KEY="django-insecure-change-me-to-random-string-here"

# 颜色输出
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[x]${NC} $1"; }

# ---- Step 1: 系统基础依赖 ----
echo ""
echo ">>> [Step 1/9] 安装系统依赖..."
apt-get update && apt-get install -y \
    nginx python3 python3-venv python3-pip git \
    build-essential libmysqlclient-dev curl nodejs npm \
    ca-certificates
info "系统依赖安装完成"

# ---- Step 2: 创建项目目录 ----
echo ""
echo ">>> [Step 2/9] 创建项目目录..."
mkdir -p ${PROJECT_DIR}
mkdir -p /var/log/novel
mkdir -p /var/run/novel
info "目录创建完成"

# ---- Step 3: 克隆/更新代码 ----
echo ""
echo ">>> [Step 3/9] 拉取代码..."
if [ -d "${BACKEND_DIR}" ]; then
    cd ${BACKEND_DIR} && git pull origin main
else
    git clone ${GIT_REPO} ${PROJECT_DIR}/temp_repo
    mv ${PROJECT_DIR}/temp_repo/novel_backend ${BACKEND_DIR}
    mv ${PROJECT_DIR}/temp_repo/novel_frontend ${FRONTEND_DIR}
    cp -r ${PROJECT_DIR}/temp_repo/deploy ${DEPLOY_DIR} 2>/dev/null || mkdir -p ${DEPLOY_DIR}
    rm -rf ${PROJECT_DIR}/temp_repo
fi
info "代码拉取完成"

# ---- Step 4: Python 虚拟环境 + 后端依赖 ----
echo ""
echo ">>> [Step 4/9] 配置 Python 环境..."
if [ ! -d "${VENV_DIR}" ]; then
    ${PYTHON_VER} -m venv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r ${BACKEND_DIR}/requirements.txt
info "Python 环境配置完成"

# ---- Step 5: Django .env + 数据库迁移 ----
echo ""
echo ">>> [Step 5/9] 初始化 Django..."
cd ${BACKEND_DIR}

# 创建 .env 文件（使用 Aiven MySQL）
cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=${DOMAIN},localhost,127.0.0.1

# Aiven MySQL
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD:-请填写Aiven密码}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF

warn ".env 已创建！请编辑 ${BACKEND_DIR}/.env 填写 DB_PASSWORD"
warn "运行: nano ${BACKEND_DIR}/.env"

python manage.py migrate
python manage.py collectstatic --noinput --clear 2>/dev/null || true
info "数据库迁移完成 (连接到 Aiven MySQL)"

# ---- Step 6: Node.js 前端构建 ----
echo ""
echo ">>> [Step 6/9] 构建前端..."
cd ${FRONTEND_DIR}

npm install
npm run build:prod
info "前端构建完成 (dist/)"

# ---- Step 7: Nginx 配置 ----
echo ""
echo ">>> [Step 7/9] 配置 Nginx..."
sed "s|your-domain.com|${DOMAIN}|g" ${DEPLOY_DIR}/nginx.conf > /etc/nginx/sites-available/novel-web.conf
ln -sf /etc/nginx/sites-available/novel-web.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
info "Nginx 配置完成"

# ---- Step 8: Systemd 服务 ----
echo ""
echo ">>> [Step 8/9] 注册 Gunicorn 服务..."
cp ${DEPLOY_DIR}/gunicorn_config.py ${BACKEND_DIR}/
cp ${DEPLOY_DIR}/novel-web.service /etc/systemd/system/

chown -R www-data:www-data ${PROJECT_DIR}
chmod -R 755 ${PROJECT_DIR}

systemctl daemon-reload
systemctl enable novel-web
systemctl restart novel-web
info "Gunicorn 服务已启动"

# ---- Step 9: 完成 ----
echo ""
echo "============================================"
echo -e "${GREEN}   部署完成！(Aiven MySQL)${NC}"
echo "============================================"
echo ""
echo "  访问地址: http://${DOMAIN}"
echo "  API 测试: http://${DOMAIN}/api/novels/"
echo ""
echo "  ⚠️  重要：请设置数据库密码！"
echo "     nano ${BACKEND_DIR}/.env"
echo "     填写 DB_PASSWORD=你的Aiven密码"
echo "     然后: systemctl restart novel-web"
echo ""
echo "  常用命令:"
echo "    systemctl status novel-web       # 查看服务状态"
echo "    systemctl restart novel-web      # 重启后端"
echo "    journalctl -u novel-web -f       # 查看实时日志"
echo "    tail -f /var/log/novel/gunicorn_error.log  # 错误日志"
echo ""
echo "  更新部署:"
echo "    在服务器上运行: bash ${DEPLOY_DIR}/deploy.sh"
echo ""
