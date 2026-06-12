#!/bin/bash
# ============================================================
#  墨香书阁 (Mo Xiang Book Pavilion) 一键部署脚本
#  适用: Ubuntu 22.04 / 阿里云香港轻量服务器
#  数据库: MySQL 8.0
#  用法: bash deploy.sh
# ============================================================

set -e
echo "============================================"
echo "   墨香书阁 - 一键部署脚本 (MySQL版)"
echo "============================================"

# ---- 配置区（按需修改） ----
DOMAIN="your-domain.com"          # ← 改为你的域名
PROJECT_DIR="/www"                 # 项目根目录
BACKEND_DIR="${PROJECT_DIR}/novel_backend"
FRONTEND_DIR="${PROJECT_DIR}/novel_frontend"
DEPLOY_DIR="${PROJECT_DIR}/deploy"
PYTHON_VER="python3.8"
VENV_DIR="${BACKEND_DIR}/venv"
GIT_REPO="https://github.com/qsd22763/novel-web.git"

# MySQL 配置（首次部署时自动创建数据库和用户）
MYSQL_ROOT_PASS=""                # ← 留空则跳过创建，或填入 root 密码
DB_NAME="novel_fiction"
DB_USER="novel_user"
DB_PASS="$(openssl rand -base64 16)"   # 自动生成随机密码

# 颜色输出
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[x]${NC} $1"; }

# ---- Step 1: 系统基础依赖 ----
echo ""
echo ">>> [Step 1/10] 安装系统依赖..."
apt-get update && apt-get install -y \
    nginx python3.8 python3.8-venv python3-pip git \
    build-essential libmysqlclient-dev curl default-mysql-server
info "系统依赖安装完成 (含 MySQL)"

# ---- Step 2: MySQL 初始化 ----
echo ""
echo ">>> [Step 2/10] 配置 MySQL..."
if [ -n "$MYSQL_ROOT_PASS" ]; then
    mysql -u root -p"${MYSQL_ROOT_PASS}" -e "
        CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
        GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
        FLUSH PRIVILEGES;
    " 2>/dev/null && info "MySQL 数据库和用户已创建" || warn "MySQL 配置可能需要手动操作"
else
    warn "未设置 MYSQL_ROOT_PASS，请手动创建 MySQL 数据库："
    echo "    CREATE DATABASE ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "    CREATE USER '${DB_USER}'@'localhost' IDENTIFIED BY '你的密码';"
    echo "    GRANT ALL ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
fi

# ---- Step 3: 创建项目目录 ----
echo ""
echo ">>> [Step 3/10] 创建项目目录..."
mkdir -p ${PROJECT_DIR}
mkdir -p /var/log/novel
mkdir -p /var/run/novel
info "目录创建完成"

# ---- Step 4: 克隆/更新代码 ----
echo ""
echo ">>> [Step 4/10] 拉取代码..."
if [ -d "${BACKEND_DIR}" ]; then
    cd ${BACKEND_DIR} && git pull origin main
    cd ${FRONTEND_DIR} && git pull origin main
else
    git clone ${GIT_REPO} ${PROJECT_DIR}/temp_repo
    mv ${PROJECT_DIR}/temp_repo/novel_backend ${BACKEND_DIR}
    mv ${PROJECT_DIR}/temp_repo/novel_frontend ${FRONTEND_DIR}
    cp -r ${PROJECT_DIR}/temp_repo/deploy ${DEPLOY_DIR} 2>/dev/null || mkdir -p ${DEPLOY_DIR}
    rm -rf ${PROJECT_DIR}/temp_repo
fi
info "代码拉取完成"

# ---- Step 5: Python 虚拟环境 + 后端依赖 ----
echo ""
echo ">>> [Step 5/10] 配置 Python 环境..."
if [ ! -d "${VENV_DIR}" ]; then
    ${PYTHON_VER} -m venv ${VENV_DIR}
fi
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r ${BACKEND_DIR}/requirements.txt
info "Python 环境配置完成 (含 mysqlclient)"

# ---- Step 6: Django .env + 数据库迁移 ----
echo ""
echo ">>> [Step 6/10] 初始化 Django..."
cd ${BACKEND_DIR}

# 复制 .env（如果不存在）
if [ ! -f "${BACKEND_DIR}/.env" ]; then
    if [ -f "${BACKEND_DIR}/.env.example" ]; then
        cp ${BACKEND_DIR}/.env.example ${BACKEND_DIR}/.env
        # 自动填充生成的密码
        sed -i "s|your-mysql-password|${DB_PASS}|g" ${BACKEND_DIR}/.env
        warn ".env 已创建，密码: ${DB_PASS}"
        warn "请编辑 ${BACKEND_DIR}/.env 设置 SECRET_KEY 和域名！"
    fi
fi

python manage.py migrate
python manage.py collectstatic --noinput --clear
info "数据库迁移完成 (MySQL)"

# ---- Step 7: Node.js 前端构建 ----
echo ""
echo ">>> [Step 7/10] 构建前端..."
cd ${FRONTEND_DIR}

if ! command -v node &> /dev/null; then
    warn "Node.js 未安装，正在安装..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | -E bash -
    apt-get install -y nodejs
fi

npm install
npm run build
info "前端构建完成 (dist/)"

# ---- Step 8: Nginx 配置 ----
echo ""
echo ">>> [Step 8/10] 配置 Nginx..."
sed "s|your-domain.com|${DOMAIN}|g" ${DEPLOY_DIR}/nginx.conf > /etc/nginx/sites-available/novel-web.conf
ln -sf /etc/nginx/sites-available/novel-web.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
info "Nginx 配置完成"

# ---- Step 9: Systemd 服务 ----
echo ""
echo ">>> [Step 9/10] 注册 Gunicorn 服务..."
cp ${DEPLOY_DIR}/gunicorn_config.py ${BACKEND_DIR}/
cp ${DEPLOY_DIR}/novel-web.service /etc/systemd/system/

chown -R www-data:www-data ${PROJECT_DIR}
chmod -R 755 ${PROJECT_DIR}

systemctl daemon-reload
systemctl enable novel-web
systemctl restart novel-web
info "Gunicorn 服务已启动"

# ---- Step 10: 完成 ----
echo ""
echo "============================================"
echo -e "${GREEN}   部署完成！(MySQL)${NC}"
echo "============================================"
echo ""
echo "  访问地址: http://${DOMAIN}"
echo "  后台管理: http://${DOMAIN}/admin/"
echo ""
if [ -n "$DB_PASS" ]; then
    echo "  MySQL 密码: ${DB_PASS}"
    echo "  已写入 .env 文件"
fi
echo ""
echo "  常用命令:"
echo "    systemctl status novel-web     # 查看服务状态"
echo "    systemctl restart novel-web    # 重启后端"
echo "    journalctl -u novel-web -f     # 查看实时日志"
echo "    tail -f /var/log/novel/gunicorn_error.log  # 错误日志"
echo ""
echo "  更新部署:"
echo "    在服务器上运行: bash ${DEPLOY_DIR}/deploy.sh"
echo ""
