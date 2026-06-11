const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const { initDatabase } = require('./db');
const { authMiddleware } = require('./middleware/auth');

// 路由
const novelsRouter = require('./routes/novels');
const chaptersRouter = require('./routes/chapters');
const authRouter = require('./routes/auth');
const favoritesRouter = require('./routes/favorites');
const progressRouter = require('./routes/progress');
const bookmarksRouter = require('./routes/bookmarks');
const commentsRouter = require('./routes/comments');
const authorRouter = require('./routes/author');
const adminRouter = require('./routes/admin');
const checkinRouter = require('./routes/checkin');
const membershipRouter = require('./routes/membership');
const followRouter = require('./routes/follow');
const ratingRouter = require('./routes/rating');
const publicRouter = require('./routes/public');

function createApp() {
  const app = express();

  // 中间件
  app.use(cors({
    origin: true,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-User-ID'],
  }));
  app.use(express.json({ limit: '10mb' }));
  app.use(cookieParser());
  app.use(authMiddleware);

  // 健康检查
  app.get('/api/health/', (_req, res) => {
    try {
      const { getDb } = require('./db');
      const db = getDb();
      db.prepare('SELECT 1').get();
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    } catch (e) {
      res.status(503).json({ status: 'error', message: e.message });
    }
  });

  // API 路由注册（兼容 Django REST Framework 的 URL 格式）
  app.use('/api/novels', novelsRouter);
  app.use('/api/chapters', chaptersRouter);
  app.use('/api/auth', authRouter);
  app.use('/api/favorites', favoritesRouter);
  app.use('/api/reading-progress', progressRouter);
  app.use('/api/bookmarks', bookmarksRouter);
  app.use('/api/comments', commentsRouter);
  app.use('/api/author', authorRouter);
  app.use('/api/admin', adminRouter);
  app.use('/api/checkin', checkinRouter);
  app.use('/api/membership', membershipRouter);
  app.use('/api/follow', followRouter);
  app.use('/api/rating', ratingRouter);
  app.use('/api/public', publicRouter);

  // 404 处理
  app.use((req, res) => {
    if (req.path.startsWith('/api/')) {
      return res.status(404).json({ detail: `接口不存在: ${req.method} ${req.path}` });
    }
    res.status(404).send('Not Found');
  });

  // 错误处理中间件
  app.use((err, req, res, _next) => {
    console.error('API Error:', err.message, err.stack);
    res.status(err.status || 500).json({
      detail: err.message || '服务器内部错误',
    });
  });

  return app;
}

// ── Vercel Serverless 导出 ──
let _app;
let _initialized = false;

// 预初始化数据库（在 cold start 时）
async function ensureInit() {
  if (!_initialized) {
    await initDatabase();
    _app = createApp();
    // 填充种子数据（仅首次）
    try { const { runSeed } = require('./seed'); await runSeed(); } catch (_) {}
    _initialized = true;
  }
  return _app;
}

module.exports = async (req, res) => {
  const app = await ensureInit();
  return app(req, res);
};

// ── 本地开发模式 ──
if (require.main === module) {
  initDatabase()
    .then(() => {
      const { runSeed } = require('./seed');
      return runSeed();
    })
    .then(() => {
      const app = createApp();
      const PORT = process.env.PORT || 3000;
      app.listen(PORT, () => {
        console.log(`\n🚀 墨香书阁 API 服务已启动`);
        console.log(`   本地地址: http://localhost:${PORT}`);
        console.log(`   API 地址:   http://localhost:${PORT}/api/`);
        console.log(`   健康检查:   http://localhost:${PORT}/api/health/`);
        console.log(`\n📚 测试账号:`);
        console.log(`   普通用户: reader / 123456`);
        console.log(`   管理员:   admin / admin123\n`);
      });
    })
    .catch(e => {
      console.error('启动失败:', e.message);
      process.exit(1);
    });
}
