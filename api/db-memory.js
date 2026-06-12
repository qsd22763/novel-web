// ──────────────────────────────────────────────
//  db-memory.js — 纯 JavaScript 内存数据库
//  替代 sql.js (WASM SQLite)，解决 Vercel Serverless 部署问题
//  接口与原 db.js 完全兼容
// ──────────────────────────────────────────────

let _dbInstance = null;
let _initialized = false;

// ── 表结构定义（列名 -> 默认值） ──
const SCHEMAS = {
  users: {
    id: null, username: '', email: '', password: '',
    is_staff: 0, is_vip: 0, vip_expire_date: null,
    avatar: '', phone: '', is_author: 0, pen_name: '', bio: '',
    coins: 0, qq_openid: '', date_joined: ''
  },
  admin_user: {
    id: null, username: '', password: '', real_name: '',
    is_active: 1, created_at: '', last_login: null
  },
  novels: {
    id: null, title: '', author_name: '', author_user_id: null,
    cover: '', category: '', description: '', tags: '',
    status: 0, audit_status: 2, word_count: 0, view_count: 0,
    recommend: 0, chapter_count: 0, favorite_count: 0,
    is_adapted: 0, is_recommended: 0, latest_chapter: '',
    created_at: '', updated_at: ''
  },
  chapters: {
    id: null, novel_id: null, title: '', content: '',
    chapter_order: 0, word_count: 0, publish_status: 1,
    created_at: '', updated_at: ''
  },
  favorites: { id: null, user_id: null, novel_id: null, created_at: '' },
  reading_progress: {
    id: null, user_id: null, novel_id: null, chapter_id: null,
    position: 0, updated_at: ''
  },
  bookmarks: {
    id: null, user_id: null, novel_id: null, chapter_id: null,
    position: 0, note: '', created_at: ''
  },
  comments: {
    id: null, user_id: null, novel_id: null, content: '',
    rating: 0, created_at: ''
  },
  categories: {
    id: null, name: '', parent_id: null, sort_order: 0,
    is_active: 1, color: '#3B82F6', description: '',
    book_count: 0, created_at: ''
  },
  advertisements: {
    id: null, title: '', ad_type: 'banner', image_url: '',
    link_url: '', position: '', is_active: 1,
    start_time: null, end_time: null, click_count: 0,
    view_count: 0, sort_order: 0, created_at: '', updated_at: ''
  },
  announcements: {
    id: null, title: '', content: '', announcement_type: 'notice',
    is_pinned: 0, is_active: 1, created_at: '', updated_at: ''
  },
  checkins: {
    id: null, user_id: null, check_date: '',
    reward_coins: 0, created_at: ''
  },
  orders: {
    id: null, order_no: '', user_id: null, plan_type: '',
    amount: 0, status: 'pending', paid_at: null, expire_at: null,
    created_at: ''
  },
  follows: { id: null, follower_id: null, following_name: '', created_at: '' },
  ratings: { id: null, user_id: null, novel_id: null, score: 0, created_at: '' }
};

// ── 自增 ID 计数器 ──
const _autoInc = {};

function nextId(table) {
  if (!_autoInc[table]) _autoInc[table] = 0;
  return ++_autoInc[table];
}

// ══════════════════════════════════════════════
//  内存数据库类
// ══════════════════════════════════════════════
class MemoryDatabase {
  constructor() {
    this.tables = {};
    this._transactionActive = false;
    this._transactionSnapshot = null;
    for (const tbl of Object.keys(SCHEMAS)) {
      this.tables[tbl] = [];
    }
  }

  // ── 创建表（初始化时调用）──
  exec(sql) {
    const stmts = splitStatements(sql);
    for (const s of stmts) {
      const trimmed = s.trim();
      if (!trimmed || trimmed.startsWith('--')) continue;
      if (/^CREATE\s+TABLE/i.test(trimmed)) {
        // 表已通过 SCHEMAS 定义，忽略 CREATE TABLE
        continue;
      }
      // 处理多行 INSERT（来自 exec 的批量插入）
      if (/^INSERT\s+INTO/i.test(trimmed)) {
        this._executeInsert(trimmed, []);
      }
    }
  }

  // ── 直接执行 SQL（返回 changes / lastInsertRowid）──
  run(sql, ...params) {
    const upper = sql.trim().toUpperCase();
    if (upper.startsWith('INSERT')) {
      return this._executeInsert(sql, params);
    } else if (upper.startsWith('UPDATE')) {
      return this._executeUpdate(sql, params);
    } else if (upper.startsWith('DELETE')) {
      return this._executeDelete(sql, params);
    } else if (upper.startsWith('CREATE') || upper.startsWith('DROP') || upper.startsWith('ALTER') ||
               upper === 'BEGIN TRANSACTION' || upper === 'COMMIT' || upper === 'ROLLBACK') {
      if (upper === 'BEGIN TRANSACTION') { this._transactionActive = true; this._transactionSnapshot = JSON.stringify(this.tables); }
      else if (upper === 'COMMIT') { this._transactionActive = false; this._transactionSnapshot = null; }
      else if (upper === 'ROLLBACK') { this._transactionActive = false; if (this._transactionSnapshot) { this.tables = JSON.parse(this._transactionSnapshot); this._transactionSnapshot = null; } }
      return { changes: 0 };
    }
    return { changes: 0 };
  }

  // ── 查询单行 ──
  get(sql, ...params) {
    const rows = this._executeSelect(sql, params);
    return rows.length > 0 ? rows[0] : undefined;
  }

  // ── 查询多行 ──
  all(sql, ...params) {
    return this._executeSelect(sql, params);
  }

  // ── 准备语句 ──
  prepare(sql) {
    return new MemoryStatement(this, sql);
  }

  // ══════════════════════════════════════════════
  //  内部：SQL 解析与执行
  // ══════════════════════════════════════════════

  _getTable(name) {
    const key = name.toLowerCase();
    if (!this.tables[key]) throw new Error(`表不存在: ${name}`);
    return { data: this.tables[key], schema: SCHEMAS[key] };
  }

