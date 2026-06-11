// ──────────────────────────────────────────────
//  api.js — Vercel 单函数合并入口（所有路由内联）
//  解决 Vercel Hobby 计划 12 Function 限制
// ──────────────────────────────────────────────

const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const { initDatabase, getDb, now } = require('./db-memory');

// ══════════════════════════════════════════════
//  中间件（原 middleware/auth.js 内联）
// ══════════════════════════════════════════════

function authMiddleware(req, res, next) {
  let user = null;
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    user = getUserByToken(authHeader.substring(7));
  }
  if (!user && req.headers['x-user-id']) {
    user = getUserById(req.headers['x-user-id']);
  }
  if (!user && req.cookies && req.cookies.user_id) {
    user = getUserById(req.cookies.user_id);
  }
  req.user = user || null;
  next();
}

function requireAuth(req, res, next) {
  if (!req.user) return res.status(401).json({ message: '未登录' });
  next();
}

function requireAdmin(req, res, next) {
  if (!req.user) return res.status(401).json({ message: '未登录' });
  if (!req.user.is_staff) return res.status(403).json({ message: '权限不足' });
  next();
}

function getUserByToken(token) {
  try {
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(parseInt(token));
    if (user) { delete user.password; return user; }
    const admin = db.prepare('SELECT *, 1 as is_staff FROM admin_user WHERE id = ?').get(parseInt(token));
    if (admin) { delete admin.password; return admin; }
    return null;
  } catch { return null; }
}

function getUserById(id) {
  try {
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(parseInt(id));
    if (user) { delete user.password; return user; }
    const admin = db.prepare('SELECT *, 1 as is_staff FROM admin_user WHERE id = ?').get(parseInt(id));
    if (admin) { delete admin.password; return admin; }
    return null;
  } catch { return null; }
}

// ══════════════════════════════════════════════
//  工具函数（原 routes/auth.js 的 formatUser）
// ══════════════════════════════════════════════

function formatUser(user) {
  return {
    id: user.id, username: user.username, email: user.email || '',
    avatar: user.avatar || '', phone: user.phone || '', is_staff: !!user.is_staff,
    is_vip: !!user.is_vip, vip_expire_date: user.vip_expire_date || null,
    is_author: !!user.is_author, pen_name: user.pen_name || '', bio: user.bio || '',
    coins: user.coins || 0, date_joined: user.date_joined,
  };
}

// ══════════════════════════════════════════════
//  创建 Express 应用（合并所有路由）
// ══════════════════════════════════════════════

