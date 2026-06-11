const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');

// GET /api/chapters/:id/ - 章节详情（含上下章）
router.get('/:id/', (req, res) => {
  try {
    const db = getDb();
    const chapter = db.prepare('SELECT c.*, n.title as novel_title, n.id as novel_id FROM chapters c JOIN novels n ON c.novel_id = n.id WHERE c.id = ?').get(req.params.id);

    if (!chapter) {
      return res.status(404).json({ detail: '章节不存在' });
    }

    // 更新阅读量
    db.prepare('UPDATE novels SET view_count = view_count + 1 WHERE id = ?').run(chapter.novel_id);

    // 获取前后章节
    const allChapters = db.prepare('SELECT id, title FROM chapters WHERE novel_id = ? AND publish_status = 1 ORDER BY chapter_order').all(chapter.novel_id);
    const currentIndex = allChapters.findIndex(c => c.id === parseInt(req.params.id));

    const prevChapter = currentIndex > 0 ? allChapters[currentIndex - 1] : null;
    const nextChapter = currentIndex < allChapters.length - 1 ? allChapters[currentIndex + 1] : null;

    res.json({
      id: chapter.id,
      novel_id: chapter.novel_id,
      title: chapter.title,
      content: chapter.content,
      chapter_order: chapter.chapter_order,
      word_count: chapter.word_count,
      created_at: chapter.created_at,
      novel_title: chapter.novel_title,
      prev_chapter: prevChapter ? { id: prevChapter.id, title: prevChapter.title } : null,
      next_chapter: nextChapter ? { id: nextChapter.id, title: nextChapter.title } : null,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