  _executeInsert(sql, params) {
    const info = parseInsert(sql);
    const { data, schema } = this._getTable(info.table);
    const row = { ...schema };

    // 解析 VALUES 子句中的每个值（区分 ? 占位符和字面量）
    // 注意：需要正确处理括号嵌套，且在 ON CONFLICT 之前停止
    const valuesMatch = sql.match(/VALUES\s*\(/i);
    const rawValues = valuesMatch ? extractBalancedParen(sql, valuesMatch.index + valuesMatch[0].length - 1) : '';
    const valueTokens = parseValueTokens(rawValues);

    let paramIdx = 0;
    for (let i = 0; i < info.columns.length; i++) {
      const col = info.columns[i];
      let val;
      if (i < valueTokens.length && valueTokens[i].type === 'param') {
        val = paramIdx < params.length ? params[paramIdx++] : null;
      } else if (i < valueTokens.length && valueTokens[i].type === 'literal') {
        val = valueTokens[i].value;
      } else {
        val = paramIdx < params.length ? params[paramIdx++] : null;
      }
      if (val === undefined) val = null;
      row[col] = val;
    }

    // 自增 ID
    if (!row.id || row.id === null) {
      row.id = nextId(info.table);
    } else if (typeof row.id === 'string') {
      row.id = parseInt(row.id) || nextId(info.table);
    }

    // UPSERT: ON CONFLICT DO UPDATE
    if (info.upsert) {
      const conflictCols = info.upsert.conflictColumns;
      const existingIdx = data.findIndex(r => conflictCols.every(c => String(r[c]) === String(row[c])));
      if (existingIdx >= 0) {
        // UPDATE existing row: SET col = excluded.col → 取新行对应列的值
        const updateCols = info.upsert.updateColumns;
        for (const uc of updateCols) {
          // uc 是 SET 子句中 = 左边的列名，值来自 row（即 excluded）的同名字段
          if (row.hasOwnProperty(uc)) {
            data[existingIdx][uc] = row[uc];
          }
        }
        return { changes: 1, lastInsertRowid: data[existingIdx].id };
      }
    }

    // INSERT OR IGNORE: 检查唯一约束
    if (info.orIgnore) {
      const uniqueKeys = getUniqueKeys(info.table);
      for (const uk of uniqueKeys) {
        const exists = data.some(r => uk.every(c => String(r[c]) === String(row[c])));
        if (exists) return { changes: 0, lastInsertRowid: row.id };
      }
    }

    data.push({ ...row });
    return { changes: 1, lastInsertRowid: row.id };
  }

  _executeUpdate(sql, params) {
    const info = parseUpdate(sql, params);
    const { data } = this._getTable(info.table);
    let changes = 0;

    // 按 SQL 中 ? 出现顺序分割参数：SET 子句的参数在前，WHERE 的在后
    const setMatch = sql.match(/SET\s+(.+?)\s+WHERE/is);
    const setClause = setMatch ? setMatch[1] : '';
    const setParamCount = (setClause.match(/\?/g) || []).length;
    const setParams = params.slice(0, setParamCount);
    const whereParams = params.slice(setParamCount);

    const rowsToUpdate = data.filter(r => matchWhere(r, info.where, whereParams));
    for (const row of rowsToUpdate) {
      for (const [col, expr] of info.setters) {
        row[col] = evaluateExpression(expr, row, setParams);
      }
      changes++;
    }

    return { changes, lastInsertRowid: -1 };
  }

  _executeDelete(sql, params) {
    const info = parseDelete(sql, params);
    const { data } = this._getTable(info.table);
    const beforeLen = data.length;
    const remaining = data.filter(r => !matchWhere(r, info.where, info.whereParams));
    data.length = 0;
    data.push(...remaining);
    return { changes: beforeLen - data.length, lastInsertRowid: -1 };
  }

  _executeSelect(sql, params) {
    return parseAndExecuteSelect(this, sql, params);
  }
}

// ══════════════════════════════════════════════
//  语句对象（prepare 返回）
// ══════════════════════════════════════════════
class MemoryStatement {
  constructor(db, sql) {
    this.db = db;
    this.sql = sql;
    this._boundParams = [];
    this._bound = false;
  }

  bind(params) {
    if (Array.isArray(params)) {
      this._boundParams = params.slice();
    }
    this._bound = true;
    return this;
  }

  run(...params) {
    const allParams = params.length > 0 ? params : this._boundParams;
    return this.db.run(this.sql, ...allParams);
  }

  get(...params) {
    const allParams = params.length > 0 ? params : this._boundParams;
    return this.db.get(this.sql, ...allParams);
  }

  all(...params) {
    const allParams = params.length > 0 ? params : this._boundParams;
    return this.db.all(this.sql, ...allParams);
  }

