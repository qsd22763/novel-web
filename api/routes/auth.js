const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const { getDb, now } = require('../db');
const { requireAuth } = require('../middleware/auth');

// POST /api/auth/login/ - 登录
router.post('/login/', (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ username: ['请输入用户名'], password: ['请输入密码'] });
    }

    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE username = ? OR email = ?').get(username, username);
    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.status(400).json({ non_field_errors: ['用户名或密码错误'] });
    }

    delete user.password;
    res.json({
      message: '登录成功',
      user: formatUser(user),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/auth/admin_login/ - 管理员登录
router.post('/admin_login/', (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) {
      return res.status(400).json({ username: ['请输入管理员账号'], password: ['请输入密码'] });
    }

    const db = getDb();
    const admin = db.prepare('SELECT * FROM admin_user WHERE username = ? AND is_active = 1').get(username);
    if (!admin || !bcrypt.compareSync(password, admin.password)) {
      return res.status(400).json({ non_field_errors: ['管理员账号或密码错误'] });
    }

    db.prepare('UPDATE admin_user SET last_login = ? WHERE id = ?').run(now(), admin.id);

    res.json({
      message: '管理员登录成功',
      user: {
        id: admin.id,
        username: admin.username,
        real_name: admin.real_name || '',
        is_staff: true,
        role: 'admin',
      },
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/auth/register/ - 注册
router.post('/register/', (req, res) => {
  try {
    const { username, email, password, password2 } = req.body;
    const errors = {};

    if (!username || username.length < 3) errors.username = ['用户名至少3个字符'];
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = ['请输入有效邮箱'];
    if (!password || password.length < 6) errors.password = ['密码至少6位'];
    if (password !== password2) errors.password2 = ['两次密码不一致'];

    if (Object.keys(errors).length > 0) {
      return res.status(400).json(errors);
    }

    const db = getDb();

    const existingUser = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?').get(username, email);
    if (existingUser) {
      return res.status(400).json({ non_field_errors: ['用户名或邮箱已被注册'] });
    }

    const hashedPwd = bcrypt.hashSync(password, 10);
    const result = db.prepare(
      'INSERT INTO users (username, email, password, coins, date_joined) VALUES (?, ?, ?, 100, ?)'
    ).run(username, email, hashedPwd, now());

    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);
    delete user.password;

    res.status(201).json({
      message: '注册成功',
      user: formatUser(user),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/auth/logout/ - 登出
router.post('/logout/', (req, res) => {
  res.json({ message: '退出登录成功' });
});

// GET /api/auth/me/ - 当前用户信息
router.get('/me/', (req, res) => {
  if (!req.user) {
    return res.status(401).json({ message: '未登录' });
  }
  res.json(formatUser(req.user));
});

// PUT /api/auth/update_profile/ - 更新资料
router.put('/update_profile/', requireAuth, (req, res) => {
  try {
    const db = getDb();
    const user = req.user;
    const data = req.body;

    const fields = [];
    const params = [];
    if (data.avatar !== undefined) { fields.push('avatar = ?'); params.push(data.avatar); }
    if (data.phone !== undefined) { fields.push('phone = ?'); params.push(data.phone); }
    if (data.email !== undefined) { fields.push('email = ?'); params.push(data.email); }
    if (data.pen_name !== undefined) { fields.push('pen_name = ?'); params.push(data.pen_name); }
    if (data.bio !== undefined) { fields.push('bio = ?'); params.push(data.bio); }

    if (fields.length === 0) {
      return res.status(400).json({ detail: '没有要更新的字段' });
    }

    fields.push('updated_at = ?');
    params.push(now());
    params.push(user.id);

    db.prepare(`UPDATE users SET ${fields.join(', ')} WHERE id = ?`).run(...params);

    const updated = db.prepare('SELECT * FROM users WHERE id = ?').get(user.id);
    delete updated.password;

    res.json({ message: '更新成功', user: formatUser(updated) });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// POST /api/auth/change_password/ - 修改密码
router.post('/change_password/', requireAuth, (req, res) => {
  try {
    const { old_password, new_password } = req.body;
    if (!old_password || !new_password) {
      return res.status(400).json({ old_password: ['请输入旧密码'], new_password: ['请输入新密码'] });
    }
    if (new_password.length < 6) {
      return res.status(400).json({ new_password: ['密码至少6位'] });
    }

    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.user.id);
    if (!bcrypt.compareSync(old_password, user.password)) {
      return res.status(400).json({ old_password: ['旧密码不正确'] });
    }

    db.prepare('UPDATE users SET password = ? WHERE id = ?').run(bcrypt.hashSync(new_password, 10), req.user.id);

    res.json({ message: '密码修改成功' });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

function formatUser(user) {
  return {
    id: user.id,
    username: user.username,
    email: user.email || '',
    avatar: user.avatar || '',
    phone: user.phone || '',
    is_staff: !!user.is_staff,
    is_vip: !!user.is_vip,
    vip_expire_date: user.vip_expire_date || null,
    is_author: !!user.is_author,
    pen_name: user.pen_name || '',
    bio: user.bio || '',
    coins: user.coins || 0,
    date_joined: user.date_joined,
  };
}

module.exports = router;
