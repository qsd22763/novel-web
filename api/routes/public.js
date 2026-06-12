const express = require('express');
const router = express.Router();
const { getDb } = require('../db');

// GET /api/public/advertisements/ - 公开广告
router.get('/advertisements/', (req, res) => {
  try {
    const db = getDb();
    const position = req.query.position;
    let rows;
    if (position) {
      rows = db.prepare('SELECT * FROM advertisements WHERE is_active=1 AND position=? ORDER BY sort_order').all(position);
    } else {
      rows = db.prepare('SELECT * FROM advertisements WHERE is_active=1 ORDER BY sort_order').all();
    }
    res.json({ count: rows.length, results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/public/announcements/ - 公开公告
router.get('/announcements/', (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare('SELECT * FROM announcements WHERE is_active=1 ORDER BY is_pinned DESC, created_at DESC').all();
    res.json({ count: rows.length, results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
