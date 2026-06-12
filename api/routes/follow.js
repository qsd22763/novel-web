const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/follow/ - 我的关注列表
router.get('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const page = parseInt(req.query.page) || 1;
    const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
    const offset = (page - 1) * pageSize;

    const countRow = db.prepare('SELECT COUNT(*) as total FROM follows WHERE follower_id = ?').get(req.user.id);
    const rows = db.prepare(
      'SELECT * FROM follows WHERE follower_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?'
    ).all(req.user.id, pageSize, offset);

    res.json({
      count: rows.length,
      next: offset + pageSize < countRow.total ? null : null,
      results: rows,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/follow/ - 关注作者
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { author_name } = req.body;
    if (!author_name) {
      return res.status(400).json({ detail: '请指定要关注的作者' });
    }

    const exists = db.prepare('SELECT id FROM follows WHERE follower_id = ? AND following_name = ?')
      .get(req.user.id, author_name);
    if (exists) {
      return res.status(400).json({ message: '已关注该作者' });
    }

    db.prepare('INSERT INTO follows (follower_id, following_name, created_at) VALUES (?, ?, ?)')
      .run(req.user.id, author_name, now());

    res.status(201).json({ message: '关注成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/follow/ - 取消关注
router.delete('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { author_name } = req.body;
    if (!author_name) {
      return res.status(400).json({ detail: '请指定要取消关注的作者' });
    }

    const result = db.prepare('DELETE FROM follows WHERE follower_id = ? AND following_name = ?')
      .run(req.user.id, author_name);

    if (result.changes === 0) {
      return res.status(404).json({ message: '未找到关注记录' });
    }

    res.json({ message: '取消关注成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/follow/check/ - 检查是否已关注
router.get('/check', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const authorName = req.query.author_name;
    const exists = db.prepare('SELECT id FROM follows WHERE follower_id = ? AND following_name = ?')
      .get(req.user.id, authorName);
    res.json({ is_following: !!exists });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
