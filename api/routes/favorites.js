const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/favorites/ - 收藏列表
router.get('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const page = parseInt(req.query.page) || 1;
    const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
    const offset = (page - 1) * pageSize;

    const countRow = db.prepare('SELECT COUNT(*) as total FROM favorites WHERE user_id = ?').get(req.user.id);
    const rows = db.prepare(`
      SELECT f.*, n.title, n.author_name, n.cover, n.category, n.status, n.word_count, n.view_count, n.updated_at
      FROM favorites f JOIN novels n ON f.novel_id = n.id
      WHERE f.user_id = ? ORDER BY f.created_at DESC LIMIT ? OFFSET ?
    `).all(req.user.id, pageSize, offset);

    res.json({
      count: rows.length,
      next: offset + pageSize < countRow.total ? `?page=${page + 1}` : null,
      previous: page > 1 ? `?page=${page - 1}` : null,
      results: rows.map(r => ({
        id: r.id, novel_id: r.novel_id, title: r.title, author: r.author_name,
        cover: r.cover, category: r.category, status: r.status,
        word_count: r.word_count, view_count: r.view_count, updated_at: r.updated_at, created_at: r.created_at,
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/favorites/ - 添加收藏
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.body.novel || req.body.novel_id;
    if (!novelId) {
      return res.status(400).json({ novel: ['请选择要收藏的书籍'] });
    }

    const exists = db.prepare('SELECT id FROM favorites WHERE user_id = ? AND novel_id = ?').get(req.user.id, novelId);
    if (exists) {
      return res.status(400).json({ message: '已收藏' });
    }

    const result = db.prepare('INSERT INTO favorites (user_id, novel_id, created_at) VALUES (?, ?, ?)').run(req.user.id, novelId, now());
    db.prepare('UPDATE novels SET favorite_count = favorite_count + 1 WHERE id = ?').run(novelId);

    const fav = db.prepare('SELECT * FROM favorites WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(fav);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/favorites/delete_by_novel/ - 删除收藏
router.post('/delete_by_novel/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.body.novel_id || req.body.novel;
    if (!novelId) {
      return res.status(400).json({ message: '缺少书籍ID参数' });
    }

    const result = db.prepare('DELETE FROM favorites WHERE user_id = ? AND novel_id = ?').run(req.user.id, novelId);
    if (result.changes === 0) {
      return res.status(404).json({ message: '收藏记录不存在' });
    }
    db.prepare('UPDATE novels SET favorite_count = MAX(0, favorite_count - 1) WHERE id = ?').run(novelId);

    res.json({ message: '取消收藏成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/favorites/check/ - 检查是否已收藏
router.get('/check', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    const exists = db.prepare('SELECT id FROM favorites WHERE user_id = ? AND novel_id = ?').get(req.user.id, novelId);
    res.json({ is_favorited: !!exists });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
