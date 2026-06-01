<template>
  <div class="chapter-list">
    <header class="head">
      <div class="inner">
        <router-link to="/author" class="back-link">← 返回作者中心</router-link>
        <h1 class="title">{{ novelTitle }} · 章节管理</h1>
        <router-link :to="`/author/novel/${novelId}/chapter/new`" class="btn-primary">
          ＋ 新建章节
        </router-link>
      </div>
    </header>

    <main class="main">
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="chapters.length === 0" class="empty">
        <p>这本书还没有章节，快去写第一章吧。</p>
        <router-link :to="`/author/novel/${novelId}/chapter/new`" class="btn-primary">立即开始</router-link>
      </div>

      <ul v-else class="list">
        <li v-for="c in chapters" :key="c.id" class="row">
          <span class="order">第 {{ c.chapter_order }} 章</span>
          <span class="ch-title">{{ c.title }}</span>
          <span class="meta">{{ c.word_count }} 字</span>
          <span class="badge" :class="c.publish_status === 1 ? 'ok' : 'warn'">
            {{ c.publish_status_display }}
          </span>
          <span class="time">{{ formatTime(c.updated_at) }}</span>
          <div class="actions">
            <router-link :to="`/author/novel/${novelId}/chapter/${c.id}/edit`" class="link">编辑</router-link>
            <button class="link danger" @click="onDelete(c)">删除</button>
          </div>
        </li>
      </ul>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { authorApi, type AuthorChapter } from '../api'

const route = useRoute()
const novelId = Number(route.params.novelId)
const novelTitle = ref('')
const chapters = ref<AuthorChapter[]>([])
const loading = ref(true)

const formatTime = (s: string) => {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const load = async () => {
  loading.value = true
  try {
    const [novelRes, listRes] = await Promise.all([
      authorApi.novelDetail(novelId),
      authorApi.chapterList(novelId),
    ])
    novelTitle.value = novelRes.title
    chapters.value = Array.isArray(listRes) ? listRes : (listRes.results || [])
  } finally {
    loading.value = false
  }
}

const onDelete = async (c: AuthorChapter) => {
  if (!confirm(`确定删除章节「${c.title}」吗？`)) return
  await authorApi.deleteChapter(c.id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.chapter-list {
  min-height: 100vh;
  background: #FDFBF7;
  font-family: 'Noto Serif SC', serif;
  color: #1A1A1A;
}
.head {
  background: #1A1A1A;
  color: #FDFBF7;
}
.inner {
  max-width: 1080px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.back-link {
  color: #FDFBF7;
  text-decoration: none;
  font-size: 14px;
  opacity: 0.85;
}
.back-link:hover { color: #CA8A04; opacity: 1; }
.title {
  flex: 1;
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  letter-spacing: 2px;
}
.btn-primary {
  background: #CA8A04;
  color: #fff;
  padding: 10px 18px;
  text-decoration: none;
  font-size: 14px;
  border-radius: 2px;
}
.btn-primary:hover { background: #A87403; }

.main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 24px 80px;
}

.empty {
  background: #fff;
  border: 1px dashed #D8D2C4;
  padding: 60px;
  text-align: center;
  color: #888;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.list { list-style: none; padding: 0; margin: 0; background: #fff; border: 1px solid #ECE7DC; border-radius: 4px; }
.row {
  display: grid;
  grid-template-columns: 100px 1fr 80px 80px 110px 140px;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-bottom: 1px solid #F2EEE3;
  transition: background 0.15s;
}
.row:last-child { border-bottom: none; }
.row:hover { background: #FAF6EC; }
.order {
  font-size: 13px;
  color: #CA8A04;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 1px;
}
.ch-title {
  font-size: 15px;
  color: #1A1A1A;
}
.meta, .time {
  font-size: 13px;
  color: #888;
  font-family: 'Noto Sans SC', sans-serif;
}
.badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 2px;
  text-align: center;
  font-family: 'Noto Sans SC', sans-serif;
}
.badge.ok { background: #E8F5E9; color: #2E7D32; }
.badge.warn { background: #FFF3E0; color: #E65100; }

.actions { display: flex; gap: 10px; justify-content: flex-end; }
.link {
  background: transparent;
  border: 1px solid #D8D2C4;
  color: #1A1A1A;
  padding: 5px 12px;
  border-radius: 2px;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  font-family: inherit;
}
.link:hover { border-color: #CA8A04; color: #CA8A04; }
.link.danger:hover { border-color: #C62828; color: #C62828; }

@media (max-width: 768px) {
  .head .inner { padding: 14px 16px; flex-wrap: wrap; gap: 10px; }
  .title { font-size: 17px; }
  .main { padding: 24px 16px 60px; }
  .work-item { grid-template-columns: 60px 1fr; gap: 12px; padding: 14px; }
  .work-cover img, .work-cover .cover-fallback { width: 55px; height: 72px; }
  .work-meta { flex-wrap: wrap; gap: 6px 14px; font-size: 12px; }
  .work-actions { flex-direction: column; gap: 6px; }
  .link-btn { font-size: 12px; padding: 5px 10px; }
  .empty { padding: 40px 20px; font-size: 13px; }
  .section-head { flex-direction: column; align-items: flex-start; gap: 10px; }
}
@media (max-width: 480px) {
  .head .inner { padding: 12px 14px; }
  .title { font-size: 15px; }
}
</style>