  free() {}
}

// ══════════════════════════════════════════════
//  SQL 解析器
// ══════════════════════════════════════════════

// 解析 VALUES 子句为 token 数组，区分 ? 占位符和字面量值
function parseValueTokens(valuesStr) {
  const tokens = [];
  let current = '';
  let inString = false;
  let strChar = '';
  for (let i = 0; i < valuesStr.length; i++) {
    const ch = valuesStr[i];
    if ((ch === "'" || ch === '"') && !inString) { inString = true; strChar = ch; current += ch; continue; }
    if (ch === strChar && inString) { inString = false; current += ch; continue; }
    if (ch === ',' && !inString) {
      tokens.push(parseSingleValueToken(current.trim()));
      current = '';
    } else {
      current += ch;
    }
  }
  if (current.trim()) tokens.push(parseSingleValueToken(current.trim()));
  return tokens;
}

function parseSingleValueToken(token) {
  const t = token.trim();
  if (t === '?') return { type: 'param' };
  // 字符串字面量
  if ((t.startsWith("'") && t.endsWith("'")) || (t.startsWith('"') && t.endsWith('"'))) {
    return { type: 'literal', value: t.slice(1, -1) };
  }
  // 数字或关键字（NULL, true, false 等）
  if (/^\d+(\.\d+)?$/.test(t)) return { type: 'literal', value: parseFloat(t) };
  if (/^null$/i.test(t)) return { type: 'literal', value: null };
  return { type: 'literal', value: t };
}

// 提取从 openParenPos 位置开始的括号内的内容（处理嵌套括号）
function extractBalancedParen(sql, openParenPos) {
  let depth = 0;
  let start = openParenPos + 1; // 跳过开括号
  for (let i = start; i < sql.length; i++) {
    if (sql[i] === '(') depth++;
    else if (sql[i] === ')') {
      if (depth === 0) return sql.substring(start, i);
      depth--;
    }
  }
  return sql.substring(start);
}

function splitStatements(sql) {
  // 简单按分号分割，处理字符串内的分号
  const result = [];
  let current = '';
  let inString = false;
  let stringChar = '';
  for (let i = 0; i < sql.length; i++) {
    const ch = sql[i];
    if ((ch === "'" || ch === '"') && !inString) { inString = true; stringChar = ch; current += ch; }
    else if (ch === stringChar && inString) { inString = false; current += ch; }
    else if (ch === ';' && !inString) { result.push(current); current = ''; }
    else { current += ch; }
  }
  if (current.trim()) result.push(current);
  return result;
}

function parseInsert(sql) {
  // INSERT [OR IGNORE] INTO table (cols...) VALUES (...) [ON CONFLICT(...) DO UPDATE SET ...]
  const orIgnore = /INSERT\s+OR\s+IGNORE/i.test(sql);
  const tableMatch = sql.match(/INSERT\s+(?:OR\s+IGNORE\s+)?INTO\s+(\w+)/i);
  const table = tableMatch ? tableMatch[1].toLowerCase() : '';

  // 提取列名
  const colsMatch = sql.match(/\(([^)]+)\)\s*VALUES/i);
  let columns = [];
  if (colsMatch) {
    columns = colsMatch[1].split(',').map(c => c.trim().replace(/[\[\]"']/g, ''));
  }

  // 解析 ON CONFLICT DO UPDATE
  let upsert = null;
  const upsertMatch = sql.match(/ON\s+CONFLICT\(([^)]+)\)\s+DO\s+UPDATE\s+SET\s+(.+?)(?:$)/is);
  if (upsertMatch) {
    const conflictColumns = upsertMatch[1].split(',').map(c => c.trim());
    const setPart = upsertMatch[2].trim();
    const updateColumns = setPart.split(',').map(c => c.trim().split('=')[0].trim());
    upsert = { conflictColumns, updateColumns };
  }

  return { table, columns, orIgnore, upsert };
}

function parseUpdate(sql, externalParams) {
  // UPDATE table SET col=expr, ... WHERE ...
  const tableMatch = sql.match(/UPDATE\s+(\w+)/i);
  const table = tableMatch ? tableMatch[1].toLowerCase() : '';

  const setMatch = sql.match(/SET\s+(.+?)\s+WHERE/is);
  const setters = [];
  if (setMatch) {
    const setPart = setMatch[1];
    // 处理 (subquery) 形式的 SET
    const setPairs = splitSetPairs(setPart);
    for (const pair of setPairs) {
      const eqIdx = pair.indexOf('=');
      if (eqIdx < 0) continue;
      const col = pair.substring(0, eqIdx).trim();
      const expr = pair.substring(eqIdx + 1).trim();
      setters.push([col, expr]);
    }
  }

  const whereInfo = extractWhere(sql, externalParams);
  return { table, setters, where: whereInfo.condition, whereParams: whereInfo.params };
}

function parseDelete(sql, externalParams) {
  const tableMatch = sql.match(/DELETE\s+FROM\s+(\w+)/i);
  const table = tableMatch ? tableMatch[1].toLowerCase() : '';
  const whereInfo = extractWhere(sql, externalParams);
  return { table, where: whereInfo.condition, whereParams: whereInfo.params };
}

function splitSetPairs(setStr) {
  // 智能分割 SET 子句，处理括号内的子查询
  const pairs = [];
  let depth = 0;
  let current = '';
  for (let i = 0; i < setStr.length; i++) {
    const ch = setStr[i];
    if (ch === '(') depth++;
    else if (ch === ')') depth--;
    if (ch === ',' && depth === 0) {
      pairs.push(current.trim());
      current = '';
    } else {
      current += ch;
    }
  }
  if (current.trim()) pairs.push(current.trim());
  return pairs;
}

function extractWhere(sql, externalParams) {
  const whereIdx = searchWhereKeyword(sql);
  if (whereIdx < 0) return { condition: null, params: [] };
  const whereClause = sql.substring(whereIdx + 5).trim(); // skip "WHERE"
  // 解析条件为结构化形式
  const cond = parseCondition(whereClause, externalParams);
  return { condition: cond, params: externalParams || [] };
}

function searchWhereKeyword(sql) {
  const upper = sql.toUpperCase();
  // 只查找主查询级别（括号深度为0）的 WHERE，跳过子查询中的 WHERE
  let depth = 0;
  let inStr = false;
  let strCh = '';
  for (let i = 0; i < upper.length; i++) {
    const ch = sql[i];
    if ((ch === "'" || ch === '"') && !inStr) { inStr = true; strCh = ch; continue; }
    if (ch === strCh && inStr) { inStr = false; continue; }
    if (ch === '(') depth++;
    else if (ch === ')') depth--;
    if (depth === 0 && !inStr) {
      if (upper.substring(i, i + 6) === 'WHERE ' || upper.substring(i, i + 6) === '\nWHERE') return i;
      // also handle WHERE at start of remaining text
      if (i > 0 && upper.substring(i, i + 5) === 'WHERE' &&
          (i + 5 >= upper.length || /[\s)]/.test(upper[i + 5]))) return i;
    }
  }
  return -1;
}

function searchFromKeyword(sql) {
  const upper = sql.toUpperCase();
  // 只查找主查询级别（括号深度为0）的 FROM，跳过子查询中的 FROM
  let depth = 0;
  let inStr = false;
  let strCh = '';
  let afterSelect = false;
  for (let i = 0; i < upper.length; i++) {
    const ch = sql[i];
    if ((ch === "'" || ch === '"') && !inStr) { inStr = true; strCh = ch; continue; }
    if (ch === strCh && inStr) { inStr = false; continue; }
    if (ch === '(') depth++;
    else if (ch === ')') depth--;
    if (upper.substring(i, i + 6) === 'SELECT') afterSelect = true;
    if (afterSelect && depth === 0 && !inStr && upper.substring(i, i + 5) === 'FROM ') return i;
  }
  return -1;
}

// ── WHERE 条件解析 ──
function parseCondition(clause, params) {
  clause = clause.trim();
  // 处理括号包裹的复杂条件
  if (clause.startsWith('(') && hasMatchingParen(clause)) {
    return parseCondition(clause.slice(1, -1), params);
  }
  // 按 AND / OR 分割（简单实现）
  const parts = splitLogical(clause);
  if (parts && (parts.operator === 'AND' || parts.operator === 'OR')) {
    return {
      type: 'logical',
      operator: parts.operator,
      left: parseCondition(parts.left, params),
      right: parseCondition(parts.right, params)
    };
  }
  // 单个比较条件
  return parseComparison(clause, params);
}

function hasMatchingParen(s) {
  let depth = 0;
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '(') depth++;
    else if (s[i] === ')') { depth--; if (depth === 0 && i === s.length - 1) return true; }
  }
  return false;
}

function splitLogical(clause) {
  // 找到顶层 AND / OR
  let depth = 0;
  let inString = false;
  let strChar = '';
  for (let i = 0; i < clause.length; i++) {
    const ch = clause[i];
    if ((ch === "'" || ch === '"') && !inString) { inString = true; strChar = ch; continue; }
    if (ch === strChar && inString) { inString = false; continue; }
    if (ch === '(') depth++;
    else if (ch === ')') depth--;
    if (depth === 0 && !inString) {
      const rest = clause.substring(i).toUpperCase();
      if (rest.startsWith(' AND ') && i > 0) {
        return { operator: 'AND', left: clause.substring(0, i), right: clause.substring(i + 5) };
      }
      if (rest.startsWith(' OR ') && i > 0) {
        return { operator: 'OR', left: clause.substring(0, i), right: clause.substring(i + 4) };
      }
    }
  }
  return null;
}

