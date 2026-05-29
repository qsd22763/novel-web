<template>
  <div class="author-center">
    <header class="ac-header">
      <div class="ac-inner">
        <router-link to="/" class="brand">墨香书阁 · 作者中心</router-link>
        <nav class="ac-nav">
          <router-link to="/" class="nav-link">返回首页</router-link>
          <router-link to="/user" class="nav-link">个人中心</router-link>
        </nav>
      </div>
    </header>

    <main class="ac-main">
      <section class="stats-strip">
        <div class="stat-card">
          <span class="stat-label">作品数</span>
          <span class="stat-value">{{ stats.total_works }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">章节数</span>
          <span class="stat-value">{{ stats.total_chapters }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">总字数</span>
          <span class="stat-value">{{ formatNumber(stats.total_words) }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">总阅读量</span>
          <span class="stat-value">{{ formatNumber(stats.total_views) }}</span>
        </div>
      </section>

      <section class="works-section">
        <div class="section-head">
          <h2 class="section-title">我的作品</h2>
          <router-link to="/author/novel/new" class="primary-btn">
            <span>＋</span> 创作新书
          </router-link>
        </div>

        <div v-if="loading" class="empty">加载中…</div>
        <div v-else-if="works.length === 0" class="empty">
          <p>还没有作品，点击右上角创作你的第一本书。</p>
        </div>

        <ul v-else class="works-list">
          <li v-for="w in works" :key="w.id" class="work-item">
            <div class="work-cover">
              <img v-if="w.cover" :src="resolveCover(w.cover)" :alt="w.title" />
              <span v-else class="cover-fallback">{{ w.title.slice(0, 1) }}</span>
            </div>
            <div class="work-body">
              <div class="work-head">
                <h3 class="work-title">{{ w.title }}</h3>
                <span class="badge" :class="audClass(w.audit_status)">{{ w.audit_status_display }}</span>
                <span class="badge badge-line">{{ w.status_display }}</span>
              </div>
              <p class="work-desc">{{ w.description || '暂无简介' }}</p>
              <div class="work-meta">
                <span>分类：{{ w.category }}</span>
                <span>章节：{{ w.chapter_count }}</span>
                <span>字数：{{ formatNumber(w.word_count) }}</span>
                <span>阅读：{{ formatNumber(w.view_count) }}</span>
              </div>
            </div>
            <div class="work-actions">
              <router-link :to="`/author/novel/${w.id}/edit`" class="link-btn">编辑信息</router-link>
              <router-link :to="`/author/novel/${w.id}/chapters`" class="link-btn">管理章节</router-link>
              <button class="link-btn danger" @click="onDelete(w)">删除</button>
            </div>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { authorApi, type AuthorNovel } from '../api'
import { resolveCover } from '../utils/image'

const loading = ref(true)
const works = ref<AuthorNovel[]>([])
const stats = ref({ total_works: 0, total_chapters: 0, total_words: 0, total_views: 0 })

const formatNumber = (n: number) => {
  if (!n) return '0'
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return String(n)
}
const audClass = (s: number) => ['', '', 'ok', 'warn', 'danger'][s] || ''

const load = async () => {
  loading.value = true
  try {
    const [listRes, statsRes] = await Promise.all([
      authorApi.novelList(),
      authorApi.stats(),
    ])
    works.value = Array.isArray(listRes) ? listRes : (listRes.results || [])
    stats.value = statsRes
  } finally {
    loading.value = false
  }
}

const onDelete = async (w: AuthorNovel) => {
  if (!confirm(`确定删除《${w.title}》吗？此操作不可恢复。`)) return
  await authorApi.deleteNovel(w.id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.author-center {
  min-height: 100vh;
  background: #FDFBF7;
  color: #1A1A1A;
  font-family: 'Noto Serif SC', serif;
}

.ac-header {
  background: #1A1A1A;
  color: #FDFBF7;
  border-bottom: 1px solid #2a2a2a;
}
.ac-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  color: #CA8A04;
  font-size: 20px;
  font-weight: 600;
  text-decoration: none;
  letter-spacing: 2px;
}
.ac-nav {
  display: flex;
  gap: 24px;
}
.nav-link {
  color: #FDFBF7;
  text-decoration: none;
  font-size: 14px;
  opacity: 0.85;
  transition: opacity 0.2s;
}
.nav-link:hover { opacity: 1; color: #CA8A04; }

.ac-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 40px;
}
.stat-card {
  background: #fff;
  border: 1px solid #ECE7DC;
  border-radius: 4px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-label {
  color: #666;
  font-size: 13px;
  font-family: 'Noto Sans SC', sans-serif;
}
.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #CA8A04;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ECE7DC;
}
.section-title {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 2px;
}
.primary-btn {
  background: #CA8A04;
  color: #fff;
  padding: 10px 20px;
  border-radius: 2px;
  text-decoration: none;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}
.primary-btn:hover { background: #A87403; }
.primary-btn span { font-size: 18px; line-height: 1; }

.empty {
  background: #fff;
  border: 1px dashed #D8D2C4;
  padding: 60px;
  text-align: center;
  color: #888;
  border-radius: 4px;
}

.works-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.work-item {
  background: #fff;
  border: 1px solid #ECE7DC;
  border-radius: 4px;
  padding: 20px;
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 20px;
  transition: box-shadow 0.2s;
}
.work-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.05); }
.work-cover {
  width: 100px;
  height: 140px;
  background: #F5F0E5;
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.work-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cover-fallback {
  font-size: 36px;
  color: #CA8A04;
  font-weight: 600;
}
.work-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.work-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 2px;
  font-family: 'Noto Sans SC', sans-serif;
  background: #F0EBE0;
  color: #666;
}
.badge.ok { background: #E8F5E9; color: #2E7D32; }
.badge.warn { background: #FFF3E0; color: #E65100; }
.badge.danger { background: #FFEBEE; color: #C62828; }
.badge-line { background: transparent; border: 1px solid #D8D2C4; }
.work-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.7;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.work-meta {
  display: flex;
  gap: 18px;
  font-size: 13px;
  color: #888;
  font-family: 'Noto Sans SC', sans-serif;
}
.work-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}
.link-btn {
  background: transparent;
  border: 1px solid #D8D2C4;
  color: #1A1A1A;
  padding: 6px 14px;
  border-radius: 2px;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  font-family: inherit;
  transition: all 0.2s;
}
.link-btn:hover { border-color: #CA8A04; color: #CA8A04; }
.link-btn.danger:hover { border-color: #C62828; color: #C62828; }
</style>
