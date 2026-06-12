const express = require('express');
const router = express.Router();
const { getDb } = require('../db');

// ── 注意：具体路由必须在 :id 参数路由之前定义 ──

// GET /api/novels/ - 小说列表（分页、分类、搜索、排序）
router.get('/', (req, res) => {
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
  } catch (e) {
    console.error('小说列表查询错误:', e.message);
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/novels/search/ - 搜索（必须在 :id 之前）
router.get('/search', (req, res) => {
  try {
    const db = getDb();
    const q = req.query.q || '';
    const page = parseInt(req.query.page) || 1;
    const pageSize = Math.min(parseInt(req.query.page_size) || 20, 100);
    const offset = (page - 1) * pageSize;

    const countRow = db.prepare(
      "SELECT COUNT(*) as total FROM novels WHERE audit_status=2 AND status!=2 AND (title LIKE ? OR author_name LIKE ?)"
    ).get(`%${q}%`, `%${q}%`);

    const rows = db.prepare(
      "SELECT *, (SELECT title FROM chapters WHERE novel_id=novels.id ORDER BY chapter_order DESC LIMIT 1) as latest_chapter \
       FROM novels WHERE audit_status=2 AND status!=2 AND (title LIKE ? OR author_name LIKE ?) ORDER BY updated_at DESC LIMIT ? OFFSET ?"
    ).all(`%${q}%`, `%${q}%`, pageSize, offset);

    res.json({
      count: rows.length,
      next: offset + pageSize < countRow.total ? null : null,
      results: rows.map(r => ({
        id: r.id, title: r.title, author: r.author_name, cover: r.cover, description: r.description,
        category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count,
        updated_at: r.updated_at, latest_chapter: r.latest_chapter,
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/novels/recommend/ - 推荐（必须在 :id 之前）
router.get('/recommend', (req, res) => {
  try {
    const db = getDb();
    const limit = Math.min(parseInt(req.query.limit) || 10, 50);
    const rows = db.prepare(
      "SELECT *, (SELECT title FROM chapters WHERE novel_id=novels.id ORDER BY chapter_order DESC LIMIT 1) as latest_chapter \
       FROM novels WHERE audit_status=2 AND status!=2 ORDER BY view_count DESC LIMIT ?"
    ).all(limit);

    res.json(rows.map(r => ({
      id: r.id, title: r.title, author: r.author_name, cover: r.cover, description: r.description,
      category: r.category, status: r.status, word_count: r.word_count, view_count: r.view_count,
      updated_at: r.updated_at, latest_chapter: r.latest_chapter,
    })));
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/novels/category_stats/ - 分类统计（必须在 :id 之前）
router.get('/category_stats', (req, res) => {
  try {
    const db = getDb();
    const cats = db.prepare("SELECT name FROM categories WHERE is_active=1 ORDER BY sort_order").all();
    const stats = {};
    for (const cat of cats) {
      stats[cat.name] = db.prepare('SELECT COUNT(*) as cnt FROM novels WHERE category=? AND audit_status=2 AND status!=2').get(cat.name).cnt;
    }
    res.json(stats);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/novels/:id/ - 小说详情（参数路由放最后）
router.get('/:id/', (req, res) => {
  try {
    const db = getDb();
    const row = db.prepare(`
      SELECT n.*, (SELECT COUNT(*) FROM chapters WHERE novel_id=n.id) as chapter_count,
        (SELECT COUNT(*) FROM comments WHERE novel_id=n.id) as comment_count,
        COALESCE((SELECT AVG(score) FROM ratings WHERE novel_id=n.id),0) as avg_rating
      FROM novels n WHERE n.id=?
    `).get(req.params.id);

    if (!row) return res.status(404).json({ detail: '小说不存在' });

    res.json({
      id: row.id, title: row.title, author: row.author_name, cover: row.cover,
      description: row.description, category: row.category, status: row.status,
      word_count: row.word_count, view_count: row.view_count, chapter_count: row.chapter_count,
      comment_count: row.comment_count, avg_rating: parseFloat(row.avg_rating),
      created_at: row.created_at, updated_at: row.updated_at,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/novels/:id/chapters/ - 章节列表
router.get('/:id/chapters/', (req, res) => {
  try {
    const db = getDb();
    const novel = db.prepare('SELECT * FROM novels WHERE id=?').get(req.params.id);
    if (!novel) return res.status(404).json({ detail: '小说不存在' });

    const chapters = db.prepare(
      'SELECT id,title,chapter_order,word_count,created_at FROM chapters WHERE novel_id=? AND publish_status=1 ORDER BY chapter_order'
    ).all(req.params.id);

    res.json({ novel_id: novel.id, novel_title: novel.title, chapter_count: chapters.length, chapters });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
