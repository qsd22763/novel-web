FROM node:20-alpine AS builder

WORKDIR /app

# 复制根依赖
COPY package.json package-lock.json* ./
RUN npm ci

# 复制前端代码并构建
COPY novel_frontend/ ./novel_frontend/
RUN cd novel_frontend && npm ci && npm run build

# ── 生产镜像 ──
FROM node:20-alpine

WORKDIR /app

# 安装基础工具
RUN apk add --no-cache curl

# 只复制生产依赖和 API 代码
COPY package.json package-lock.json* ./
RUN npm ci --production && npm cache clean --force

COPY api/ ./api/

# 从构建阶段复制前端产物
COPY --from=builder /app/novel_frontend/dist/ ./novel_frontend/dist/

# 数据目录
RUN mkdir -p /app/data

# 初始化数据库并填充种子数据
RUN node api/seed.js || true

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health/ || exit 1

CMD ["node", "api/index.js"]
