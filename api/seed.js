const { getDb, now, saveDb } = require('./db');
const bcrypt = require('bcryptjs');

async function runSeed() {
  await require('./db').initDatabase();

  const db = getDb();

  // 检查是否已有数据
  const existingUsers = db.prepare('SELECT COUNT(*) as cnt FROM users').get();
  if (existingUsers.cnt > 0) {
    console.log('数据库已有数据，跳过种子初始化');
    return;
  }

  const t = now();

  // 创建管理员
  const adminPwd = bcrypt.hashSync('admin123', 10);
  db.prepare(`INSERT INTO admin_user (username, password, real_name, is_active, created_at)
    VALUES ('admin', ?, '系统管理员', 1, ?)`).run(adminPwd, t);

  // 创建普通用户
  const userPwd = bcrypt.hashSync('123456', 10);
  db.prepare(`INSERT INTO users (username, email, password, is_staff, is_vip, coins, date_joined)
    VALUES ('reader', 'reader@example.com', ?, 0, 0, 100, ?)`).run(userPwd, t);

  // 创建分类
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
  const insertCat = db.prepare('INSERT INTO categories (name, parent_id, sort_order, is_active, color, created_at) VALUES (?, ?, ?, 1, ?, ?)');
  for (const [name, pid, order] of categories) {
    insertCat.run(name, pid, order, `#${Math.floor(Math.random()*16777215).toString(16).padStart(6,'0')}`, t);
  }

  // 示例小说数据
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

  const insertNovel = db.prepare(`INSERT INTO novels (title, author_name, cover, category, description, status, audit_status, word_count, view_count, recommend, chapter_count, favorite_count, is_adapted, is_recommended, latest_chapter, created_at, updated_at)
    VALUES (?, '', ?, ?, ?, ?, 2, ?, ?, ?, ?, ?, 0, 1, ?, ?, ?)`);

  for (const n of novels) {
    const chCount = 50 + Math.floor(Math.random() * 300);
    insertNovel.run(n.title, n.author, n.cat, n.desc, n.status, n.words, n.views, n.rec, chCount, Math.floor(n.views / 50), `第${chCount}章 大结局`, t, t);

    const result = db.prepare('SELECT last_insert_rowid() as id').get();
    const novelId = result.id;

    const sampleChapters = [
      `第一章 ${n.title}起源`,
      `第二章 初入${n.cat}世界`,
      `第三章 奇遇降临`,
      ...Array.from({ length: chCount - 3 }, (_, i) => `第${i + 4}章 历练之路`),
    ];

    const insertChapter = db.prepare(`INSERT INTO chapters (novel_id, title, content, chapter_order, word_count, publish_status, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, 1, ?, ?)`);

    for (let i = 0; i < sampleChapters.length; i++) {
      const content = generateChapterContent(sampleChapters[i], n.title, n.cat);
      insertChapter.run(novelId, sampleChapters[i], content, i + 1, content.length, t, t);
    }
  }

  // 插入评论
  const allNovels = db.prepare('SELECT id FROM novels').all();
  const userIds = db.prepare('SELECT id FROM users').all();
  const insertComment = db.prepare('INSERT INTO comments (user_id, novel_id, content, rating, created_at) VALUES (?, ?, ?, ?, ?)');
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
  for (const novel of allNovels) {
    const count = 3 + Math.floor(Math.random() * 12);
    for (let i = 0; i < count; i++) {
      const uid = userIds[Math.floor(Math.random() * userIds.length)].id;
      const rating = Math.floor(Math.random() * 5) + 1;
      insertComment.run(uid, novel.id, commentTemplates[Math.floor(Math.random() * commentTemplates.length)], rating, t);
    }
  }

  // 插入评分
  const insertRating = db.prepare('INSERT OR IGNORE INTO ratings (user_id, novel_id, score, created_at) VALUES (?, ?, ?, ?)');
  for (const novel of allNovels) {
    for (const u of userIds) {
      insertRating.run(u.id, novel.id, Math.floor(Math.random() * 5) + 1, t);
    }
  }

  // 插入关注记录
  const authors = [...new Set(novels.map(n => n.author))];
  const insertFollow = db.prepare('INSERT OR IGNORE INTO follows (follower_id, following_name, created_at) VALUES (?, ?, ?)');
  for (const u of userIds) {
    authors.slice(0, 3 + Math.floor(Math.random() * authors.length)).forEach(a => {
      insertFollow.run(u.id, a, t);
    });
  }

  // 插入广告
  db.exec(`
    INSERT INTO advertisements (title, ad_type, image_url, link_url, position, is_active, sort_order, created_at, updated_at)
    VALUES ('墨香书阁VIP会员', 'banner', '/ads/vip-banner.jpg', '/membership', 'home_top', 1, 1, '${t}', '${t}'),
           ('新书推荐', 'sidebar', '/ads/new-book.jpg', '/novels/category?category=玄幻', 'home_sidebar', 1, 2, '${t}', '${t}'),
           ('阅读体验升级', 'popup', '/ads/upgrade.jpg', '/membership', 'reader_popup', 1, 3, '${t}', '${t}');
  `);

  // 插入公告
  db.exec(`
    INSERT INTO announcements (title, content, announcement_type, is_pinned, is_active, created_at, updated_at)
    VALUES ('欢迎使用墨香书阁', '欢迎来到墨香书阁，这里汇聚了海量精彩小说，祝您阅读愉快！', 'notice', 1, 1, '${t}', '${t}'),
           ('系统维护通知', '本站将于每周日凌晨2:00-4:00进行例行维护，届时部分功能可能不可用，敬请谅解。', 'maintenance', 0, 1, '${t}', '${t}'),
           ('签到活动开启', '每日签到即可获得虚拟币奖励，连续签到奖励更丰厚！快来参与吧~', 'activity', 0, 1, '${t}', '${t}');
  `);

  saveDb();

  console.log('种子数据初始化完成！');
  console.log('- 管理员账号: admin / admin123');
  console.log('- 普通用户: reader / 123456');
}

