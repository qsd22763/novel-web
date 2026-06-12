const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// POST /api/checkin/do_checkin/ - 执行签到
router.post('/do_checkin/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const today = new Date().toISOString().split('T')[0];

    // 检查是否已签到
    const existing = db.prepare('SELECT id FROM checkins WHERE user_id = ? AND check_date = ?').get(req.user.id, today);
    if (existing) {
      return res.status(400).json({ message: '今天已经签过了，明天再来吧~' });
    }

    // 获取奖励配置（默认10币）
    const reward = 10;

    db.prepare('BEGIN TRANSACTION');

    // 插入签到记录
    db.prepare('INSERT INTO checkins (user_id, check_date, reward_coins, created_at) VALUES (?, ?, ?, ?)')
      .run(req.user.id, today, reward, now());

    // 增加用户虚拟币
    db.prepare('UPDATE users SET coins = coins + ? WHERE id = ?').run(reward, req.user.id);

    db.prepare('COMMIT');

    // 查询连续签到天数
    const streakRows = db.prepare(
      `SELECT check_date FROM checkins WHERE user_id = ? ORDER BY check_date DESC LIMIT 7`
    ).all(req.user.id);

    let streak = 0;
    const todayDate = new Date(today);
    for (const r of streakRows) {
      const expected = new Date(todayDate);
      expected.setDate(expected.getDate() - streak);
      if (r.check_date === expected.toISOString().split('T')[0]) {
        streak++;
      } else {
        break;
      }
    }

    const user = db.prepare('SELECT coins FROM users WHERE id = ?').get(req.user.id);

    res.json({
      message: '签到成功！',
      reward_coins: reward,
      current_coins: user.coins,
      continuous_days: streak,
    });
  } catch (e) {
    const db = getDb();
    db.prepare('ROLLBACK').run();
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/checkin/status/ - 签到状态
router.get('/status/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const today = new Date().toISOString().split('T')[0];

    const todayCheckin = db.prepare('SELECT * FROM checkins WHERE user_id = ? AND check_date = ?').get(req.user.id, today);

    // 最近7天签到记录
    const recentCheckins = db.prepare(
      `SELECT check_date, reward_coins FROM checkins WHERE user_id = ? ORDER BY check_date DESC LIMIT 30`
    ).all(req.user.id);

    // 本月签到天数
    const monthStart = new Date().toISOString().slice(0, 7) + '-01';
    const monthlyCount = db.prepare(
      "SELECT COUNT(*) as cnt FROM checkins WHERE user_id = ? AND check_date >= ?"
    ).get(req.user.id, monthStart).cnt;

    // 总签到次数
    const totalCount = db.prepare('SELECT COUNT(*) as cnt FROM checkins WHERE user_id = ?').get(req.user.id).cnt;

    res.json({
      checked_today: !!todayCheckin,
      today_reward: todayCheckin ? todayCheckin.reward_coins : 0,
      recent_checkins: recentCheckins.map(r => ({ date: r.check_date, coins: r.reward_coins })),
      monthly_count: monthlyCount,
      total_count: totalCount,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
