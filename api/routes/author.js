const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// ── 作者小说管理 ──

// GET /api/author/novels/ - 获取我的小说列表
router.get('/novels/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const rows = db.prepare(
      'SELECT * FROM novels WHERE author_user_id = ? ORDER BY updated_at DESC'
    ).all(req.user.id);

    res.json({ results: rows });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/author/novels/ - 创建小说
router.post('/novels/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { title, author_name, cover, category, description, tags } = req.body;
    if (!title || !author_name || !category) {
      return res.status(400).json({ detail: '标题、作者名和分类为必填项' });
    }

    const result = db.prepare(`
      INSERT INTO novels (title, author_name, cover, category, description, tags, audit_status, status, created_at, updated_at, author_user_id)
      VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?, ?, ?)
    `).run(title, author_name, cover || '', category, description || '', tags || '', now(), now(), req.user.id);

    const novel = db.prepare('SELECT * FROM novels WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(novel);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// PATCH /api/author/novels/:id/ - 更新小说
router.patch('/novels/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(req.params.id, req.user.id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在或无权操作' });
    }

    const allowedFields = ['title', 'cover', 'category', 'description', 'tags', 'status'];
    const fields = [];
    const params = [];
    for (const field of allowedFields) {
      if (req.body[field] !== undefined) {
        fields.push(`${field} = ?`);
        params.push(req.body[field]);
      }
    }
    if (fields.length === 0) {
      return res.status(400).json({ detail: '没有可更新的字段' });
    }
    fields.push('updated_at = ?');
    params.push(now());
    params.push(req.params.id);

    db.prepare(`UPDATE novels SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    const updated = db.prepare('SELECT * FROM novels WHERE id = ?').get(req.params.id);
    res.json(updated);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/author/novels/:id/ - 删除小说
router.delete('/novels/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(req.params.id, req.user.id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在或无权操作' });
    }

    db.prepare('DELETE FROM chapters WHERE novel_id = ?').run(req.params.id);
    db.prepare('DELETE FROM novels WHERE id = ?').run(req.params.id);
    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// ── 作者章节管理 ──

// GET /api/author/chapters/ - 获取某小说的章节列表（含草稿）
router.get('/chapters/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const novelId = req.query.novel_id;
    if (!novelId) {
      return res.status(400).json({ detail: '缺少 novel_id 参数' });
    }

    const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(novelId, req.user.id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在或无权操作' });
    }

    const chapters = db.prepare(
      'SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_order'
    ).all(novelId);

    res.json({ results: chapters, count: chapters.length });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/author/chapters/ - 创建章节
router.post('/chapters/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { novel_id, title, content, publish_status } = req.body;
    if (!novel_id || !title || !content) {
      return res.status(400).json({ detail: '缺少必要参数' });
    }

    const novel = db.prepare('SELECT * FROM novels WHERE id = ? AND author_user_id = ?').get(novel_id, req.user.id);
    if (!novel) {
      return res.status(404).json({ detail: '小说不存在或无权操作' });
    }

    const maxOrder = db.prepare('SELECT COALESCE(MAX(chapter_order), 0) as mx FROM chapters WHERE novel_id = ?').get(novel_id).mx;
    const t = now();

    const result = db.prepare(`
      INSERT INTO chapters (novel_id, title, content, chapter_order, word_count, publish_status, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(novel_id, title, content, maxOrder + 1, content.length, publish_status || 0, t, t);

    // 更新小说章节计数和最新章节
    db.prepare(`
      UPDATE novels SET chapter_count = (SELECT COUNT(*) FROM chapters WHERE novel_id = ?),
        latest_chapter = ?, updated_at = ? WHERE id = ?
    `).run(novel_id, title, t, novel_id);

    const chapter = db.prepare('SELECT * FROM chapters WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json(chapter);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// PATCH /api/author/chapters/:id/ - 更新章节
router.patch('/chapters/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const chapter = db.prepare(`
      SELECT c.* FROM chapters c JOIN novels n ON c.novel_id = n.id
      WHERE c.id = ? AND n.author_user_id = ?
    `).get(req.params.id, req.user.id);

    if (!chapter) {
      return res.status(404).json({ detail: '章节不存在或无权操作' });
    }

    const allowedFields = ['title', 'content', 'publish_status', 'chapter_order'];
    const fields = [];
    const params = [];
    for (const field of allowedFields) {
      if (req.body[field] !== undefined) {
        fields.push(`${field} = ?`);
        if (field === 'content') {
          params.push(req.body[field]);
          fields.push('word_count = ?');
          params.push(req.body[field].length);
        } else {
          params.push(req.body[field]);
        }
      }
    }
    if (fields.length === 0) {
      return res.status(400).json({ detail: '没有可更新的字段' });
    }
    fields.push('updated_at = ?');
    params.push(now());
    params.push(req.params.id);

    db.prepare(`UPDATE chapters SET ${fields.join(', ')} WHERE id = ?`).run(...params);
    const updated = db.prepare('SELECT * FROM chapters WHERE id = ?').get(req.params.id);
    res.json(updated);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/author/chapters/:id/ - 删除章节
router.delete('/chapters/:id/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const chapter = db.prepare(`
      SELECT c.*, c.novel_id FROM chapters c JOIN novels n ON c.novel_id = n.id
      WHERE c.id = ? AND n.author_user_id = ?
    `).get(req.params.id, req.user.id);

    if (!chapter) {
      return res.status(404).json({ detail: '章节不存在或无权操作' });
    }

    db.prepare('DELETE FROM chapters WHERE id = ?').run(req.params.id);
    db.prepare(`
      UPDATE novels SET chapter_count = (SELECT COUNT(*) FROM chapters WHERE novel_id = ?),
        updated_at = ? WHERE id = ?
    `).run(chapter.novel_id, now(), chapter.novel_id);

    res.json({ message: '删除成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