function parseComparison(clause, params) {
  clause = clause.trim();

  // date(date_joined) = date('now')
  const dateFuncMatch = clause.match(/^date\((\w+)\)\s*=\s*date\(['"]?now['"]?\)/i);
  if (dateFuncMatch) {
    const col = dateFuncMatch[1];
    const today = new Date().toISOString().split('T')[0];
    return { type: 'func', func: 'date_eq', column: col, value: today };
  }

  // datetime('now') 比较
  const dtNowMatch = clause.match(/^(\w+)\s*(<=|>=|<|>)\s*datetime\(['"]?now['"]?\)/i);
  if (dtNowMatch) {
    return { type: 'comparison', column: dtNowMatch[1], op: dtNowMatch[2], value: new Date().toISOString(), paramType: 'literal' };
  }

  // vip_expire_date > datetime('now') or vip_expire_date IS NULL
  const orNullMatch = clause.match(/^(\w+)\s*(>|<|>=|<=)\s*datetime\(['"]?now['"]?\)\s+(OR|AND)\s+(\w+)\s+IS\s+NULL/i);
  if (orNullMatch) {
    return {
      type: 'or_null',
      column: orNullMatch[1],
      op: orNullMatch[2],
      compareValue: new Date().toISOString(),
      nullColumn: orNullMatch[4]
    };
  }

  // IS NULL / IS NOT NULL
  const isNullMatch = clause.match(/^(\w+)\s+IS\s+NULL/i);
  if (isNullMatch) return { type: 'null_check', column: isNullMatch[1], not: false };
  const isNotNullMatch = clause.match(/^(\w+)\s+IS\s+NOT\s+NULL/i);
  if (isNotNullMatch) return { type: 'null_check', column: isNotNullMatch[1], not: true };

  // IN (...)
  const inMatch = clause.match(/^(\w+)\s+IN\s*\(([^)]+)\)/i);
  if (inMatch) {
    const values = inMatch[2].split(',').map(v => v.trim().replace(/['"]/g, '')).map(v => isNaN(v) ? v : parseFloat(v));
    return { type: 'in', column: inMatch[1], values };
  }

  // 标准比较: col OP ?
  const compMatch = clause.match(/^(\w+)\s*(=|!=|<>|>=|<=|>|<)\s*(\?|\d+|'[^']*'|"[^"]*"|%[^%]*%)/i);
  if (compMatch) {
    let val;
    if (compMatch[3] === '?') {
      val = { type: 'param' }; // 占位符，运行时从 params 取值
    } else if (compMatch[3].startsWith("'") || compMatch[3].startsWith('"')) {
      val = compMatch[3].slice(1, -1);
    } else if (compMatch[3].includes('%')) {
      val = compMatch[3]; // LIKE pattern
    } else {
      val = isNaN(compMatch[3]) ? compMatch[3] : parseFloat(compMatch[3]);
    }
    return { type: 'comparison', column: compMatch[1], op: normalizeOp(compMatch[2]), value: val, paramType: typeof val === 'object' && val.type === 'param' ? 'param' : 'literal' };
  }

  // LIKE
  const likeMatch = clause.match(/^(\w+)\s+LIKE\s+(\?|'%[^']*%'|"%[^%]*%")/i);
  if (likeMatch) {
    const val = likeMatch[2] === '?' ? { type: 'param' } : likeMatch[2].slice(1, -1);
    return { type: 'like', column: likeMatch[1], value: val, paramType: val.type === 'param' ? 'param' : 'literal' };
  }

  // 无条件的真
  if (!clause || clause === '1') return { type: 'always' };

  return { type: 'always' };
}

function normalizeOp(op) {
  if (op === '<>') return '!=';
  return op;
}

// ── 条件匹配 ──
function matchWhere(row, condition, params) {
  if (!condition) return true;
  return evalCondition(row, condition, params, 0);
}

function evalCondition(row, condition, params, paramIdx) {
  switch (condition.type) {
    case 'always': return true;
    case 'logical': {
      const left = evalCondition(row, condition.left, params, paramIdx);
      if (condition.operator === 'AND') return left && evalCondition(row, condition.right, params, paramIdx);
      return left || evalCondition(row, condition.right, params, paramIdx);
    }
    case 'comparison': {
      const lval = getVal(row, condition.column);
      const rval = condition.paramType === 'param' ? params[paramIdx++] : condition.value;
      return compare(lval, rval, condition.op);
    }
    case 'like': {
      const lval = String(getVal(row, condition.column) || '');
      const rval = condition.paramType === 'param' ? params[paramIdx++] : condition.value;
      const pattern = String(rval).replace(/\%/g, '.*').replace(/\_/g, '.');
      return new RegExp('^' + pattern + '$', 'i').test(lval);
    }
    case 'null_check': {
      const val = row[condition.column];
      return condition.not ? (val !== null && val !== undefined) : (val === null || val === undefined);
    }
    case 'in': {
      const val = getVal(row, condition.column);
      return condition.values.includes(val);
    }
    case 'func':
      if (condition.func === 'date_eq') {
        const val = String(row[condition.column] || '');
        return val.startsWith(condition.value);
      }
      return true;
    case 'or_null': {
      const val = getVal(row, condition.column);
      const cmp = compare(val, condition.compareValue, condition.op);
      const isNull = row[condition.nullColumn] == null;
      return cmp || isNull;
    }
    default:
      return true;
  }
}

function getVal(row, col) {
  if (row.hasOwnProperty(col)) return row[col];
  return undefined;
}

function compare(a, b, op) {
  // 类型转换用于比较
  const la = a == null ? '' : (typeof a === 'number' ? a : String(a));
  const lb = b == null ? '' : (typeof b === 'number' ? b : String(b));
  switch (op) {
    case '=': return String(la) === String(lb);
    case '!=': return String(la) !== String(lb);
    case '>': return Number(la) > Number(lb);
    case '>=': return Number(la) >= Number(lb);
    case '<': return Number(la) < Number(lb);
    case '<=': return Number(la) <= Number(lb);
    default: return false;
  }
}

function evaluateExpression(expr, row, params) {
  expr = expr.trim();

  // MAX(0, col - 1)
  const maxMatch = expr.match(/^MAX\s*\(\s*(\d+)\s*,\s*(\w+)\s*-\s*(\d+)\s*\)$/i);
  if (maxMatch) {
    const fallback = parseInt(maxMatch[1]);
    const colVal = parseInt(row[maxMatch[2]]) || 0;
    const subtract = parseInt(maxMatch[3]) || 0;
    return Math.max(fallback, colVal - subtract);
  }

  // col + N 或 col + ? (coins = coins + ?)
  const addMatch = expr.match(/^(\w+)\s*\+\s*(\?|\d+)$/i);
  if (addMatch) {
    const base = parseInt(row[addMatch[1]]) || 0;
    const addend = addMatch[2] === '?' ? (params[0] || 0) : parseInt(addMatch[2]) || 0;
    return base + addend;
  }

  // (SELECT COUNT(*) FROM chapters WHERE novel_id = ?) — 子查询作为值
  const subqueryMatch = expr.match(/^\(SELECT\s+COUNT\(\*\)\s+FROM\s+(\w+)\s+WHERE\s+(\w+)\s*=\s*\?\)$/i);
  if (subqueryMatch) {
    const targetTable = subqueryMatch[1].toLowerCase();
    const targetCol = subqueryMatch[2];
    // 从当前 DB 实例中查找
    const targetData = _dbInstance.tables[targetTable] || [];
    return targetData.filter(r => String(r[targetCol]) === String(row.id)).length;
  }

  // 字面量或参数引用
  if (expr === '?') return params[0];

  return expr;
}

// ══════════════════════════════════════════════
//  SELECT 解析器（核心）
// ══════════════════════════════════════════════

function parseAndExecuteSelect(db, sql, params) {
  const parsed = parseSelectQuery(sql);
  let rows = [];

  // 主表数据
  if (parsed.from && parsed.from.table) {
    const { data } = db._getTable(parsed.from.table);
    rows = data.map(r => ({ ...r, __table__: parsed.from.table }));
  } else if (!parsed.from) {
    // 无 FROM 子句（如 SELECT 1）→ 返回单行
    rows = [{}];
  }

  // 处理 JOIN
  for (const join of parsed.joins) {
    rows = executeJoin(db, rows, join, params);
  }

  // WHERE 过滤
  if (parsed.where) {
    rows = rows.filter(r => matchWhere(r, parsed.where, params));
  }

  // GROUP BY + 聚合（如果只有聚合函数没有 GROUP BY，对全部行聚合）
  const hasAgg = hasAggregate(parsed.select.columns);

  if (hasAgg && !parsed.groupBy) {
    // 全表聚合 → 返回单行
    rows = [evaluateSelectColumns(parsed.select.columns, rows, params)];
  } else if (parsed.groupBy) {
    // GROUP BY 聚合
    const groups = groupRows(rows, parsed.groupBy);
    rows = groups.map(group => evaluateSelectColumns(parsed.select.columns, group, params));
  } else {
    // 普通行级 SELECT
    rows = rows.map(r => evaluateSelectColumns(parsed.select.columns, [r], params));
  }

  // ORDER BY
  if (parsed.orderBy) {
    rows = sortRows(rows, parsed.orderBy);
  }

  // DISTINCT
  if (parsed.distinct) {
    const seen = new Set();
    rows = rows.filter(r => {
      const key = JSON.stringify(r);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  // LIMIT / OFFSET
  if (parsed.limit != null) {
    const offset = parsed.offset || 0;
    rows = rows.slice(offset, offset + parsed.limit);
  }

  return rows;
}

function parseSelectQuery(sql) {
  const upperSql = sql.toUpperCase();

  // SELECT DISTINCT?
  const distinct = /^\s*SELECT\s+DISTINCT/i.test(sql);

  // 解析 SELECT 列
  const selectPart = extractSelectPart(sql);
  const columns = parseSelectColumns(selectPart);

  // FROM
  const fromMatch = sql.match(/\bFROM\s+(\w+)/i);
  const from = fromMatch ? { table: fromMatch[1].toLowerCase() } : null;

  // JOINs
  const joins = parseJoins(sql);

  // WHERE
  const whereResult = extractWhere(sql, []);

  // ORDER BY
  const orderBy = parseOrderBy(sql);

  // LIMIT / OFFSET
  const limitMatch = sql.match(/\bLIMIT\s+(\d+)/i);
  const limit = limitMatch ? parseInt(limitMatch[1]) : null;
  const offsetMatch = sql.match(/\bOFFSET\s+(\d+)/i);
  const offset = offsetMatch ? parseInt(offsetMatch[1]) : null;

  // GROUP BY
  const groupByMatch = sql.match(/\bGROUP\s+BY\s+([\w,\s]+?)(?:\s+ORDER|\s+LIMIT|$)/i);
  const groupBy = groupByMatch ? groupByMatch[1].trim().split(',').map(c => c.trim()) : null;

  return { select: { columns, distinct }, from, joins, where: whereResult.condition, orderBy, limit, offset, groupBy };
}

function extractSelectPart(sql) {
  // 找到 SELECT 和 FROM 之间的内容
  const upper = sql.toUpperCase();
  const selStart = upper.indexOf('SELECT');
  const fromIdx = searchFromKeyword(sql);
  if (fromIdx < 0) return sql.substring(selStart + 6).trim();
  return sql.substring(selStart + 6, fromIdx).trim();
}

function parseSelectColumns(selectStr) {
  const columns = [];
  // 处理逗号分隔的列，注意子查询中的逗号
  let depth = 0;
  let inStr = false;
  let strCh = '';
  let current = '';
  for (let i = 0; i < selectStr.length; i++) {
    const ch = selectStr[i];
    if ((ch === "'" || ch === '"') && !inStr) { inStr = true; strCh = ch; current += ch; continue; }
    if (ch === strCh && inStr) { inStr = false; current += ch; continue; }
    if (ch === '(') { depth++; current += ch; continue; }
    if (ch === ')') { depth--; current += ch; continue; }
    if (ch === ',' && depth === 0 && !inStr) {
      columns.push(parseSingleColumn(current.trim()));
      current = '';
    } else {
      current += ch;
    }
  }
  if (current.trim()) columns.push(parseSingleColumn(current.trim()));
  return columns;
}

function parseSingleColumn(expr) {
  expr = expr.trim();

  // COALESCE((subquery), 0) as alias
  const coalesceMatch = expr.match(/^COALESCE\(\((.+)\),\s*(\d+)\)\s+AS\s+(\w+)$/i);
  if (coalesceMatch) {
    return { type: 'coalesce_subquery', subquery: coalesceMatch[1], fallback: parseInt(coalesceMatch[2]), alias: coalesceMatch[3] };
  }

  // COALESCE(SUM(col), 0) as alias
  const coalesceSumMatch = expr.match(/^COALESCE\(SUM\((\w+)\),\s*(\d+)\)\s+AS\s+(\w+)$/i);
  if (coalesceSumMatch) {
    return { type: 'coalesce_sum', column: coalesceSumMatch[1], fallback: parseInt(coalesceSumMatch[2]), alias: coalesceSumMatch[3] };
  }

  // COALESCE(MAX(col), 0) as alias
  const coalesceMaxMatch = expr.match(/^COALESCE\(MAX\((\w+)\),\s*(\d+)\)\s+AS\s+(\w+)$/i);
  if (coalesceMaxMatch) {
    return { type: 'coalesce_max', column: coalesceMaxMatch[1], fallback: parseInt(coalesceMaxMatch[2]), alias: coalesceMaxMatch[3] };
  }

  // AVG(score) as avg
  const avgMatch = expr.match(/^AVG\((\w+)\)(?:\s+AS\s+(\w+))?$/i);
  if (avgMatch) {
    return { type: 'avg', column: avgMatch[1], alias: avgMatch[2] || 'avg' };
  }

  // COUNT(*) [as alias]
  const countStarMatch = expr.match(/^COUNT\(\*\)(?:\s+AS\s+(\w+))?$/i);
  if (countStarMatch) {
    return { type: 'count_star', alias: countStarMatch[1] || 'cnt' };
  }

  // COUNT(col) [as alias]
  const countColMatch = expr.match(/^COUNT\((\w+)\)(?:\s+AS\s+(\w+))?$/i);
  if (countColMatch) {
    return { type: 'count_col', column: countColMatch[1], alias: countColMatch[2] || 'cnt' };
  }

  // SUM(col) as cnt
  const sumMatch = expr.match(/^SUM\((\w+)\)\s+AS\s+(\w+)$/i);
  if (sumMatch) {
    return { type: 'sum', column: sumMatch[1], alias: sumMatch[2] };
  }

  // (subquery) as alias
  const subqAliasMatch = expr.match(/^\((.+)\)\s+AS\s+(\w+)$/is);
  if (subqAliasMatch) {
    return { type: 'subquery_alias', subquery: subqAliasMatch[1], alias: subqAliasMatch[2] };
  }

  // 1 as is_staff （字面量别名）
  const literalAliasMatch = expr.match(/^(\d+)\s+AS\s+(\w+)$/i);
  if (literalAliasMatch) {
    return { type: 'literal', value: parseInt(literalAliasMatch[1]), alias: literalAliasMatch[2] };
  }

  // table.* 或 *
  if (expr === '*') return { type: 'star' };
  if (expr.endsWith('.*')) {
    return { type: 'table_star', table: expr.split('.')[0] };
  }

  // col as alias
  const colAliasMatch = expr.match(/^([\w.]+)\s+AS\s+(\w+)$/i);
  if (colAliasMatch) {
    const parts = colAliasMatch[1].split('.');
    return { type: 'column', table: parts.length > 1 ? parts[0] : null, column: parts[parts.length - 1], alias: colAliasMatch[2] };
  }

  // table.col (带表前缀)
  if (expr.includes('.')) {
    const parts = expr.split('.');
    return { type: 'column', table: parts[0], column: parts[1] };
  }

  // plain column
  return { type: 'column', column: expr };
}

function parseJoins(sql) {
  const joins = [];
  const joinRegex = /\b(INNER\s+JOIN|LEFT\s+JOIN|JOIN)\s+(\w+)\s+ON\s+(.+?)(?=(?:INNER\s+JOIN|LEFT\s+JOIN|JOIN|WHERE|ORDER|GROUP|LIMIT|$))/gi;
  let m;
  while ((m = joinRegex.exec(sql)) !== null) {
    const type = m[1].replace(/\s+/g, ' ').toUpperCase(); // "INNER JOIN" | "LEFT JOIN" | "JOIN"
    const table = m[2].toLowerCase();
    const onClause = m[3].trim();
    joins.push({ type, table, on: onClause });
  }
  return joins;
}

function executeJoin(db, leftRows, joinInfo, params) {
  const { data: rightData, schema: rightSchema } = db._getTable(joinInfo.table);
  const result = [];

  // 解析 ON 条件
  const onCond = parseJoinOn(joinInfo.on);

  for (const leftRow of leftRows) {
    let matched = false;
    for (const rightRow of rightData) {
      const merged = { ...leftRow };
      // 给右表列加前缀避免冲突
      for (const [k, v] of Object.entries(rightRow)) {
        merged[k] = v;
      }

      if (evalJoinOn(onCond, leftRow, rightRow)) {
        result.push(merged);
        matched = true;
      }
    }

    // LEFT JOIN: 未匹配则用 NULL 填充右表
    if (!matched && (joinInfo.type === 'LEFT JOIN')) {
      const merged = { ...leftRow };
      for (const k of Object.keys(rightSchema)) {
        merged[k] = null;
      }
      result.push(merged);
    }
  }

  return result;
}

function parseJoinOn(onClause) {
  // table1.col1 = table2.col2
  const eqMatch = onClause.match(/(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)/);
  if (eqMatch) {
    return {
      type: 'eq',
      leftTable: eqMatch[1], leftCol: eqMatch[2],
      rightTable: eqMatch[3], rightCol: eqMatch[4]
    };
  }
  return { type: 'raw', clause: onClause };
}

function evalJoinOn(cond, leftRow, rightRow) {
  if (cond.type === 'eq') {
    const lv = cond.leftTable === '__implicit__' ? leftRow[cond.leftCol] :
              (leftRow.__table__ === cond.leftTable ? leftRow[cond.leftCol] : null);
    const rv = rightRow[cond.rightCol];
    // 尝试从左行取左表列，从右行取右表列
    const leftVal = leftRow[cond.leftCol];
    const rightVal = rightRow[cond.rightCol];
    return String(leftVal) === String(rightVal);
  }
  return true;
}

function parseOrderBy(sql) {
  const obMatch = sql.match(/\bORDER\s+BY\s+(.+?)(?:\s+LIMIT|\s+OFFSET|$)/is);
  if (!obMatch) return null;
  const parts = obMatch[1].split(',').map(p => p.trim());
  return parts.map(p => {
    const trimmed = p.trim();
    const desc = /\bDESC$/i.test(trimmed);
    const asc = /\bASC$/i.test(trimmed);
    const col = trimmed.replace(/\s+(?:DESC|ASC)$/i, '').trim();
    // 处理 table.col 格式
    const dotParts = col.split('.');
    return { column: dotParts[dotParts.length - 1], direction: desc ? 'desc' : (asc ? 'asc' : 'desc') };
  });
}

function sortRows(rows, orderBy) {
  return [...rows].sort((a, b) => {
    for (const ob of orderBy) {
      const va = a[ob.column];
      const vb = b[ob.column];
      const na = va == null ? (ob.direction === 'desc' ? -Infinity : Infinity) : (isNaN(va) ? String(va) : Number(va));
      const nb = vb == null ? (ob.direction === 'desc' ? -Infinity : Infinity) : (isNaN(vb) ? String(vb) : Number(vb));
      if (na < nb) return ob.direction === 'desc' ? 1 : -1;
      if (na > nb) return ob.direction === 'desc' ? -1 : 1;
    }
    return 0;
  });
}

function hasAggregate(columns) {
  return columns.some(c =>
    c.type === 'count_star' || c.type === 'count_col' || c.type === 'sum' ||
    c.type === 'avg' || c.type === 'coalesce_sum' || c.type === 'coalesce_max'
  );
}

function groupRows(rows, groupBy) {
  const groups = new Map();
  for (const r of rows) {
    const key = groupBy.map(g => String(r[g] ?? '')).join('\x00');
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(r);
  }
  return Array.from(groups.values());
}

function evaluateSelectColumns(columns, rows, params) {
  const result = {};
  for (const col of columns) {
    switch (col.type) {
      case 'star':
        for (const [k, v] of Object.entries(rows[0])) {
          if (k !== '__table__') result[k] = v;
        }
        break;
      case 'table_star':
        for (const [k, v] of Object.entries(rows[0])) {
          if (k !== '__table__') result[k] = v;
        }
        break;
      case 'column': {
        const val = rows[0][col.column];
        const outKey = col.alias || col.column;
        result[outKey] = val;
        break;
      }
      case 'literal':
        result[col.alias] = col.value;
        break;
      case 'count_star':
        result[col.alias] = rows.length;
        break;
      case 'count_col':
        result[col.alias] = rows.filter(r => r[col.column] != null).length;
        break;
      case 'sum': {
        let total = 0;
        for (const r of rows) total += Number(r[col.column]) || 0;
        result[col.alias] = total;
        break;
      }
      case 'avg': {
        let sum = 0, count = 0;
        for (const r of rows) { sum += Number(r[col.column]) || 0; count++; }
        result[col.alias] = count > 0 ? sum / count : 0;
        break;
      }
      case 'coalesce_sum': {
        let total = 0;
        for (const r of rows) total += Number(r[col.column]) || 0;
        result[col.alias] = total || col.fallback;
        break;
      }
      case 'coalesce_max': {
        let max = null;
        for (const r of rows) { const v = Number(r[col.column]); if (max == null || v > max) max = v; }
        result[col.alias] = max != null ? max : col.fallback;
        break;
      }
      case 'subquery_alias': {
        // 执行子查询（处理相关子查询：替换外部引用如 n.id 为实际值）
        const resolvedSub = resolveCorrelatedSubquery(col.subquery, rows[0]);
        const subRows = _dbInstance._executeSelect(resolvedSub, params);
        result[col.alias] = subRows.length > 0 ? Object.values(subRows[0])[0] : null;
        break;
      }
      case 'coalesce_subquery': {
        const resolvedSub = resolveCorrelatedSubquery(col.subquery, rows[0]);
        const subRows = _dbInstance._executeSelect(resolvedSub, params);
        result[col.alias] = subRows.length > 0 ? Object.values(subRows[0])[0] : col.fallback;
        break;
      }
    }
  }
  return result;
}

// 解析相关子查询：将 table.col 引用替换为当前行的实际值
function resolveCorrelatedSubquery(sql, outerRow) {
  if (!outerRow) return sql;
  // 匹配 word.word 格式（如表别名.列名）并替换为实际值
  return sql.replace(/\b(\w+)\.(\w+)\b/g, (match, alias, col) => {
    if (outerRow[col] !== undefined && outerRow[col] !== null) {
      const val = outerRow[col];
      if (typeof val === 'number') return String(val);
      return "'" + String(val).replace(/'/g, "''") + "'";
    }
    return match;
  });
}

// ══════════════════════════════════════════════
//  唯一约束信息
// ══════════════════════════════════════════════
function getUniqueKeys(table) {
  const map = {
    users: [['username'], ['email']],
    admin_user: [['username']],
    favorites: [['user_id', 'novel_id']],
    reading_progress: [['user_id', 'novel_id']],
    checkins: [['user_id', 'check_date']],
    orders: [['order_no']],
    follows: [['follower_id', 'following_name']],
    ratings: [['user_id', 'novel_id']]
  };
  return map[table] || [];
}

// ══════════════════════════════════════════════
//  公共 API
// ══════════════════════════════════════════════

async function initDatabase() {
  if (_initialized) return;
  _dbInstance = new MemoryDatabase();

  // 内置种子数据
  seedData(_dbInstance);

  _initialized = true;
}

function getDb() {
  if (!_dbInstance) throw new Error('数据库未初始化，请确保已调用 initDatabase()');
  return _dbInstance;
}

function now() {
  return new Date().toISOString();
}

// ══════════════════════════════════════════════
//  内置种子数据
// ══════════════════════════════════════════════
function seedData(db) {
  const bcrypt = require('bcryptjs');
  const t = now();

  // 管理员
  const adminPwd = bcrypt.hashSync('admin123', 10);
  db.run(`INSERT INTO admin_user (username, password, real_name, is_active, created_at) VALUES (?, ?, ?, 1, ?)`,
    'admin', adminPwd, '系统管理员', t);

  // 普通用户
  const userPwd = bcrypt.hashSync('123456', 10);
  db.run(`INSERT INTO users (username, email, password, is_staff, is_vip, coins, date_joined) VALUES (?, ?, ?, 0, 0, 100, ?)`,
    'reader', 'reader@example.com', userPwd, t);

  // 分类
  const categories = [
    ['玄幻', null, 1],
    ['仙侠', null, 2],
    ['都市', null, 3],
    ['历史', null, 4],
    ['科幻', null, 5],
    ['悬疑', null, 6],
    ['言情', null, 7],
    ['武侠', null, 8],
  ];
  for (const [name, pid, order] of categories) {
    db.run(`INSERT INTO categories (name, parent_id, sort_order, is_active, color, created_at) VALUES (?, ?, ?, 1, ?, ?)`,
      name, pid, order, '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0'), t);
  }

  // 示例小说
  const novels = [
    { title: '星辰变', author: '我吃西红柿', cat: '玄幻', desc: '秦羽，一个资质平庸的少年，在机缘巧合下踏上了修真之路。从默默无闻到名震天下，他的传奇故事由此展开...', words: 3200000, views: 890000, rec: 5200, status: 1 },
    { title: '斗破苍穹', author: '天蚕土豆', cat: '玄幻', desc: '萧炎，曾经的家族天才，如今却沦为废人。但他并未放弃，在药老的指引下，他踏上了一条逆天改命的道路...', words: 5300000, views: 2100000, rec: 12000, status: 1 },
    { title: '完美世界', author: '辰东', cat: '仙侠', desc: '一粒尘可填海，一根草斩尽日月星辰，弹指间天翻地覆。群雄并起，万族林立，诸圣争霸，乱天动地...', words: 4800000, views: 1750000, rec: 8900, status: 0 },
    { title: '遮天', author: '辰东', cat: '仙侠', desc: '冰冷与黑暗并存的宇宙深处，九具庞大的龙尸拉着一口青铜古棺，亘古长存。这是太空中的青铜巨棺，九龙拉棺，究竟来自何方？', words: 6500000, views: 2300000, rec: 15000, status: 1 },
    { title: '大主宰', author: '天蚕土豆', cat: '玄幻', desc: '大千世界，位面交汇，万族林立，群雄荟萃，一位位来自下位面的天之至尊，在这无尽世界，演绎着令人向往的传奇...', words: 4200000, views: 1500000, rec: 7500, status: 1 },
    { title: '赘婿', author: '愤怒的香蕉', cat: '都市', desc: '武毅穿越成为苏家赘婿，本想安安稳稳过日子，奈何身不由己。他一步步走上巅峰，揭开一个个惊天秘密...', words: 2800000, views: 1300000, rec: 6800, status: 0 },
    { title: '雪中悍刀行', author: '烽火戏诸侯', cat: '武侠', desc: '北凉王世子徐凤年，历经三千大道，十万大山，百万甲兵，终成天下第一人。这是一个关于江湖、庙堂和人生的故事...', words: 4500000, views: 1680000, rec: 9200, status: 1 },
    { title: '诡秘之主', author: '爱潜水的乌贼', cat: '悬疑', desc: '周明瑞穿越到了一个蒸汽与机械的世界，在这里，他发现了一个关于神灵的惊人秘密...', words: 3800000, views: 1950000, rec: 11000, status: 1 },
    { title: '凡人修仙传', author: '忘语', cat: '仙侠', desc: '一个普通山村穷小子，偶然之下跨入到一个江湖小门派，虽然资质平庸，但依靠自身努力和合理算计最后修炼成仙...', words: 5600000, views: 2450000, rec: 13500, status: 1 },
    { title: '全职高手', author: '蝴蝶蓝', cat: '都市', desc: '网游荣耀中被誉为教科书级别的顶尖高手叶修，因为种种原因遭到俱乐部的驱逐。离开职业圈的他寄身于一家网吧成了一个小小的网管...', words: 3500000, views: 1800000, rec: 10500, status: 1 },
    { title: '庆余年', author: '猫腻', cat: '历史', desc: '范闲，一个现代灵魂穿越到古代的故事。他在权谋斗争中步步为营，最终揭开了自己的身世之谜...', words: 2900000, views: 1120000, rec: 5600, status: 1 },
    { title: '三体', author: '刘慈欣', cat: '科幻', desc: '文化大革命如火如荼进行的同时，军方探寻外星文明的绝秘计划"红岸工程"取得了突破性进展...', words: 880000, views: 980000, rec: 20000, status: 1 },
  ];

  const commentTemplates = [
    '这本书太好看了！强烈推荐！',
    '情节紧凑，人物刻画生动，值得一看。',
    '更新太慢了，等得好辛苦...',
    '文笔不错，世界观宏大。',
    '已经追了好久了，期待后续发展！',
    '主角的成长路线很清晰，喜欢这种风格。',
    '战斗场面描写得非常精彩！',
    '感情线处理得很细腻，感人至深。',
  ];
  const chapterTemplates = [
    (title, novelName, category) => `${title}\n\n夜幕低垂，繁星点点。\n\n${novelName}的世界里，一场新的冒险正在悄然展开。主人公站在山巅之上，眺望着远方的地平线。风吹过他的衣摆，带来一丝凉意。\n\n"前方就是传说中的秘境了。"他喃喃自语道。\n\n这一路走来，经历了无数艰难险阻，但所有的付出都将在今天得到回报。他深吸一口气，迈出了坚定的步伐。\n\n空气中弥漫着淡淡的灵气波动，显然这里并非寻常之地。周围的树木高大挺拔，叶片上闪烁着微弱的光芒——这是${category}世界特有的灵植。\n\n就在这时，一道身影从前方走出...\n\n（本章完）`,
    (title, novelName, category) => `${title}\n\n清晨的第一缕阳光透过窗户洒进房间。\n\n主人公缓缓睁开双眼，感受着体内流转的力量。经过一夜的修炼，他的修为又精进了几分。这让他对即将到来的挑战充满了信心。\n\n"是时候出发了。"他整理好行装，推开门走了出去。\n\n外面的世界依然喧嚣热闹，街道上行色匆匆的人们各奔前程。而他的目标只有一个——那就是变强，强到足以保护身边的一切。\n\n远处传来一阵骚动，似乎发生了什么事情。主人公眉头微皱，朝着声音的方向快步走去...\n\n（本章完）`,
    (title, novelName, category) => `${title}\n\n天地之间，风云变幻。\n\n一道惊雷划破长空，紧接着便是倾盆大雨。主人公站在雨中，任凭雨水冲刷着他的身体。这不是普通的雨，而是蕴含着天地灵气的洗礼。\n\n"终于等到这一天了..."他的眼中闪烁着兴奋的光芒。\n\n在${category}的世界里，这种天气变化往往预示着重大的事件将要发生。而他，已经为此准备了太久太久。\n\n体内的力量在不断涌动，仿佛要突破某种桎梏。他知道，这是突破的征兆——一个全新的境界正在向他招手。\n\n他闭上眼睛，开始引导体内那股狂暴的能量...\n\n（本章完）`,
  ];

  for (const n of novels) {
    const chCount = 50 + Math.floor(Math.random() * 300);
    const novelRes = db.run(
      `INSERT INTO novels (title, author_name, cover, category, description, status, audit_status, word_count, view_count, recommend, chapter_count, favorite_count, is_adapted, is_recommended, latest_chapter, created_at, updated_at) VALUES (?, '', ?, ?, ?, ?, 2, ?, ?, ?, ?, ?, 0, 1, ?, ?, ?)`,
      n.title, n.author, n.cat, n.desc, n.status, n.words, n.views, n.rec, chCount, Math.floor(n.views / 50),
      `第${chCount}章 大结局`, t, t
    );
    const novelId = novelRes.lastInsertRowid;

    const sampleChapters = [
      `第一章 ${n.title}起源`,
      `第二章 初入${n.cat}世界`,
      `第三章 奇遇降临`,
      ...Array.from({ length: chCount - 3 }, (_, i) => `第${i + 4}章 历练之路`),
    ];

    for (let i = 0; i < sampleChapters.length; i++) {
      const tpl = chapterTemplates[Math.floor(Math.random() * chapterTemplates.length)];
      const content = tpl(sampleChapters[i], n.title, n.cat);
      db.run(
        `INSERT INTO chapters (novel_id, title, content, chapter_order, word_count, publish_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)`,
        novelId, sampleChapters[i], content, i + 1, content.length, t, t
      );
    }
  }

  // 评论
  const allNovels = db.all('SELECT id FROM novels');
  const userIds = db.all('SELECT id FROM users');
  for (const novel of allNovels) {
    const count = 3 + Math.floor(Math.random() * 12);
    for (let i = 0; i < count; i++) {
      const uid = userIds[Math.floor(Math.random() * userIds.length)].id;
      const rating = Math.floor(Math.random() * 5) + 1;
      db.run(
        `INSERT INTO comments (user_id, novel_id, content, rating, created_at) VALUES (?, ?, ?, ?, ?)`,
        uid, novel.id, commentTemplates[Math.floor(Math.random() * commentTemplates.length)], rating, t
      );
    }
  }

  // 评分
  for (const novel of allNovels) {
    for (const u of userIds) {
      db.run(
        `INSERT OR IGNORE INTO ratings (user_id, novel_id, score, created_at) VALUES (?, ?, ?, ?)`,
        u.id, novel.id, Math.floor(Math.random() * 5) + 1, t
      );
    }
  }

  // 关注
  const authors = [...new Set(novels.map(n => n.author))];
  for (const u of userIds) {
    authors.slice(0, 3 + Math.floor(Math.random() * authors.length)).forEach(a => {
      db.run(
        `INSERT OR IGNORE INTO follows (follower_id, following_name, created_at) VALUES (?, ?, ?)`,
        u.id, a, t
      );
    });
  }

  // 广告
  db.exec(`
    INSERT INTO advertisements (title, ad_type, image_url, link_url, position, is_active, sort_order, created_at, updated_at)
    VALUES ('墨香书阁VIP会员', 'banner', '/ads/vip-banner.jpg', '/membership', 'home_top', 1, 1, '${t}', '${t}'),
           ('新书推荐', 'sidebar', '/ads/new-book.jpg', '/novels/category?category=玄幻', 'home_sidebar', 1, 2, '${t}', '${t}'),
           ('阅读体验升级', 'popup', '/ads/upgrade.jpg', '/membership', 'reader_popup', 1, 3, '${t}', '${t}');
  `);

  // 公告
  db.exec(`
    INSERT INTO announcements (title, content, announcement_type, is_pinned, is_active, created_at, updated_at)
    VALUES ('欢迎使用墨香书阁', '欢迎来到墨香书阁，这里汇聚了海量精彩小说，祝您阅读愉快！', 'notice', 1, 1, '${t}', '${t}'),
           ('系统维护通知', '本站将于每周日凌晨2:00-4:00进行例行维护，届时部分功能可能不可用，敬请谅解。', 'maintenance', 0, 1, '${t}', '${t}'),
           ('签到活动开启', '每日签到即可获得虚拟币奖励，连续签到奖励更丰厚！快来参与吧~', 'activity', 0, 1, '${t}', '${t}');
  `);
}

module.exports = { initDatabase, getDb, now };