function generateChapterContent(title, novelName, category) {
  const templates = [
    `${title}\n\n夜幕低垂，繁星点点。\n\n${novelName}的世界里，一场新的冒险正在悄然展开。主人公站在山巅之上，眺望着远方的地平线。风吹过他的衣摆，带来一丝凉意。\n\n"前方就是传说中的秘境了。"他喃喃自语道。\n\n这一路走来，经历了无数艰难险阻，但所有的付出都将在今天得到回报。他深吸一口气，迈出了坚定的步伐。\n\n空气中弥漫着淡淡的灵气波动，显然这里并非寻常之地。周围的树木高大挺拔，叶片上闪烁着微弱的光芒——这是${category}世界特有的灵植。\n\n就在这时，一道身影从前方走出...\n\n（本章完）`,
    `${title}\n\n清晨的第一缕阳光透过窗户洒进房间。\n\n主人公缓缓睁开双眼，感受着体内流转的力量。经过一夜的修炼，他的修为又精进了几分。这让他对即将到来的挑战充满了信心。\n\n"是时候出发了。"他整理好行装，推开门走了出去。\n\n外面的世界依然喧嚣热闹，街道上行色匆匆的人们各奔前程。而他的目标只有一个——那就是变强，强到足以保护身边的一切。\n\n远处传来一阵骚动，似乎发生了什么事情。主人公眉头微皱，朝着声音的方向快步走去...\n\n（本章完）`,
    `${title}\n\n天地之间，风云变幻。\n\n一道惊雷划破长空，紧接着便是倾盆大雨。主人公站在雨中，任凭雨水冲刷着他的身体。这不是普通的雨，而是蕴含着天地灵气的洗礼。\n\n"终于等到这一天了..."他的眼中闪烁着兴奋的光芒。\n\n在${category}的世界里，这种天气变化往往预示着重大的事件将要发生。而他，已经为此准备了太久太久。\n\n体内的力量在不断涌动，仿佛要突破某种桎梏。他知道，这是突破的征兆——一个全新的境界正在向他招手。\n\n他闭上眼睛，开始引导体内那股狂暴的能量...\n\n（本章完）`,
  ];
  return templates[Math.floor(Math.random() * templates.length)];
}

if (require.main === module) {
  runSeed().catch(e => {
    console.error('种子数据初始化失败:', e && e.message ? e.message : String(e));
    if (e && e.stack) console.error(e.stack);
    process.exit(1);
  });
}

module.exports = { runSeed };
