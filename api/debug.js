// Debug script - run: node api/debug.js
const { initDatabase, getDb } = require('./db');

async function main() {
  console.log('Step 1: Initializing database...');
  await initDatabase();
  console.log('Step 1 OK');

  const db = getDb();
  const t = new Date().toISOString();

  console.log('Step 2: Creating admin...');
  const bcrypt = require('bcryptjs');
  db.prepare(`INSERT INTO admin_user (username, password, real_name, is_active, created_at) VALUES (?, ?, '系统管理员', 1, ?)`).run(bcrypt.hashSync('admin123', 10), t);
  console.log('Step 2 OK');

  console.log('Step 3: Creating user...');
  db.prepare(`INSERT INTO users (username, email, password, is_staff, is_vip, coins, date_joined) VALUES ('reader', 'reader@example.com', ?, 0, 0, 100, ?)`).run(bcrypt.hashSync('123456', 10), t);
  console.log('Step 3 OK');

  console.log('Step 4: Creating categories...');
  for (const [name, pid, order] of [['玄幻', null, 1], ['仙侠', null, 2], ['都市', null, 3]]) {
    db.prepare('INSERT INTO categories (name, parent_id, sort_order, is_active, color, created_at) VALUES (?, ?, ?, 1, ?, ?)').run(name, pid, order, '#FF0000', t);
  }
  console.log('Step 4 OK');

  console.log('Step 5: Creating novel...');
  db.prepare(`INSERT INTO novels (title, author_name, cover, category, description, status, audit_status, word_count, view_count, recommend, chapter_count, favorite_count, is_adapted, is_recommended, latest_chapter, created_at, updated_at)
    VALUES ('TestNovel', 'TestAuthor', '', '玄幻', 'test desc', 0, 2, 1000, 500, 10, 5, 0, 0, 1, 'Ch5', ?, ?)`).run(t, t);
  console.log('Step 5 OK');

  console.log('Step 6: Getting novel ID...');
  const result = db.prepare('SELECT last_insert_rowid() as id').get();
  console.log('Novel ID:', result.id);

  console.log('Step 7: Creating chapters...');
  for (let i = 1; i <= 5; i++) {
    db.prepare(`INSERT INTO chapters (novel_id, title, content, chapter_order, word_count, publish_status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)`)
      .run(result.id, `第${i}章`, `Content of chapter ${i}...`, i, 20, t, t);
  }
  console.log('Step 7 OK');

  console.log('Step 8: Testing multi-statement exec()...');
  db.exec("INSERT INTO advertisements (title, ad_type, image_url, link_url, position, is_active, sort_order, created_at, updated_at) VALUES ('test-ad', 'banner', '/img.jpg', '/', 'home_top', 1, 1, '" + t + "', '" + t + "')");
  console.log('Step 8 OK');

  // Save
  const { saveDb } = require('./db');
  saveDb();
  console.log('\n✅ All steps passed! Database is ready.');
}

main().catch(e => {
  console.error('❌ Failed at step:');
  console.error('Error type:', typeof e);
  console.error('Error value:', e);
  if (e && typeof e === 'object') {
    console.error('Keys:', Object.keys(e));
    console.error('Message:', e.message || '(no message)');
    console.error('Stack:', e.stack || '(no stack)');
  }
  process.exit(1);
});
