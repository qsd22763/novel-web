const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/bookmarks/ - 书签列表
router.get('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare(`
      SELECT b.*, n.title as novel_title, ch.title as chapter_title
      FROM bookmarks b
      JOIN novels n ON b.novel_id = n.id
      LEFT JOIN chapters ch ON b.chapter_id = ch.id
      WHERE b.user_id = ? ORDER BY b.created_at DESC
    `).all(req.user.id);

    res.json(rows.map(r => ({
      id: r.id, user_id: r.user_id, novel_id: r.novel_id, chapter_id: r.chapter_id,
      position: r.position, note: r.note, created_at: r.created_at,
      novel_title: r.novel_title, chapter_title: r.chapter_title,
    })));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/bookmarks/ - 添加书签
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id, chapter_id, position, note } = req.body;
    if (!novel_id || !chapter_id) {
      return res.status(400).json({ detail: '缺少必要参数' });
    }

    const result = db.prepare(
      'INSERT INTO bookmarks (user_id, novel_id, chapter_id, position, note, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    ).run(req.user.id, novel_id, chapter_id, position || 0, note || '', now());

    const bookmark = db.prepare('SELECT * FROM bookmarks WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(bookmark);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/bookmarks/:id/ - 删除书签
router.delete('/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const result = db.prepare('DELETE FROM bookmarks WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id);
    if (result.changes === 0) {
      return res.status(404).json({ detail: '书签不存在' });
    }
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
