const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth, requireAdmin } = require('../middleware/auth');

// ── 仪表盘统计 ──

router.get('/books/dashboard_stats/', requireAdmin, (req, res) => {
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

    // 最近7天注册趋势
    const registerTrend = [];
    for (let i = 6; i >= 0; i--) {
      const dateStr = `date('now', '-${i} days')`;
      const row = db.prepare(`SELECT COUNT(*) as cnt FROM users WHERE date(date_joined) = ${dateStr}`).get();
      registerTrend.push({ date: new Date(Date.now() - i * 86400000).toISOString().split('T')[0], count: row.cnt });
    }

    res.json({
      total_books: totalBooks,
      total_users: totalUsers,
      total_chapters: totalChapters,
      total_comments: totalComments,
      total_views: totalViews,
      today_new_users: todayNewUsers,
      pending_audit: pendingAudit,
      active_vips: activeVips,
      register_trend: registerTrend,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// ── 广告管理 ──

router.get('/advertisements/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare('SELECT * FROM advertisements ORDER BY sort_order, created_at DESC').all();
    res.json({ count: rows.length, results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.post('/advertisements/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const { title, ad_type, image_url, link_url, position, is_active, sort_order } = req.body;
    if (!title || !image_url || !position) {
      return res.status(400).json({ detail: '标题、图片地址和位置为必填项' });
    }

    const result = db.prepare(
      `INSERT INTO advertisements (title, ad_type, image_url, link_url, position, is_active, sort_order, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).run(title, ad_type || 'banner', image_url, link_url || '', position, is_active !== undefined ? (is_active ? 1 : 0) : 1, sort_order || 0, now(), now());

    const ad = db.prepare('SELECT * FROM advertisements WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(ad);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.patch('/advertisements/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const ad = db.prepare('SELECT * FROM advertisements WHERE id = ?').get(req.params.id);
    if (!ad) return res.status(404).json({ detail: '广告不存在' });

    const allowedFields = ['title', 'ad_type', 'image_url', 'link_url', 'position', 'is_active', 'sort_order'];
    const fields = [];
    const params = [];
    for (const f of allowedFields) {
      if (req.body[f] !== undefined) {
        fields.push(`${f} = ${f === 'is_active' ? '?' : '?'}`);
        params.push(f === 'is_active' ? (req.body[f] ? 1 : 0) : req.body[f]);
      }
    }
    fields.push('updated_at = ?');
    params.push(now());
    params.push(req.params.id);

    db.prepare(`UPDATE advertisements SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    res.json(db.prepare('SELECT * FROM advertisements WHERE id = ?').get(req.params.id));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.delete('/advertisements/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    db.prepare('DELETE FROM advertisements WHERE id = ?').run(req.params.id);
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// ── 公告管理 ──

router.get('/announcements/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare('SELECT * FROM announcements ORDER BY is_pinned DESC, created_at DESC').all();
    res.json({ count: rows.length, results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.post('/announcements/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const { title, content, announcement_type, is_pinned, is_active } = req.body;
    if (!title || !content) {
      return res.status(400).json({ detail: '标题和内容为必填项' });
    }

    const result = db.prepare(
      `INSERT INTO announcements (title, content, announcement_type, is_pinned, is_active, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    ).run(title, content, announcement_type || 'notice', is_pinned ? 1 : 0, is_active !== undefined ? (is_active ? 1 : 0) : 1, now(), now());

    res.status(201).json(db.prepare('SELECT * FROM announcements WHERE id = ?').get(result.lastInsertRowid));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.patch('/announcements/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const a = db.prepare('SELECT * FROM announcements WHERE id = ?').get(req.params.id);
    if (!a) return res.status(404).json({ detail: '公告不存在' });

    const allowedFields = ['title', 'content', 'announcement_type', 'is_pinned', 'is_active'];
    const fields = [];
    const params = [];
    for (const f of allowedFields) {
      if (req.body[f] !== undefined) {
        fields.push(`${f} = ?`);
        params.push(['is_pinned', 'is_active'].includes(f) ? (req.body[f] ? 1 : 0) : req.body[f]);
      }
    }
    fields.push('updated_at = ?');
    params.push(now());
    params.push(req.params.id);

    db.prepare(`UPDATE announcements SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    res.json(db.prepare('SELECT * FROM announcements WHERE id = ?').get(req.params.id));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.delete('/announcements/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    db.prepare('DELETE FROM announcements WHERE id = ?').run(req.params.id);
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// ── 书籍管理（管理员） ──

router.get('/books/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const page = parseInt(req.query.page) || 1;
    const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
    const offset = (page - 1) * pageSize;

    let where = '';
    const params = [];
    if (req.query.search) {
      where += "WHERE title LIKE ? OR author_name LIKE ?";
      params.push(`%${req.query.search}%`, `%${req.query.search}%`);
    }
    if (req.query.audit_status !== undefined && req.query.audit_status !== '') {
      where += (where ? ' AND ' : 'WHERE ') + 'audit_status = ?';
      params.push(parseInt(req.query.audit_status));
    }

    const countRow = db.prepare(`SELECT COUNT(*) as total FROM novels ${where}`).get(...params);
    const rows = db.prepare(`SELECT * FROM novels ${where} ORDER BY updated_at DESC LIMIT ? OFFSET ?`).all(...params, pageSize, offset);

    res.json({
      count: rows.length,
      next: offset + pageSize < countRow.total ? null : null,
      results: rows,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.post('/books/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const { title, author_name, cover, category, description, status, audit_status } = req.body;
    if (!title || !author_name || !category) {
      return res.status(400).json({ detail: '标题、作者名和分类为必填项' });
    }

    const t = now();
    const result = db.prepare(`
      INSERT INTO novels (title, author_name, cover, category, description, status, audit_status, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(title, author_name, cover || '', category, description || '', status || 0, audit_status || 2, t, t);

    res.status(201).json(db.prepare('SELECT * FROM novels WHERE id = ?').get(result.lastInsertRowid));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.patch('/books/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const novel = db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id);
    if (!novel) return res.status(404).json({ detail: '小说不存在' });

    const allowedFields = ['title', 'author_name', 'cover', 'category', 'description', 'status', 'audit_status', 'word_count', 'view_count', 'recommend', 'is_recommended'];
    const fields = [];
    const params = [];
    for (const f of allowedFields) {
      if (req.body[f] !== undefined) {
        fields.push(`${f} = ?`);
        params.push(req.body[f]);
      }
    }
    fields.push('updated_at = ?');
    params.push(now());
    params.push(req.params.id);

    db.prepare(`UPDATE novels SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    res.json(db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.delete('/books/:id/', requireAdmin, (req, res) => {
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
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// ── 分类管理 ──

router.get('/categories/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare('SELECT * FROM categories ORDER BY sort_order, id').all();
    res.json({ count: rows.length, results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.post('/categories/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const { name, parent_id, sort_order, color, description } = req.body;
    if (!name) return res.status(400).json({ detail: '分类名称不能为空' });

    const result = db.prepare(
      'INSERT INTO categories (name, parent_id, sort_order, color, description, is_active, created_at) VALUES (?, ?, ?, ?, ?, 1, ?)'
    ).run(name, parent_id || null, sort_order || 0, color || '#3B82F6', description || '', now());

    res.status(201).json(db.prepare('SELECT * FROM categories WHERE id = ?').get(result.lastInsertRowid));
  } catch (e) {
    res.status(400).json({ detail: e.message });
  }
});

router.patch('/categories/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    const cat = db.prepare('SELECT * FROM categories WHERE id = ?').get(req.params.id);
    if (!cat) return res.status(404).json({ detail: '分类不存在' });

    const allowedFields = ['name', 'parent_id', 'sort_order', 'color', 'description', 'is_active', 'book_count'];
    const fields = [];
    const params = [];
    for (const f of allowedFields) {
      if (req.body[f] !== undefined) {
        fields.push(`${f} = ?`);
        params.push(req.body[f]);
      }
    }
    if (fields.length === 0) return res.status(400).json({ detail: '没有可更新的字段' });
    params.push(req.params.id);

    db.prepare(`UPDATE categories SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    res.json(db.prepare('SELECT * FROM categories WHERE id = ?').get(req.params.id));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

router.delete('/categories/:id/', requireAdmin, (req, res) => {
  try {
    const db = getDb();
    db.prepare('DELETE FROM categories WHERE id = ?').run(req.params.id);
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