function createApp() {
  const app = express();

  // 全局中间件
  app.use(cors({
    origin: true, credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-User-ID'],
  }));
  app.use(express.json({ limit: '10mb' }));
  app.use(cookieParser());
  app.use(authMiddleware);

  // ── 健康检查 ──
  app.get('/api/health/', (_req, res) => {
    try {
      const db = getDb();
      db.prepare('SELECT 1').get();
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    } catch (e) {
      res.status(503).json({ status: 'error', message: e.message });
    }
  });

  // ══════════════════════════════════════════════
  //  路由：novels（原 routes/novels.js）
  // ══════════════════════════════════════════════

  // GET /api/novels/ - 小说列表
  app.get('/api/novels/', (req, res) => {
    try {
      const db = getDb();
      const page = parseInt(req.query.page) || 1;
      const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
      const offset = (page - 1) * pageSize;
      let where = 'WHERE audit_status = 2 AND status != 2';
      const params = [];
      if (req.query.category) { where += ' AND category = ?'; params.push(req.query.category); }
      if (req.query.status !== undefined && req.query.status !== '') { where += ' AND status = ?'; params.push(parseInt(req.query.status)); }
      if (req.query.word_count_min) { where += ' AND word_count >= ?'; params.push(parseInt(req.query.word_count_min)); }
      if (req.query.word_count_max) { where += ' AND word_count <= ?'; params.push(parseInt(req.query.word_count_max)); }
      if (req.query.search) { where += ' AND (title LIKE ? OR author_name LIKE ?)'; params.push(`%${req.query.search}%`, `%${req.query.search}%`); }
      let orderBy = 'ORDER BY updated_at DESC';
      const ordering = req.query.ordering;
      if (ordering) {
        const allowedFields = ['updated_at','view_count','created_at','word_count','recommend','-updated_at','-view_count','-created_at','-word_count','-recommend'];
        if (allowedFields.includes(ordering)) {
          const dir = ordering.startsWith('-') ? 'DESC' : 'ASC';
          orderBy = `ORDER BY ${ordering.replace('-', '')} ${dir}`;
        }
      }
      const countRow = db.prepare(`SELECT COUNT(*) as total FROM novels ${where}`).get(...params);
      const rows = db.prepare(
        `SELECT n.*, (SELECT title FROM chapters WHERE novel_id = n.id ORDER BY chapter_order DESC LIMIT 1) as latest_chapter
         FROM novels n ${where} ${orderBy} LIMIT ? OFFSET ?`
      ).all(...params, pageSize, offset);
      res.json({
        count: rows.length,
        next: offset + pageSize < countRow.total ? `?page=${page + 1}&page_size=${pageSize}` : null,
        previous: page > 1 ? `?page=${page - 1}&page_size=${pageSize}` : null,
        results: rows.map(r => ({
          id: r.id, title: r.title, author: r.author_name, cover: r.cover, description: r.description,
          category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count,
          updated_at: r.updated_at, latest_chapter: r.latest_chapter,
        })),
      });
    } catch (e) { console.error('小说列表查询错误:', e.message); res.status(500).json({ detail: e.message }); }
  });

  // GET /api/novels/search/
  app.get('/api/novels/search', (req, res) => {
    try {
      const db = getDb();
      const q = req.query.q || '';
      const page = parseInt(req.query.page) || 1;
      const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
      const offset = (page - 1) * pageSize;
      const countRow = db.prepare("SELECT COUNT(*) as total FROM novels WHERE audit_status=2 AND status!=2 AND (title LIKE ? OR author_name LIKE ?)").get(`%${q}%`, `%${q}%`);
      const rows = db.prepare("SELECT *, (SELECT title FROM chapters WHERE novel_id=novels.id ORDER BY chapter_order DESC LIMIT 1) as latest_chapter FROM novels WHERE audit_status=2 AND status!=2 AND (title LIKE ? OR author_name LIKE ?) ORDER BY updated_at DESC LIMIT ? OFFSET ?").all(`%${q}%`, `%${q}%`, pageSize, offset);
      res.json({ count: rows.length, next: offset + pageSize < countRow.total ? null : null, results: rows.map(r => ({ id: r.id, title: r.title, author: r.author_name, cover: r.cover, description: r.description, category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count, updated_at: r.updated_at, latest_chapter: r.latest_chapter })) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // GET /api/novels/recommend/
  app.get('/api/novels/recommend', (req, res) => {
    try {
      const db = getDb();
      const limit = Math.min(parseInt(req.query.limit) || 10, 50);
      const rows = db.prepare("SELECT *, (SELECT title FROM chapters WHERE novel_id=novels.id ORDER BY chapter_order DESC LIMIT 1) as latest_chapter FROM novels WHERE audit_status=2 AND status!=2 ORDER BY view_count DESC LIMIT ?").all(limit);
      res.json(rows.map(r => ({ id: r.id, title: r.title, author: r.author_name, cover: r.cover, description: r.description, category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count, updated_at: r.updated_at, latest_chapter: r.latest_chapter })));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // GET /api/novels/category_stats/
  app.get('/api/novels/category_stats', (req, res) => {
    try {
      const db = getDb();
      const cats = db.prepare("SELECT name FROM categories WHERE is_active=1 ORDER BY sort_order").all();
      const stats = {};
      for (const cat of cats) stats[cat.name] = db.prepare('SELECT COUNT(*) as cnt FROM novels WHERE category=? AND audit_status=2 AND status!=2').get(cat.name).cnt;
      res.json(stats);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // GET /api/novels/:id/
  app.get('/api/novels/:id/', (req, res) => {
    try {
      const db = getDb();
      const row = db.prepare(`SELECT n.*, (SELECT COUNT(*) FROM chapters WHERE novel_id=n.id) as chapter_count, (SELECT COUNT(*) FROM comments WHERE novel_id=n.id) as comment_count, COALESCE((SELECT AVG(score) FROM ratings WHERE novel_id=n.id),0) as avg_rating FROM novels n WHERE n.id=?`).get(req.params.id);
      if (!row) return res.status(404).json({ detail: '小说不存在' });
      res.json({ id: row.id, title: row.title, author: row.author_name, cover: row.cover, description: row.description, category: row.category, status: row.status, word_count: row.word_count, view_count: row.view_count, chapter_count: row.chapter_count, comment_count: row.comment_count, avg_rating: parseFloat(row.avg_rating), created_at: row.created_at, updated_at: row.updated_at });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // GET /api/novels/:id/chapters/
  app.get('/api/novels/:id/chapters/', (req, res) => {
    try {
      const db = getDb();
      const novel = db.prepare('SELECT * FROM novels WHERE id=?').get(req.params.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在' });
      const chapters = db.prepare('SELECT id,title,chapter_order,word_count,created_at FROM chapters WHERE novel_id=? AND publish_status=1 ORDER BY chapter_order').all(req.params.id);
      res.json({ novel_id: novel.id, novel_title: novel.title, chapter_count: chapters.length, chapters });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：chapters（原 routes/chapters.js）
  // ══════════════════════════════════════════════

  app.get('/api/chapters/:id/', (req, res) => {
    try {
      const db = getDb();
      const chapter = db.prepare('SELECT c.*, n.title as novel_title, n.id as novel_id FROM chapters c JOIN novels n ON c.novel_id = n.id WHERE c.id = ?').get(req.params.id);
      if (!chapter) return res.status(404).json({ detail: '章节不存在' });
      db.prepare('UPDATE novels SET view_count = view_count + 1 WHERE id = ?').run(chapter.novel_id);
      const allChapters = db.prepare('SELECT id, title FROM chapters WHERE novel_id = ? AND publish_status = 1 ORDER BY chapter_order').all(chapter.novel_id);
      const currentIndex = allChapters.findIndex(c => c.id === parseInt(req.params.id));
      const prevChapter = currentIndex > 0 ? allChapters[currentIndex - 1] : null;
      const nextChapter = currentIndex < allChapters.length - 1 ? allChapters[currentIndex + 1] : null;
      res.json({ id: chapter.id, novel_id: chapter.novel_id, title: chapter.title, content: chapter.content, chapter_order: chapter.chapter_order, word_count: chapter.word_count, created_at: chapter.created_at, novel_title: chapter.novel_title, prev_chapter: prevChapter ? { id: prevChapter.id, title: prevChapter.title } : null, next_chapter: nextChapter ? { id: nextChapter.id, title: nextChapter.title } : null });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：auth（原 routes/auth.js）
  // ══════════════════════════════════════════════

  app.post('/api/auth/login/', (req, res) => {
    try {
      const { username, password } = req.body;
      if (!username || !password) return res.status(400).json({ username: ['请输入用户名'], password: ['请输入密码'] });
      const db = getDb();
      const user = db.prepare('SELECT * FROM users WHERE username = ? OR email = ?').get(username, username);
      if (!user || !bcrypt.compareSync(password, user.password)) return res.status(400).json({ non_field_errors: ['用户名或密码错误'] });
      delete user.password;
      res.json({ message: '登录成功', user: formatUser(user) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/auth/admin_login/', (req, res) => {
    try {
      const { username, password } = req.body;
      if (!username || !password) return res.status(400).json({ username: ['请输入管理员账号'], password: ['请输入密码'] });
      const db = getDb();
      const admin = db.prepare('SELECT * FROM admin_user WHERE username = ? AND is_active = 1').get(username);
      if (!admin || !bcrypt.compareSync(password, admin.password)) return res.status(400).json({ non_field_errors: ['管理员账号或密码错误'] });
      db.prepare('UPDATE admin_user SET last_login = ? WHERE id = ?').run(now(), admin.id);
      res.json({ message: '管理员登录成功', user: { id: admin.id, username: admin.username, real_name: admin.real_name || '', is_staff: true, role: 'admin' } });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/auth/register/', (req, res) => {
    try {
      const { username, email, password, password2 } = req.body;
      const errors = {};
      if (!username || username.length < 3) errors.username = ['用户名至少3个字符'];
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = ['请输入有效邮箱'];
      if (!password || password.length < 6) errors.password = ['密码至少6位'];
      if (password !== password2) errors.password2 = ['两次密码不一致'];
      if (Object.keys(errors).length > 0) return res.status(400).json(errors);
      const db = getDb();
      const existingUser = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?').get(username, email);
      if (existingUser) return res.status(400).json({ non_field_errors: ['用户名或邮箱已被注册'] });
      const hashedPwd = bcrypt.hashSync(password, 10);
      const result = db.prepare('INSERT INTO users (username, email, password, coins, date_joined) VALUES (?, ?, ?, 100, ?)').run(username, email, hashedPwd, now());
      const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);
      delete user.password;
      res.status(201).json({ message: '注册成功', user: formatUser(user) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/auth/logout/', (_req, res) => { res.json({ message: '退出登录成功' }); });

  app.get('/api/auth/me/', (req, res) => {
    if (!req.user) return res.status(401).json({ message: '未登录' });
    res.json(formatUser(req.user));
  });

  app.put('/api/auth/update_profile/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const data = req.body;
      const fields = [], params = [];
      if (data.avatar !== undefined) { fields.push('avatar = ?'); params.push(data.avatar); }
      if (data.phone !== undefined) { fields.push('phone = ?'); params.push(data.phone); }
      if (data.email !== undefined) { fields.push('email = ?'); params.push(data.email); }
      if (data.pen_name !== undefined) { fields.push('pen_name = ?'); params.push(data.pen_name); }
      if (data.bio !== undefined) { fields.push('bio = ?'); params.push(data.bio); }
      if (fields.length === 0) return res.status(400).json({ detail: '没有要更新的字段' });
      fields.push('updated_at = ?'); params.push(now()); params.push(req.user.id);
      db.prepare(`UPDATE users SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      const updated = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
      delete updated.password;
      res.json({ message: '更新成功', user: formatUser(updated) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/auth/change_password/', requireAuth, (req, res) => {
    try {
      const { old_password, new_password } = req.body;
      if (!old_password || !new_password) return res.status(400).json({ old_password: ['请输入旧密码'], new_password: ['请输入新密码'] });
      if (new_password.length < 6) return res.status(400).json({ new_password: ['密码至少6位'] });
      const db = getDb();
      const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
      if (!bcrypt.compareSync(old_password, user.password)) return res.status(400).json({ old_password: ['旧密码不正确'] });
      db.prepare('UPDATE users SET password = ? WHERE id = ?').run(bcrypt.hashSync(new_password, 10), req.user.id);
      res.json({ message: '密码修改成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：favorites（原 routes/favorites.js）
  // ══════════════════════════════════════════════

  app.get('/api/favorites/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const page = parseInt(req.query.page) || 1;
      const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
      const offset = (page - 1) * pageSize;
      const countRow = db.prepare('SELECT COUNT(*) as total FROM favorites WHERE user_id = ?').get(req.user.id);
      const rows = db.prepare(`SELECT f.*, n.title, n.author_name, n.cover, n.category, n.status, n.word_count, n.view_count, n.updated_at FROM favorites f JOIN novels n ON f.novel_id = n.id WHERE f.user_id = ? ORDER BY f.created_at DESC LIMIT ? OFFSET ?`).all(req.user.id, pageSize, offset);
      res.json({ count: rows.length, next: offset + pageSize < countRow.total ? `?page=${page + 1}` : null, previous: page > 1 ? `?page=${page - 1}` : null, results: rows.map(r => ({ id: r.id, novel_id: r.novel_id, title: r.title, author: r.author_name, cover: r.cover, category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count, updated_at: r.updated_at, created_at: r.created_at })) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/favorites/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const novelId = req.body.novel || req.body.novel_id;
      if (!novelId) return res.status(400).json({ novel: ['请选择要收藏的书籍'] });
      const exists = db.prepare('SELECT id FROM favorites WHERE user_id = ? AND novel_id = ?').get(req.user.id, novelId);
      if (exists) return res.status(400).json({ message: '已收藏' });
      const result = db.prepare('INSERT INTO favorites (user_id, novel_id, created_at) VALUES (?, ?, ?)').run(req.user.id, novelId, now());
      db.prepare('UPDATE novels SET favorite_count = favorite_count + 1 WHERE id = ?').run(novelId);
      const fav = db.prepare('SELECT * FROM favorites WHERE id = ?').get(result.lastInsertRowid);
      res.status(201).json(fav);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/favorites/delete_by_novel/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const novelId = req.body.novel_id || req.body.novel;
      if (!novelId) return res.status(400).json({ message: '缺少书籍ID参数' });
      const result = db.prepare('DELETE FROM favorites WHERE user_id = ? AND novel_id = ?').run(req.user.id, novelId);
      if (result.changes === 0) return res.status(404).json({ message: '收藏记录不存在' });
      db.prepare('UPDATE novels SET favorite_count = MAX(0, favorite_count - 1) WHERE id = ?').run(novelId);
      res.json({ message: '取消收藏成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/favorites/check', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const exists = db.prepare('SELECT id FROM favorites WHERE user_id = ? AND novel_id = ?').get(req.user.id, req.query.novel_id);
      res.json({ is_favorited: !!exists });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：progress（原 routes/progress.js）
  // ══════════════════════════════════════════════

  app.get('/api/reading-progress/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const rows = db.prepare(`SELECT rp.*, n.title as novel_title, ch.title as chapter_title FROM reading_progress rp JOIN novels n ON rp.novel_id = n.id LEFT JOIN chapters ch ON rp.chapter_id = ch.id WHERE rp.user_id = ? ORDER BY rp.updated_at DESC`).all(req.user.id);
      res.json(rows.map(r => ({ id: r.id, user_id: r.user_id, novel_id: r.novel_id, chapter_id: r.chapter_id, position: r.position, updated_at: r.updated_at, novel_title: r.novel_title, chapter_title: r.chapter_title })));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/reading-progress/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const { novel_id, chapter_id, position } = req.body;
      if (!novel_id || !chapter_id) return res.status(400).json({ detail: '缺少必要参数' });
      db.prepare(`INSERT INTO reading_progress (user_id, novel_id, chapter_id, position, updated_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id, novel_id) DO UPDATE SET chapter_id = excluded.chapter_id, position = excluded.position, updated_at = excluded.updated_at`).run(req.user.id, novel_id, chapter_id, position || 0, now());
      const saved = db.prepare('SELECT * FROM reading_progress WHERE user_id = ? AND novel_id = ?').get(req.user.id, novel_id);
      res.json({ message: '更新成功', progress: saved });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/reading-progress/get_progress', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const progress = db.prepare('SELECT * FROM reading_progress WHERE user_id = ? AND novel_id = ?').get(req.user.id, req.query.novel_id);
      if (!progress) return res.json({ message: '暂无阅读进度' });
      res.json(progress);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：bookmarks（原 routes/bookmarks.js）
  // ══════════════════════════════════════════════

  app.get('/api/bookmarks/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const rows = db.prepare(`SELECT b.*, n.title as novel_title, ch.title as chapter_title FROM bookmarks b JOIN novels n ON b.novel_id = n.id LEFT JOIN chapters ch ON b.chapter_id = ch.id WHERE b.user_id = ? ORDER BY b.created_at DESC`).all(req.user.id);
      res.json(rows.map(r => ({ id: r.id, user_id: r.user_id, novel_id: r.novel_id, chapter_id: r.chapter_id, position: r.position, note: r.note, created_at: r.created_at, novel_title: r.novel_title, chapter_title: r.chapter_title })));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/bookmarks/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const { novel_id, chapter_id, position, note } = req.body;
      if (!novel_id || !chapter_id) return res.status(400).json({ detail: '缺少必要参数' });
      const result = db.prepare('INSERT INTO bookmarks (user_id, novel_id, chapter_id, position, note, created_at) VALUES (?, ?, ?, ?, ?, ?)').run(req.user.id, novel_id, chapter_id, position || 0, note || '', now());
      const bookmark = db.prepare('SELECT * FROM bookmarks WHERE id = ?').get(result.lastInsertRowid);
      res.status(201).json(bookmark);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/bookmarks/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const result = db.prepare('DELETE FROM bookmarks WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id);
      if (result.changes === 0) return res.status(404).json({ detail: '书签不存在' });
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：comments（原 routes/comments.js）
  // ══════════════════════════════════════════════

  app.get('/api/comments/', (req, res) => {
    try {
      const db = getDb();
      const novelId = req.query.novel_id;
      const page = parseInt(req.query.page) || 1;
      const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
      const offset = (page - 1) * pageSize;
      let where = ''; const params = [];
      if (novelId) { where = 'WHERE c.novel_id = ?'; params.push(novelId); }
      const countRow = db.prepare(`SELECT COUNT(*) as total FROM comments c ${where}`).get(...params);
      const rows = db.prepare(`SELECT c.*, u.username, u.avatar FROM comments c LEFT JOIN users u ON c.user_id = u.id ${where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?`).all(...params, pageSize, offset);
      res.json({ count: rows.length, next: offset + pageSize < countRow.total ? null : null, results: rows.map(r => ({ id: r.id, user_id: r.user_id, novel_id: r.novel_id, content: r.content, rating: r.rating, created_at: r.created_at, user: { id: r.user_id, username: r.username, avatar: r.avatar } })) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/comments/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const { novel_id, content, rating } = req.body;
      if (!novel_id || !content) return res.status(400).json({ detail: '缺少必要参数' });
      const novel = db.prepare('SELECT id FROM novels WHERE id = ?').get(novel_id);
      if (!novel) return res.status(404).json({ detail: '小说不存在' });
      const result = db.prepare('INSERT INTO comments (user_id, novel_id, content, rating, created_at) VALUES (?, ?, ?, ?, ?)').run(req.user.id, novel_id, content, rating || 0, now());
      const comment = db.prepare('SELECT c.*, u.username, u.avatar FROM comments c LEFT JOIN users u ON c.user_id = u.id WHERE c.id = ?').get(result.lastInsertRowid);
      res.status(201).json(comment);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/comments/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const comment = db.prepare('SELECT * FROM comments WHERE id = ?').get(req.params.id);
      if (!comment) return res.status(404).json({ detail: '评论不存在' });
      if (comment.user_id !== req.user.id && !req.user.is_staff) return res.status(403).json({ detail: '无权删除此评论' });
      db.prepare('DELETE FROM comments WHERE id = ?').run(req.params.id);
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：author（原 routes/author.js）
  // ══════════════════════════════════════════════

  // 作者小说管理
  app.get('/api/author/novels/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const rows = db.prepare('SELECT * FROM novels WHERE author_user_id = ? ORDER BY updated_at DESC').all(req.user.id);
      res.json({ results: rows });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/author/novels/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const { title, author_name, cover, category, description, tags } = req.body;
      if (!title || !author_name || !category) return res.status(400).json({ detail: '标题、作者名和分类为必填项' });
      const result = db.prepare(`INSERT INTO novels (title, author_name, cover, category, description, tags, audit_status, status, created_at, updated_at, author_user_id) VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?, ?, ?)`).run(title, author_name, cover || '', category, description || '', tags || '', now(), now(), req.user.id);
      const novel = db.prepare('SELECT * FROM novels WHERE id = ?').get(result.lastInsertRowid);
      res.status(201).json(novel);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.patch('/api/author/novels/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(req.params.id, req.user.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在或无权操作' });
      const allowedFields = ['title', 'cover', 'category', 'description', 'tags', 'status'];
      const fields = [], params = [];
      for (const field of allowedFields) {
        if (req.body[field] !== undefined) { fields.push(`${field} = ?`); params.push(req.body[field]); }
      }
      if (fields.length === 0) return res.status(400).json({ detail: '没有可更新的字段' });
      fields.push('updated_at = ?'); params.push(now()); params.push(req.params.id);
      db.prepare(`UPDATE novels SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/author/novels/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(req.params.id, req.user.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在或无权操作' });
      db.prepare('DELETE FROM chapters WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM novels WHERE id = ?').run(req.params.id);
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // 作者章节管理
  app.get('/api/author/chapters/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const novelId = req.query.novel_id;
      if (!novelId) return res.status(400).json({ detail: '缺少 novel_id 参数' });
      const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(novelId, req.user.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在或无权操作' });
      const chapters = db.prepare('SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_order').all(novelId);
      res.json({ results: chapters, count: chapters.length });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/author/chapters/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const { novel_id, title, content, publish_status } = req.body;
      if (!novel_id || !title || !content) return res.status(400).json({ detail: '缺少必要参数' });
      const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(novel_id, req.user.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在或无权操作' });
      const maxOrder = db.prepare('SELECT COALESCE(MAX(chapter_order), 0) as mx FROM chapters WHERE novel_id = ?').get(novel_id).mx;
      const t = now();
      const result = db.prepare(`INSERT INTO chapters (novel_id, title, content, chapter_order, word_count, publish_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`).run(novel_id, title, content, maxOrder + 1, content.length, publish_status || 0, t, t);
      db.prepare(`UPDATE novels SET chapter_count = (SELECT COUNT(*) FROM chapters WHERE novel_id = ?), latest_chapter = ?, updated_at = ? WHERE id = ?`).run(novel_id, title, t, novel_id);
      res.status(201).json(db.prepare('SELECT * FROM chapters WHERE id = ?').get(result.lastInsertRowid));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.patch('/api/author/chapters/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const chapter = db.prepare(`SELECT c.* FROM chapters c JOIN novels n ON c.novel_id = n.id WHERE c.id = ? AND n.author_user_id = ?`).get(req.params.id, req.user.id);
      if (!chapter) return res.status(404).json({ detail: '章节不存在或无权操作' });
      const allowedFields = ['title', 'content', 'publish_status', 'chapter_order'];
      const fields = [], params = [];
      for (const field of allowedFields) {
        if (req.body[field] !== undefined) {
          fields.push(`${field} = ?`);
          if (field === 'content') { params.push(req.body[field]); fields.push('word_count = ?'); params.push(req.body[field].length); }
          else params.push(req.body[field]);
        }
      }
      if (fields.length === 0) return res.status(400).json({ detail: '没有可更新的字段' });
      fields.push('updated_at = ?'); params.push(now()); params.push(req.params.id);
      db.prepare(`UPDATE chapters SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM chapters WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/author/chapters/:id/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const chapter = db.prepare(`SELECT c.*, c.novel_id FROM chapters c JOIN novels n ON c.novel_id = n.id WHERE c.id = ? AND n.author_user_id = ?`).get(req.params.id, req.user.id);
      if (!chapter) return res.status(404).json({ detail: '章节不存在或无权操作' });
      db.prepare('DELETE FROM chapters WHERE id = ?').run(req.params.id);
      db.prepare(`UPDATE novels SET chapter_count = (SELECT COUNT(*) FROM chapters WHERE novel_id = ?), updated_at = ? WHERE id = ?`).run(chapter.novel_id, now(), chapter.novel_id);
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：admin（原 routes/admin.js）
  // ══════════════════════════════════════════════

  // 仪表盘统计
  app.get('/api/admin/books/dashboard_stats/', requireAdmin, (req, res) => {
    try {
      const db = getDb();
      const totalBooks = db.prepare('SELECT COUNT(*) as cnt FROM novels').get().cnt;
      const totalUsers = db.prepare('SELECT COUNT(*) as cnt FROM users').get().cnt;
      const totalChapters = db.prepare('SELECT COUNT(*) as cnt FROM chapters').get().cnt;
      const totalComments = db.prepare('SELECT COUNT(*) as cnt FROM comments').get().cnt;
      const totalViews = db.prepare("SELECT COALESCE(SUM(view_count), 0) as cnt FROM novels").get().cnt;
      const todayNewUsers = db.prepare("SELECT COUNT(*) as cnt FROM users WHERE date(date_joined) = date('now')").get().cnt;
      const pendingAudit = db.prepare("SELECT COUNT(*) as cnt FROM novels WHERE audit_status IN (0, 1)").get().cnt;
      const activeVips = db.prepare("SELECT COUNT(*) as cnt FROM users WHERE is_vip = 1 AND (vip_expire_date IS NULL OR vip_expire_date > datetime('now'))").get().cnt;
      const registerTrend = [];
      for (let i = 6; i >= 0; i--) {
        const dateStr = `date('now', '-${i} days')`;
        const row = db.prepare(`SELECT COUNT(*) as cnt FROM users WHERE date(date_joined) = ${dateStr}`).get();
        registerTrend.push({ date: new Date(Date.now() - i * 86400000).toISOString().split('T')[0], count: row.cnt });
      }
      res.json({ total_books: totalBooks, total_users: totalUsers, total_chapters: totalChapters, total_comments: totalComments, total_views: totalViews, today_new_users: todayNewUsers, pending_audit: pendingAudit, active_vips: activeVips, register_trend: registerTrend });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // 广告管理
  app.get('/api/admin/advertisements/', requireAdmin, (req, res) => {
    try { const db = getDb(); res.json({ count: (db.prepare('SELECT * FROM advertisements ORDER BY sort_order, created_at DESC')).all().length, results: db.prepare('SELECT * FROM advertisements ORDER BY sort_order, created_at DESC').all() }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/admin/advertisements/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const { title, ad_type, image_url, link_url, position, is_active, sort_order } = req.body;
      if (!title || !image_url || !position) return res.status(400).json({ detail: '标题、图片地址和位置为必填项' });
      const result = db.prepare(`INSERT INTO advertisements (title, ad_type, image_url, link_url, position, is_active, sort_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(title, ad_type || 'banner', image_url, link_url || '', position, is_active !== undefined ? (is_active ? 1 : 0) : 1, sort_order || 0, now(), now());
      res.status(201).json(db.prepare('SELECT * FROM advertisements WHERE id = ?').get(result.lastInsertRowid));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.patch('/api/admin/advertisements/:id/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const ad = db.prepare('SELECT * FROM advertisements WHERE id = ?').get(req.params.id);
      if (!ad) return res.status(404).json({ detail: '广告不存在' });
      const allowedFields = ['title', 'ad_type', 'image_url', 'link_url', 'position', 'is_active', 'sort_order']; const fields = []; const params = [];
      for (const f of allowedFields) { if (req.body[f] !== undefined) { fields.push(`${f} = ?`); params.push(f === 'is_active' ? (req.body[f] ? 1 : 0) : req.body[f]); } }
      fields.push('updated_at = ?'); params.push(now()); params.push(req.params.id);
      db.prepare(`UPDATE advertisements SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM advertisements WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/admin/advertisements/:id/', requireAdmin, (req, res) => {
    try { const db = getDb(); db.prepare('DELETE FROM advertisements WHERE id = ?').run(req.params.id); res.json({ message: '删除成功' }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // 公告管理
  app.get('/api/admin/announcements/', requireAdmin, (req, res) => {
    try { const db = getDb(); res.json({ count: (db.prepare('SELECT * FROM announcements ORDER BY is_pinned DESC, created_at DESC')).all().length, results: db.prepare('SELECT * FROM announcements ORDER BY is_pinned DESC, created_at DESC').all() }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/admin/announcements/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const { title, content, announcement_type, is_pinned, is_active } = req.body;
      if (!title || !content) return res.status(400).json({ detail: '标题和内容为必填项' });
      res.status(201).json(db.prepare('SELECT * FROM announcements WHERE id = ?').get(
        db.prepare(`INSERT INTO announcements (title, content, announcement_type, is_pinned, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)`).run(title, content, announcement_type || 'notice', is_pinned ? 1 : 0, is_active !== undefined ? (is_active ? 1 : 0) : 1, now(), now()).lastInsertRowid
      ));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.patch('/api/admin/announcements/:id/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const a = db.prepare('SELECT * FROM announcements WHERE id = ?').get(req.params.id);
      if (!a) return res.status(404).json({ detail: '公告不存在' });
      const allowedFields = ['title', 'content', 'announcement_type', 'is_pinned', 'is_active']; const fields = []; const params = [];
      for (const f of allowedFields) { if (req.body[f] !== undefined) { fields.push(`${f} = ?`); params.push(['is_pinned', 'is_active'].includes(f) ? (req.body[f] ? 1 : 0) : req.body[f]); } }
      fields.push('updated_at = ?'); params.push(now()); params.push(req.params.id);
      db.prepare(`UPDATE announcements SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM announcements WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/admin/announcements/:id/', requireAdmin, (req, res) => {
    try { const db = getDb(); db.prepare('DELETE FROM announcements WHERE id = ?').run(req.params.id); res.json({ message: '删除成功' }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // 书籍管理（管理员）
  app.get('/api/admin/books/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const page = parseInt(req.query.page) || 1; const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100); const offset = (page - 1) * pageSize;
      let where = ''; const params = [];
      if (req.query.search) { where += "WHERE title LIKE ? OR author_name LIKE ?"; params.push(`%${req.query.search}%`, `%${req.query.search}%`); }
      if (req.query.audit_status !== undefined && req.query.audit_status !== '') { where += (where ? ' AND ' : 'WHERE ') + 'audit_status = ?'; params.push(parseInt(req.query.audit_status)); }
      const countRow = db.prepare(`SELECT COUNT(*) as total FROM novels ${where}`).get(...params);
      const rows = db.prepare(`SELECT * FROM novels ${where} ORDER BY updated_at DESC LIMIT ? OFFSET ?`).all(...params, pageSize, offset);
      res.json({ count: rows.length, next: offset + pageSize < countRow.total ? null : null, results: rows });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/admin/books/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const { title, author_name, cover, category, description, status, audit_status } = req.body;
      if (!title || !author_name || !category) return res.status(400).json({ detail: '标题、作者名和分类为必填项' });
      const t = now();
      res.status(201).json(db.prepare('SELECT * FROM novels WHERE id = ?').get(
        db.prepare(`INSERT INTO novels (title, author_name, cover, category, description, status, audit_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(title, author_name, cover || '', category, description || '', status || 0, audit_status || 2, t, t).lastInsertRowid
      ));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.patch('/api/admin/books/:id/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const novel = db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id);
      if (!novel) return res.status(404).json({ detail: '小说不存在' });
      const allowedFields = ['title', 'author_name', 'cover', 'category', 'description', 'status', 'audit_status', 'word_count', 'view_count', 'recommend', 'is_recommended']; const fields = []; const params = [];
      for (const f of allowedFields) { if (req.body[f] !== undefined) { fields.push(`${f} = ?`); params.push(req.body[f]); } }
      fields.push('updated_at = ?'); params.push(now()); params.push(req.params.id);
      db.prepare(`UPDATE novels SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/admin/books/:id/', requireAdmin, (req, res) => {
    try {
      const db = getDb();
      db.prepare('DELETE FROM chapters WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM favorites WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM comments WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM ratings WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM reading_progress WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM bookmarks WHERE novel_id = ?').run(req.params.id);
      db.prepare('DELETE FROM novels WHERE id = ?').run(req.params.id);
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // 分类管理
  app.get('/api/admin/categories/', requireAdmin, (req, res) => {
    try { const db = getDb(); res.json({ count: (db.prepare('SELECT * FROM categories ORDER BY sort_order, id')).all().length, results: db.prepare('SELECT * FROM categories ORDER BY sort_order, id').all() }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/admin/categories/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const { name, parent_id, sort_order, color, description } = req.body;
      if (!name) return res.status(400).json({ detail: '分类名称不能为空' });
      res.status(201).json(db.prepare('SELECT * FROM categories WHERE id = ?').get(
        db.prepare('INSERT INTO categories (name, parent_id, sort_order, color, description, is_active, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)').run(name, parent_id || null, sort_order || 0, color || '#3B82F6', description || '', now()).lastInsertRowid
      ));
    } catch (e) { res.status(400).json({ detail: e.message }); }
  });

  app.patch('/api/admin/categories/:id/', requireAdmin, (req, res) => {
    try {
      const db = getDb(); const cat = db.prepare('SELECT * FROM categories WHERE id = ?').get(req.params.id);
      if (!cat) return res.status(404).json({ detail: '分类不存在' });
      const allowedFields = ['name', 'parent_id', 'sort_order', 'color', 'description', 'is_active', 'book_count']; const fields = []; const params = [];
      for (const f of allowedFields) { if (req.body[f] !== undefined) { fields.push(`${f} = ?`); params.push(req.body[f]); } }
      if (fields.length === 0) return res.status(400).json({ detail: '没有可更新的字段' });
      params.push(req.params.id);
      db.prepare(`UPDATE categories SET ${fields.join(', ')} WHERE id = ?`).run(...params);
      res.json(db.prepare('SELECT * FROM categories WHERE id = ?').get(req.params.id));
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/admin/categories/:id/', requireAdmin, (req, res) => {
    try { const db = getDb(); db.prepare('DELETE FROM categories WHERE id = ?').run(req.params.id); res.json({ message: '删除成功' }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：checkin（原 routes/checkin.js）
  // ══════════════════════════════════════════════

  app.post('/api/checkin/do_checkin/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const today = new Date().toISOString().split('T')[0];
      const existing = db.prepare('SELECT id FROM checkins WHERE user_id = ? AND check_date = ?').get(req.user.id, today);
      if (existing) return res.status(400).json({ message: '今天已经签过了，明天再来吧~' });
      const reward = 10;
      db.prepare('BEGIN TRANSACTION');
      db.prepare('INSERT INTO checkins (user_id, check_date, reward_coins, created_at) VALUES (?, ?, ?, ?)').run(req.user.id, today, reward, now());
      db.prepare('UPDATE users SET coins = coins + ? WHERE id = ?').run(reward, req.user.id);
      db.prepare('COMMIT');
      const streakRows = db.prepare(`SELECT check_date FROM checkins WHERE user_id = ? ORDER BY check_date DESC LIMIT 7`).all(req.user.id);
      let streak = 0; const todayDate = new Date(today);
      for (const r of streakRows) { const expected = new Date(todayDate); expected.setDate(expected.getDate() - streak); if (r.check_date === expected.toISOString().split('T')[0]) streak++; else break; }
      const user = db.prepare('SELECT coins FROM users WHERE id = ?').get(req.user.id);
      res.json({ message: '签到成功！', reward_coins: reward, current_coins: user.coins, continuous_days: streak });
    } catch (e) { try { getDb().prepare('ROLLBACK').run(); } catch (_) {} res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/checkin/status/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const today = new Date().toISOString().split('T')[0];
      const todayCheckin = db.prepare('SELECT * FROM checkins WHERE user_id = ? AND check_date = ?').get(req.user.id, today);
      const recentCheckins = db.prepare(`SELECT check_date, reward_coins FROM checkins WHERE user_id = ? ORDER BY check_date DESC LIMIT 30`).all(req.user.id);
      const monthStart = new Date().toISOString().slice(0, 7) + '-01';
      const monthlyCount = db.prepare("SELECT COUNT(*) as cnt FROM checkins WHERE user_id = ? AND check_date >= ?").get(req.user.id, monthStart).cnt;
      const totalCount = db.prepare('SELECT COUNT(*) as cnt FROM checkins WHERE user_id = ?').get(req.user.id).cnt;
      res.json({ checked_today: !!todayCheckin, today_reward: todayCheckin ? todayCheckin.reward_coins : 0, recent_checkins: recentCheckins.map(r => ({ date: r.check_date, coins: r.reward_coins })), monthly_count: monthlyCount, total_count: totalCount });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：membership（原 routes/membership.js）
  // ══════════════════════════════════════════════

  app.get('/api/membership/plans/', (_req, res) => {
    try {
      res.json([
        { id: 'monthly', name: '月卡会员', price: 18.00, duration: 30, benefits: ['免广告阅读', '专属书架', '优先客服'] },
        { id: 'quarterly', name: '季卡会员', price: 45.00, duration: 90, benefits: ['免广告阅读', '专属书架', '优先客服', '每月赠送200币'] },
        { id: 'yearly', name: '年卡会员', price: 148.00, duration: 365, benefits: ['免广告阅读', '专属书架', '优先客服', '每月赠送300币', '生日特权'] },
      ]);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/membership/my_status/', requireAuth, (req, res) => {
    try {
      const db = getDb();
      const user = db.prepare('SELECT is_vip, vip_expire_date, coins FROM users WHERE id = ?').get(req.user.id);
      const isVip = user.is_vip === 1 && (!user.vip_expire_date || new Date(user.vip_expire_date) > new Date());
      const orders = db.prepare('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5').all(req.user.id);
      res.json({ is_vip: isVip, vip_expire_date: user.vip_expire_date, coins: user.coins, recent_orders: orders.map(o => ({ id: o.id, order_no: o.order_no, plan_type: o.plan_type, amount: o.amount, status: o.status, created_at: o.created_at })) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/membership/purchase/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const { plan_type } = req.body;
      const plans = { monthly: 18.00, quarterly: 45.00, yearly: 148.00 };
      const durations = { monthly: 30, quarterly: 90, yearly: 365 };
      if (!plans[plan_type]) return res.status(400).json({ detail: '无效的套餐类型' });
      const orderNo = uuidv4().replace(/-/g, '').substring(0, 32); const amount = plans[plan_type];
      const result = db.prepare('INSERT INTO orders (order_no, user_id, plan_type, amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?)').run(orderNo, req.user.id, plan_type, amount, 'pending', now());
      const expireAt = new Date(); expireAt.setDate(expireAt.getDate() + durations[plan_type]);
      db.prepare('UPDATE orders SET status = ?, paid_at = ?, expire_at = ? WHERE id = ?').run('paid', now(), expireAt.toISOString(), result.lastInsertRowid);
      db.prepare('UPDATE users SET is_vip = 1, vip_expire_date = ? WHERE id = ?').run(expireAt.toISOString(), req.user.id);
      res.status(201).json({ message: '购买成功！', order: db.prepare('SELECT * FROM orders WHERE id = ?').get(result.lastInsertRowid) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：follow（原 routes/follow.js）
  // ══════════════════════════════════════════════

  app.get('/api/follow/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const page = parseInt(req.query.page) || 1; const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100); const offset = (page - 1) * pageSize;
      const countRow = db.prepare('SELECT COUNT(*) as total FROM follows WHERE follower_id = ?').get(req.user.id);
      const rows = db.prepare('SELECT * FROM follows WHERE follower_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?').all(req.user.id, pageSize, offset);
      res.json({ count: rows.length, next: offset + pageSize < countRow.total ? null : null, results: rows });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/follow/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const { author_name } = req.body;
      if (!author_name) return res.status(400).json({ detail: '请指定要关注的作者' });
      const exists = db.prepare('SELECT id FROM follows WHERE follower_id = ? AND following_name = ?').get(req.user.id, author_name);
      if (exists) return res.status(400).json({ message: '已关注该作者' });
      db.prepare('INSERT INTO follows (follower_id, following_name, created_at) VALUES (?, ?, ?)').run(req.user.id, author_name, now());
      res.status(201).json({ message: '关注成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/follow/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const { author_name } = req.body;
      if (!author_name) return res.status(400).json({ detail: '请指定要取消关注的作者' });
      const result = db.prepare('DELETE FROM follows WHERE follower_id = ? AND following_name = ?').run(req.user.id, author_name);
      if (result.changes === 0) return res.status(404).json({ message: '未找到关注记录' });
      res.json({ message: '取消关注成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/follow/check', requireAuth, (req, res) => {
    try { const db = getDb(); const exists = db.prepare('SELECT id FROM follows WHERE follower_id = ? AND following_name = ?').get(req.user.id, req.query.author_name); res.json({ is_following: !!exists }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：rating（原 routes/rating.js）
  // ══════════════════════════════════════════════

  app.get('/api/rating/', (req, res) => {
    try {
      const db = getDb(); const novelId = req.query.novel_id;
      if (!novelId) return res.status(400).json({ detail: '缺少 novel_id 参数' });
      const rows = db.prepare(`SELECT r.*, u.username, u.avatar FROM ratings r LEFT JOIN users u ON r.user_id = u.id WHERE r.novel_id = ? ORDER BY r.created_at DESC`).all(novelId);
      const avgRow = db.prepare('SELECT AVG(score) as avg, COUNT(*) as cnt FROM ratings WHERE novel_id = ?').get(novelId);
      res.json({ average_score: parseFloat(avgRow.avg?.toFixed(1)) || 0, rating_count: avgRow.cnt || 0, results: rows.map(r => ({ id: r.id, user_id: r.user_id, novel_id: r.novel_id, score: r.score, created_at: r.created_at, user: { username: r.username, avatar: r.avatar } })) });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.post('/api/rating/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const { novel_id, score } = req.body;
      if (!novel_id || !score) return res.status(400).json({ detail: '缺少必要参数' });
      if (score < 1 || score > 5) return res.status(400).json({ detail: '评分必须在1-5之间' });
      const novel = db.prepare('SELECT id FROM novels WHERE id = ?').get(novel_id);
      if (!novel) return res.status(404).json({ detail: '小说不存在' });
      const existing = db.prepare('SELECT id FROM ratings WHERE user_id = ? AND novel_id = ?').get(req.user.id, novel_id);
      if (existing) db.prepare('UPDATE ratings SET score = ?, created_at = ? WHERE id = ?').run(score, now(), existing.id);
      else db.prepare('INSERT INTO ratings (user_id, novel_id, score, created_at) VALUES (?, ?, ?, ?)').run(req.user.id, novel_id, score, now());
      const avgRow = db.prepare('SELECT AVG(score) as avg FROM ratings WHERE novel_id = ?').get(novel_id);
      res.json({ message: existing ? '评分更新成功' : '评分提交成功', average_score: parseFloat(avgRow.avg?.toFixed(1)) || 0 });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/rating/my_rating', requireAuth, (req, res) => {
    try {
      const db = getDb(); const rating = db.prepare('SELECT * FROM ratings WHERE user_id = ? AND novel_id = ?').get(req.user.id, req.query.novel_id);
      if (!rating) return res.json({ message: '暂未评分' });
      res.json(rating);
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.delete('/api/rating/', requireAuth, (req, res) => {
    try {
      const db = getDb(); const { novel_id } = req.body;
      if (!novel_id) return res.status(400).json({ detail: '缺少 novel_id 参数' });
      const result = db.prepare('DELETE FROM ratings WHERE user_id = ? AND novel_id = ?').run(req.user.id, novel_id);
      if (result.changes === 0) return res.status(404).json({ message: '评分不存在' });
      res.json({ message: '删除成功' });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ══════════════════════════════════════════════
  //  路由：public（原 routes/public.js）
  // ══════════════════════════════════════════════

  app.get('/api/public/advertisements/', (req, res) => {
    try {
      const db = getDb(); const position = req.query.position; let rows;
      if (position) rows = db.prepare('SELECT * FROM advertisements WHERE is_active=1 AND position=? ORDER BY sort_order').all(position);
      else rows = db.prepare('SELECT * FROM advertisements WHERE is_active=1 ORDER BY sort_order').all();
      res.json({ count: rows.length, results: rows });
    } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  app.get('/api/public/announcements/', (_req, res) => {
    try { const db = getDb(); res.json({ count: (db.prepare('SELECT * FROM announcements WHERE is_active=1 ORDER BY is_pinned DESC, created_at DESC')).all().length, results: db.prepare('SELECT * FROM announcements WHERE is_active=1 ORDER BY is_pinned DESC, created_at DESC').all() }); } catch (e) { res.status(500).json({ detail: e.message }); }
  });

  // ── 404 处理 ──
  app.use((req, res) => {
    if (req.path.startsWith('/api/')) return res.status(404).json({ detail: `接口不存在: ${req.method} ${req.path}` });
    res.status(404).send('Not Found');
  });

  // ── 错误处理中间件 ──
  app.use((err, req, res, _next) => {
    console.error('API Error:', err.message, err.stack);
    res.status(err.status || 500).json({ detail: err.message || '服务器内部错误' });
  });

  return app;
}

// ══════════════════════════════════════════════
//  Vercel Serverless 导出 & 本地开发入口
// ══════════════════════════════════════════════

let _app;
let _initialized = false;

async function ensureInit() {
  if (!_initialized) {
    await initDatabase();
    _app = createApp();
    try { const { runSeed } = require('./seed'); await runSeed(); } catch (_) {}
    _initialized = true;
  }
  return _app;
}

// Vercel Serverless handler
const handler = async (req, res) => {
  const app = await ensureInit();
  return app(req, res);
};

// 本地开发启动
function startLocal() {
  initDatabase()
    .then(() => { const { runSeed } = require('./seed'); return runSeed(); })
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
    .catch(e => { console.error('启动失败:', e.message); process.exit(1); });
}

module.exports = { handler, startLocal };
