const express = require('express');
const router = express.Router();
const { getDb, now } = require('../db');
const { v4: uuidv4 } = require('uuid');
const { requireAuth } = require('../middleware/auth');

// GET /api/membership/plans/ - 会员套餐列表
router.get('/plans/', (req, res) => {
  try {
    const plans = [
      { id: 'monthly', name: '月卡会员', price: 18.00, duration: 30, benefits: ['免广告阅读', '专属书架', '优先客服'] },
      { id: 'quarterly', name: '季卡会员', price: 45.00, duration: 90, benefits: ['免广告阅读', '专属书架', '优先客服', '每月赠送200币'] },
      { id: 'yearly', name: '年卡会员', price: 148.00, duration: 365, benefits: ['免广告阅读', '专属书架', '优先客服', '每月赠送300币', '生日特权'] },
    ];
    res.json(plans);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// GET /api/membership/my_status/ - 我的会员状态
router.get('/my_status/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const user = db.prepare('SELECT is_vip, vip_expire_date, coins FROM users WHERE id = ?').get(req.user.id);

    const isVip = user.is_vip === 1 &&
      (!user.vip_expire_date || new Date(user.vip_expire_date) > new Date());

    // 最近订单
    const orders = db.prepare(
      'SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 5'
    ).all(req.user.id);

    res.json({
      is_vip: isVip,
      vip_expire_date: user.vip_expire_date,
      coins: user.coins,
      recent_orders: orders.map(o => ({
        id: o.id, order_no: o.order_no, plan_type: o.plan_type,
        amount: o.amount, status: o.status, created_at: o.created_at,
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/membership/purchase/ - 创建订单（模拟）
router.post('/purchase/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const { plan_type } = req.body;
    const plans = { monthly: 18.00, quarterly: 45.00, yearly: 148.00 };
    const durations = { monthly: 30, quarterly: 90, yearly: 365 };

    if (!plans[plan_type]) {
      return res.status(400).json({ detail: '无效的套餐类型' });
    }

    const orderNo = uuidv4().replace(/-/g, '').substring(0, 32);
    const amount = plans[plan_type];

    const result = db.prepare(
      'INSERT INTO orders (order_no, user_id, plan_type, amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?)'
    ).run(orderNo, req.user.id, plan_type, amount, 'pending', now());

    // 模拟自动支付成功
    const expireAt = new Date();
    expireAt.setDate(expireAt.getDate() + durations[plan_type]);

    db.prepare('UPDATE orders SET status = ?, paid_at = ?, expire_at = ? WHERE id = ?')
      .run('paid', now(), expireAt.toISOString(), result.lastInsertRowid);

    // 更新用户VIP状态
    db.prepare('UPDATE users SET is_vip = 1, vip_expire_date = ? WHERE id = ?')
      .run(expireAt.toISOString(), req.user.id);

    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(result.lastInsertRowid);
    res.status(201).json({
      message: '购买成功！',
      order,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
