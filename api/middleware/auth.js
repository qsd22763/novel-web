// 认证中间件 - 兼容原 Django Session/Token 方式
// 前端通过 localStorage 存储用户信息，请求时通过 Header 或 Cookie 传递

function authMiddleware(req, res, next) {
  // 支持多种认证方式：
  // 1. Authorization Bearer token
  // 2. X-User-ID header (简化版，用于 Vercel serverless)
  // 3. Cookie session

  let user = null;

  // 方式1: Bearer Token
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    user = getUserByToken(token);
  }

  // 方式2: X-User-ID (兼容前端 localStorage 模式)
  if (!user && req.headers['x-user-id']) {
    user = getUserById(req.headers['x-user-id']);
  }

  // 方式3: Cookie
  if (!user && req.cookies && req.cookies.user_id) {
    user = getUserById(req.cookies.user_id);
  }

  if (user) {
    req.user = user;
  } else {
    req.user = null;
  }

  next();
}

function requireAuth(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ message: '未登录' });
  }
  next();
}

function requireAdmin(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ message: '未登录' });
  }
  if (!req.user.is_staff) {
    return res.status(403).json({ message: '权限不足' });
  }
  next();
}

// 内部工具函数 - 通过简单 token 查找用户
function getUserByToken(token) {
  try {
    const { getDb } = require('../db');
    const db = getDb();
    // token 就是用户的 id（简化方案），实际项目应使用 JWT
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(parseInt(token));
    if (user) {
      delete user.password;
      return user;
    }
    // 也检查管理员
    const admin = db.prepare('SELECT *, 1 as is_staff FROM admin_user WHERE id = ?').get(parseInt(token));
    if (admin) {
      delete admin.password;
      return admin;
    }
    return null;
  } catch {
    return null;
  }
}

function getUserById(id) {
  try {
    const { getDb } = require('../db');
    const db = getDb();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(parseInt(id));
    if (user) {
      delete user.password;
      return user;
    }
    const admin = db.prepare('SELECT *, 1 as is_staff FROM admin_user WHERE id = ?').get(parseInt(id));
    if (admin) {
      delete admin.password;
      return admin;
    }
    return null;
  } catch {
    return null;
  }
}

module.exports = { authMiddleware, requireAuth, requireAdmin, getUserByToken, getUserById };
