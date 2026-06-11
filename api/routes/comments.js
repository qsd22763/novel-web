const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/comments/ - 评论列表
router.get('/', (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    const page = parseInt(req.query.page) || 1;
    const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
    const offset = (page - 1) * pageSize;

    let where = '';
    const params = [];
    if (novelId) {
      where = 'WHERE c.novel_id = ?';
      params.push(novelId);
    }

    const countRow = db.prepare(`SELECT COUNT(*) as total FROM comments c ${where}`).get(...params);
    const rows = db.prepare(`
      SELECT c.*, u.username, u.avatar
      FROM comments c LEFT JOIN users u ON c.user_id = u.id
      ${where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?
    `).all(...params, pageSize, offset);

    res.json({
      count: rows.length,
      next: offset + pageSize < countRow.total ? null : null,
      results: rows.map(r => ({
        id: r.id, user_id: r.user_id, novel_id: r.novel_id, content: r.content,
        rating: r.rating, created_at: r.created_at,
        user: { id: r.user_id, username: r.username, avatar: r.avatar },
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/comments/ - 发表评论
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id, content, rating } = req.body;
    if (!novel_id || !content) {
      return res.status(400).json({ detail: '缺少必要参数' });
    }

    const novel = db.prepare('SELECT id FROM novels WHERE id = ?').get(novel_id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在' });
    }

    const result = db.prepare(
      'INSERT INTO comments (user_id, novel_id, content, rating, created_at) VALUES (?, ?, ?, ?, ?)'
    ).run(req.user.id, novel_id, content, rating || 0, now());

    const comment = db.prepare('SELECT c.*, u.username, u.avatar FROM comments c LEFT JOIN users u ON c.user_id = u.id WHERE c.id = ?').get(result.lastInsertRowid);
    res.status(201).json(comment);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/comments/:id/ - 删除评论
router.delete('/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const comment = db.prepare('SELECT * FROM comments WHERE id = ?').get(req.params.id);
    if (!comment) {
      return res.status(404).json({ detail: '评论不存在' });
    }

    // 只有作者本人或管理员可以删除
    if (comment.user_id !== req.user.id && !req.user.is_staff) {
      return res.status(403).json({ detail: '无权删除此评论' });
    }

    db.prepare('DELETE FROM comments WHERE id = ?').run(req.params.id);
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
