const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// GET /api/rating/ - 获取某小说的评分列表
router.get('/', (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    if (!novelId) {
      return res.status(400).json({ detail: '缺少 novel_id 参数' });
    }

    const rows = db.prepare(`
      SELECT r.*, u.username, u.avatar
      FROM ratings r LEFT JOIN users u ON r.user_id = u.id
      WHERE r.novel_id = ? ORDER BY r.created_at DESC
    `).all(novelId);

    // 计算平均分
    const avgRow = db.prepare('SELECT AVG(score) as avg, COUNT(*) as cnt FROM ratings WHERE novel_id = ?').get(novelId);

    res.json({
      average_score: parseFloat(avgRow.avg?.toFixed(1)) || 0,
      rating_count: avgRow.cnt || 0,
      results: rows.map(r => ({
        id: r.id, user_id: r.user_id, novel_id: r.novel_id, score: r.score, created_at: r.created_at,
        user: { username: r.username, avatar: r.avatar },
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/rating/ - 提交评分
router.post('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id, score } = req.body;
    if (!novel_id || !score) {
      return res.status(400).json({ detail: '缺少必要参数' });
    }
    if (score < 1 || score > 5) {
      return res.status(400).json({ detail: '评分必须在1-5之间' });
    }

    const novel = db.prepare('SELECT id FROM novels WHERE id = ?').get(novel_id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在' });
    }

    // UPSERT
    const existing = db.prepare('SELECT id FROM ratings WHERE user_id = ? AND novel_id = ?').get(req.user.id, novel_id);

    if (existing) {
      db.prepare('UPDATE ratings SET score = ?, created_at = ? WHERE id = ?').run(score, now(), existing.id);
    } else {
      db.prepare('INSERT INTO ratings (user_id, novel_id, score, created_at) VALUES (?, ?, ?, ?)')
        .run(req.user.id, novel_id, score, now());
    }

    // 重新计算平均分
    const avgRow = db.prepare('SELECT AVG(score) as avg FROM ratings WHERE novel_id = ?').get(novel_id);

    res.json({
      message: existing ? '评分更新成功' : '评分提交成功',
      average_score: parseFloat(avgRow.avg?.toFixed(1)) || 0,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/rating/my_rating/ - 我对某小说的评分
router.get('/my_rating', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    const rating = db.prepare('SELECT * FROM ratings WHERE user_id = ? AND novel_id = ?').get(req.user.id, novelId);

    if (!rating) {
      return res.json({ message: '暂未评分' });
    }
    res.json(rating);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/rating/ - 删除评分
router.delete('/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id } = req.body;
    if (!novel_id) {
      return res.status(400).json({ detail: '缺少 novel_id 参数' });
    }

    const result = db.prepare('DELETE FROM ratings WHERE user_id = ? AND novel_id = ?').run(req.user.id, novel_id);
    if (result.changes === 0) {
      return res.status(404).json({ message: '评分不存在' });
    }
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
