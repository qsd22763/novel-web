const initSqlJs = require('sql.js');
const path = require('path');
const fs = require('fs');

let _db = null;
let _SQL = null;
let _dbReady = null;

// ── 启动时调用此函数完成异步初始化 ──
async function initDatabase() {
  if (_dbReady) return _dbReady;

  _dbReady = (async () => {
    _SQL = await initSqlJs();

    const dbPath = process.env.SQLITE_PATH || path.join(__dirname, '..', 'data', 'database.sqlite');
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

    if (fs.existsSync(dbPath)) {
      const fileBuffer = fs.readFileSync(dbPath);
      _db = new _SQL.Database(fileBuffer);
    } else {
      _db = new _SQL.Database();
    }

    createTables();
    saveDb();
    return _db;
  })();

  return _dbReady;
}

// ── 同步获取数据库实例（必须在 initDatabase() 之后调用）──
function getDb() {
  if (!_db) {
    throw new Error('数据库未初始化，请确保已调用 initDatabase()');
  }
  return new SqlJsDb(_db);
}

function saveDb() {
  if (_db) {
    const dbPath = process.env.SQLITE_PATH || path.join(__dirname, '..', 'data', 'database.sqlite');
    const data = _db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(dbPath, buffer);
  }
}

// ── 同步包装器（兼容 better-sqlite3 API 风格）──

class SqlJsDb {
  constructor(db) { this._db = db; }

  run(sql, ...params) {
    try {
      const stmt = this._db.prepare(sql);
      if (params.length > 0) stmt.bind(params);
      let stepped = false;
      try { stepped = !!stmt.step(); } catch (_) {}
      stmt.free();
      const modified = this._db.getRowsModified();
      // 获取最后插入的 rowid
      const lastId = this._db.exec("SELECT last_insert_rowid() as id");
      const lid = lastId[0] && lastId[0].values && lastId[0].values[0] ? lastId[0].values[0][0] : -1;
      return { changes: modified, lastInsertRowid: lid };
    } catch (e) {
      // 对于 CREATE/DROP 等语句
      this._db.run(sql);
      return { changes: 0 };
    }
  }

  get(sql, ...params) {
    const stmt = this._db.prepare(sql);
    if (params.length > 0) stmt.bind(params);
    if (!stmt.step()) { stmt.free(); return undefined; }
    const obj = stmt.getAsObject();
    stmt.free();
    return obj;
  }

  all(sql, ...params) {
    const stmt = this._db.prepare(sql);
    if (params.length > 0) stmt.bind(params);
    const results = [];
    while (stmt.step()) results.push(stmt.getAsObject());
    stmt.free();
    return results;
  }

  exec(sql) {
    try { this._db.run(sql); }
    catch (_) { /* sql.js run() may fail on multi-statement, try exec */ try { this._db.exec(sql); } catch (e2) { throw e2; } }
  }

  prepare(sql) { return new StatementWrapper(this._db.prepare(sql)); }

  pragma(sql) { this._db.run(`PRAGMA ${sql}`); }
}

class StatementWrapper {
  constructor(stmt) { this._stmt = stmt; this._bound = false; }

  bind(params) {
    if (Array.isArray(params)) this._stmt.bind(params);
    this._bound = true; return this;
  }

  run(...params) {
    if (params.length > 0) this._stmt.bind(params);
    try { this._stmt.step(); } catch (_) {}
    this._stmt.reset();
    return { changes: 1 };
  }

  get(...params) {
    if (params.length > 0 && !this._bound) this._stmt.bind(params);
    if (!this._stmt.step()) { this._stmt.reset(); return undefined; }
    const obj = this._stmt.getAsObject();
    this._stmt.reset(); return obj;
  }

  all(...params) {
    if (params.length > 0 && !this._bound) this._stmt.bind(params);
    const results = [];
    while (this._stmt.step()) results.push(this._stmt.getAsObject());
    this._stmt.reset(); return results;
  }

  free() { try { this._stmt.free(); } catch(_) {} }
}

