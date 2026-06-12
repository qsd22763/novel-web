const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/reading-progress/ - 获取阅读进度列表
router.get('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare(`
      SELECT rp.*, n.title as novel_title, ch.title as chapter_title
      FROM reading_progress rp
      JOIN novels n ON rp.novel_id = n.id
      LEFT JOIN chapters ch ON rp.chapter_id = ch.id
      WHERE rp.user_id = ? ORDER BY rp.updated_at DESC
    `).all(req.user.id);

    res.json(rows.map(r => ({
      id: r.id, user_id: r.user_id, novel_id: r.novel_id, chapter_id: r.chapter_id,
      position: r.position, updated_at: r.updated_at,
      novel_title: r.novel_title, chapter_title: r.chapter_title,
    })));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/reading-progress/ - 更新或创建阅读进度
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id, chapter_id, position } = req.body;
    if (!novel_id || !chapter_id) {
      return res.status(400).json({ detail: '缺少必要参数' });
    }

    const progress = db.prepare(`
      INSERT INTO reading_progress (user_id, novel_id, chapter_id, position, updated_at)
      VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(user_id, novel_id) DO UPDATE SET chapter_id = excluded.chapter_id, position = excluded.position, updated_at = excluded.updated_at
    `).run(req.user.id, novel_id, chapter_id, position || 0, now());

    const saved = db.prepare('SELECT * FROM reading_progress WHERE user_id = ? AND novel_id = ?').get(req.user.id, novel_id);
    res.json({ message: '更新成功', progress: saved });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/reading-progress/get_progress/ - 获取单本小说进度
router.get('/get_progress', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    const progress = db.prepare('SELECT * FROM reading_progress WHERE user_id = ? AND novel_id = ?').get(req.user.id, novelId);

    if (!progress) {
      return res.json({ message: '暂无阅读进度' });
    }
    res.json(progress);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
