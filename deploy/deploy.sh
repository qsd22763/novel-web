#!/bin/bash
# ============================================================
#  墨香书阁 (Mo Xiang Book Pavilion) 一键部署脚本
#  适用: Ubuntu 22.04 / 阿里云香港轻量服务器
#  用法: bash deploy.sh
# ============================================================

set -e
echo "============================================"
echo "   墨香书阁 - 一键部署脚本"
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

# 颜色输出
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err() { echo -e "${RED}[x]${NC} $1"; }

# ---- Step 1: 系统基础依赖 ----
echo ""
echo ">>> [Step 1/9] 安装系统依赖..."
apt-get update && apt-get install -y \
    nginx python3.8 python3.8-venv python3-pip git \
    build-essential libpq-dev curl
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
    cd ${FRONTEND_DIR} && git pull origin main
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

# ---- Step 5: Django 数据库迁移 + 收集静态文件 ----
echo ""
echo ">>> [Step 5/9] 初始化数据库..."
cd ${BACKEND_DIR}

# 复制 .env（如果不存在）
if [ ! -f "${BACKEND_DIR}/.env" ]; then
    if [ -f "${BACKEND_DIR}/.env.example" ]; then
        cp ${BACKEND_DIR}/.env.example ${BACKEND_DIR}/.env
        warn "请编辑 ${BACKEND_DIR}/.env 设置 SECRET_KEY 和域名！"
    fi
fi

python manage.py migrate
python manage.py collectstatic --noinput --clear
info "数据库迁移完成"

# ---- Step 6: Node.js 前端构建 ----
echo ""
echo ">>> [Step 6/9] 构建前端..."
cd ${FRONTEND_DIR}

# 检查 Node.js
if ! command -v node &> /dev/null; then
    warn "Node.js 未安装，正在安装..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | -E bash -
    apt-get install -y nodejs
fi

npm install
npm run build
info "前端构建完成 (dist/)"

# ---- Step 7: Nginx 配置 ----
echo ""
echo ">>> [Step 7/9] 配置 Nginx..."
# 替换域名为实际值
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

# 确保 www-data 用户有权限
chown -R www-data:www-data ${PROJECT_DIR}
chmod -R 755 ${PROJECT_DIR}

systemctl daemon-reload
systemctl enable novel-web
systemctl restart novel-web
info "Gunicorn 服务已启动"

# ---- Step 9: 完成 ----
echo ""
echo "============================================"
echo -e "${GREEN}   部署完成！${NC}"
echo "============================================"
echo ""
echo "  访问地址: http://${DOMAIN}"
echo "  后台管理: http://${DOMAIN}/admin/"
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