function createTables() {
  const db = new SqlJsDb(_db);

  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      email TEXT UNIQUE DEFAULT '',
      password TEXT NOT NULL,
      is_staff INTEGER DEFAULT 0,
      is_vip INTEGER DEFAULT 0,
      vip_expire_date TEXT DEFAULT NULL,
      avatar TEXT DEFAULT '',
      phone TEXT DEFAULT '',
      is_author INTEGER DEFAULT 0,
      pen_name TEXT DEFAULT '',
      bio TEXT DEFAULT '',
      coins INTEGER DEFAULT 0,
      qq_openid TEXT DEFAULT '',
      date_joined TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS admin_user (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      real_name TEXT DEFAULT '',
      is_active INTEGER DEFAULT 1,
      created_at TEXT NOT NULL,
      last_login TEXT DEFAULT NULL
    );

    CREATE TABLE IF NOT EXISTS novels (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      author_name TEXT NOT NULL,
      author_user_id INTEGER DEFAULT NULL,
      cover TEXT DEFAULT '',
      category TEXT NOT NULL,
      description TEXT DEFAULT '',
      tags TEXT DEFAULT '',
      status INTEGER DEFAULT 0,
      audit_status INTEGER DEFAULT 2,
      word_count INTEGER DEFAULT 0,
      view_count INTEGER DEFAULT 0,
      recommend INTEGER DEFAULT 0,
      chapter_count INTEGER DEFAULT 0,
      favorite_count INTEGER DEFAULT 0,
      is_adapted INTEGER DEFAULT 0,
      is_recommended INTEGER DEFAULT 0,
      latest_chapter TEXT DEFAULT '',
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS chapters (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      novel_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      chapter_order INTEGER DEFAULT 0,
      word_count INTEGER DEFAULT 0,
      publish_status INTEGER DEFAULT 1,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS favorites (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      novel_id INTEGER NOT NULL,
      created_at TEXT NOT NULL,
      UNIQUE(user_id, novel_id)
    );

    CREATE TABLE IF NOT EXISTS reading_progress (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      novel_id INTEGER NOT NULL,
      chapter_id INTEGER NOT NULL,
      position INTEGER DEFAULT 0,
      updated_at TEXT NOT NULL,
      UNIQUE(user_id, novel_id)
    );

    CREATE TABLE IF NOT EXISTS bookmarks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      novel_id INTEGER NOT NULL,
      chapter_id INTEGER NOT NULL,
      position INTEGER DEFAULT 0,
      note TEXT DEFAULT '',
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS comments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      novel_id INTEGER NOT NULL,
      content TEXT NOT NULL,
      rating INTEGER DEFAULT 0,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      parent_id INTEGER DEFAULT NULL,
      sort_order INTEGER DEFAULT 0,
      is_active INTEGER DEFAULT 1,
      color TEXT DEFAULT '#3B82F6',
      description TEXT DEFAULT '',
      book_count INTEGER DEFAULT 0,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS advertisements (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      ad_type TEXT DEFAULT 'banner',
      image_url TEXT NOT NULL,
      link_url TEXT DEFAULT '',
      position TEXT NOT NULL,
      is_active INTEGER DEFAULT 1,
      start_time TEXT DEFAULT NULL,
      end_time TEXT DEFAULT NULL,
      click_count INTEGER DEFAULT 0,
      view_count INTEGER DEFAULT 0,
      sort_order INTEGER DEFAULT 0,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS announcements (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      announcement_type TEXT DEFAULT 'notice',
      is_pinned INTEGER DEFAULT 0,
      is_active INTEGER DEFAULT 1,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS checkins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      check_date TEXT NOT NULL,
      reward_coins INTEGER DEFAULT 0,
      created_at TEXT NOT NULL,
      UNIQUE(user_id, check_date)
    );

    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_no TEXT UNIQUE NOT NULL,
      user_id INTEGER NOT NULL,
      plan_type TEXT NOT NULL,
      amount REAL NOT NULL,
      status TEXT DEFAULT 'pending',
      paid_at TEXT DEFAULT NULL,
      expire_at TEXT DEFAULT NULL,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS follows (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      follower_id INTEGER NOT NULL,
      following_name TEXT NOT NULL,
      created_at TEXT NOT NULL,
      UNIQUE(follower_id, following_name)
    );

    CREATE TABLE IF NOT EXISTS ratings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      novel_id INTEGER NOT NULL,
      score INTEGER NOT NULL,
      created_at TEXT NOT NULL,
      UNIQUE(user_id, novel_id)
    );
  `);
}

function now() {
  return new Date().toISOString();
}

module.exports = { getDb, now, saveDb, initDatabase, SqlJsDb };
