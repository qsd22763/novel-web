<template>
  <div class="novel-detail">
    <header class="site-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="logo" @click="goHome">墨香书阁</h1>
          <nav v-if="novel" class="breadcrumb" aria-label="breadcrumb">
            <span class="bc-item bc-link" @click="goHome">首页</span>
            <span class="bc-sep">/</span>
            <span class="bc-item bc-link" @click="goToCategory">{{ novel.category }}</span>
            <span class="bc-sep">/</span>
            <span class="bc-item bc-current">{{ novel.title }}</span>
          </nav>
        </div>
        <div class="header-actions">
          <button v-if="!isLoggedIn" class="btn-login" @click="goLogin">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            登录
          </button>
          <button v-else class="btn-user" @click="goUserCenter">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            用户中心
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div v-if="loading" class="loading-state">
        <div class="skeleton-hero">
          <div class="skeleton-block skeleton-shimmer"></div>
        </div>
        <div class="skeleton-info">
          <div class="skeleton-cover skeleton-shimmer"></div>
          <div class="skeleton-meta">
            <div class="skeleton-line skeleton-shimmer" style="width:60%;height:28px"></div>
            <div class="skeleton-line skeleton-shimmer" style="width:40%;height:16px"></div>
            <div class="skeleton-line skeleton-shimmer" style="width:80%;height:48px"></div>
            <div class="skeleton-line skeleton-shimmer" style="width:50%;height:44px"></div>
          </div>
        </div>
        <div class="skeleton-desc">
          <div class="skeleton-line skeleton-shimmer" style="width:100%;height:16px"></div>
          <div class="skeleton-line skeleton-shimmer" style="width:90%;height:16px"></div>
          <div class="skeleton-line skeleton-shimmer" style="width:75%;height:16px"></div>
        </div>
        <div class="skeleton-chapters">
          <div v-for="i in 8" :key="i" class="skeleton-chapter skeleton-shimmer"></div>
        </div>
      </div>

      <template v-else-if="novel">
        <section class="hero-section">
          <div class="hero-blur-bg">
            <img :src="novel.cover" :alt="novel.title" class="hero-blur-img" />
          </div>
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-cover-frame">
              <img :src="novel.cover" :alt="novel.title" class="hero-cover-img" />
            </div>
            <div class="hero-meta">
              <h1 class="hero-title">{{ novel.title }}</h1>
              <p class="hero-author">{{ novel.author }}</p>
              <div class="hero-tags">
                <span class="tag tag-category">{{ novel.category }}</span>
                <span class="tag" :class="novel.status === 1 ? 'tag-complete' : 'tag-ongoing'">
                  {{ novel.status === 1 ? '已完结' : '连载中' }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <div class="content-wrapper">
          <section class="info-section">
            <div class="info-layout">
              <div class="info-left">
                <div class="cover-card">
                  <img :src="novel.cover" :alt="novel.title" class="side-cover" />
                  <div class="cover-spine"></div>
                </div>
              </div>
              <div class="info-right">
                <div class="stats-bar">
                  <div class="stat-cell">
                    <span class="stat-num">{{ formatCount(novel.word_count || 0) }}</span>
                    <span class="stat-lbl">字数</span>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-cell">
                    <span class="stat-num">{{ formatCount(novel.view_count || 0) }}</span>
                    <span class="stat-lbl">阅读</span>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-cell">
                    <span class="stat-num">{{ novel.chapter_count || chapters.length }}</span>
                    <span class="stat-lbl">章节</span>
                  </div>
                </div>
                <div class="action-buttons">
                  <button class="btn-read" @click="startReading">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    开始阅读
                  </button>
                  <button
                    v-if="isLoggedIn"
                    class="btn-favorite"
                    :class="{ favorited: isFavorited }"
                    @click="toggleFavorite"
                  >
                    <Transition name="heart" mode="out-in">
                      <svg v-if="isFavorited" key="filled" width="18" height="18" viewBox="0 0 24 24" fill="#CA8A04" stroke="#CA8A04" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                      <svg v-else key="outline" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    </Transition>
                    {{ isFavorited ? '已收藏' : '收藏' }}
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="description-section">
            <div class="section-header">
              <span class="section-title">内容简介</span>
              <div class="section-line"></div>
            </div>
            <div class="description-body" :class="{ collapsed: !descExpanded }">
              <p class="description-text">{{ novel.description || '暂无简介' }}</p>
            </div>
            <button
              v-if="novel.description && novel.description.length > 120"
              class="expand-btn"
              @click="descExpanded = !descExpanded"
            >
              {{ descExpanded ? '收起' : '展开全文' }}
              <svg v-if="!descExpanded" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
            </button>
          </section>

          <section class="chapter-section">
            <div class="section-header">
              <span class="section-title">章节目录</span>
              <span class="chapter-count">共 {{ chapters.length }} 章</span>
              <div class="section-line"></div>
            </div>
            <div v-if="chapters.length > 0" class="chapter-grid">
              <div
                v-for="chapter in chapters"
                :key="chapter.id"
                class="chapter-item"
                :class="{ 'chapter-read': isChapterRead(chapter.id) }"
                @click="goToRead(chapter.id)"
              >
                <span class="chapter-name">{{ chapter.title }}</span>
                <svg v-if="isChapterRead(chapter.id)" class="read-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </div>
            <div v-else class="chapter-empty">暂无章节</div>
          </section>

          <section class="comment-section">
            <div class="section-header">
              <span class="section-title">书评 · 评分</span>
              <span class="chapter-count">
                共 {{ commentStats.comment_count }} 条 / 平均 {{ commentStats.avg_rating || '—' }}
              </span>
              <div class="section-line"></div>
            </div>

            <div class="comment-form">
              <div class="rating-row">
                <span class="rating-label">评分</span>
                <div class="stars">
                  <span
                    v-for="i in 5"
                    :key="i"
                    class="star"
                    :class="{ active: i <= newRating }"
                    @click="newRating = (newRating === i ? 0 : i)"
                  >★</span>
                </div>
                <span class="rating-tip">{{ newRating ? newRating + ' 星' : '不打分（仅评论）' }}</span>
              </div>
              <textarea
                v-model="newContent"
                class="comment-input"
                placeholder="留下你的评论…（最多 500 字）"
                maxlength="500"
                rows="3"
              ></textarea>
              <div class="comment-actions">
                <span class="counter">{{ newContent.length }} / 500</span>
                <button class="comment-submit" :disabled="submitting || !newContent.trim()" @click="onSubmitComment">
                  {{ submitting ? '发表中…' : '发表评论' }}
                </button>
              </div>
            </div>

            <ul v-if="comments.length" class="comment-list">
              <li v-for="c in comments" :key="c.id" class="comment-item">
                <div class="avatar">{{ (c.username || 'U').slice(0, 1) }}</div>
                <div class="comment-body">
                  <div class="comment-head">
                    <span class="comment-user">{{ c.username }}</span>
                    <span v-if="c.rating > 0" class="comment-rating">
                      <span v-for="i in 5" :key="i" class="mini-star" :class="{ on: i <= c.rating }">★</span>
                    </span>
                    <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                  </div>
                  <p class="comment-text">{{ c.content }}</p>
                </div>
              </li>
            </ul>
            <div v-else class="comment-empty">还没有评论，来抢第一条吧。</div>
          </section>
        </div>
      </template>

      <div v-else class="error-state">
        <svg class="error-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <p class="error-text">小说不存在或加载失败</p>
        <button class="btn-retry" @click="loadNovelDetail">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          重新加载
        </button>
      </div>
    </main>

    <footer class="site-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { novelApi, favoriteApi, progressApi, commentApi, type Novel, type Chapter, type NovelComment } from '../api'

const route = useRoute()
const router = useRouter()
const novel = ref<Novel | null>(null)
const chapters = ref<Chapter[]>([])
const isFavorited = ref(false)
const readChapterIds = ref<Set<number>>(new Set())
const loading = ref(false)
const descExpanded = ref(false)

const comments = ref<NovelComment[]>([])
const commentStats = ref({ comment_count: 0, rating_count: 0, avg_rating: 0 })
const newContent = ref('')
const newRating = ref(0)
const submitting = ref(false)

const formatTime = (s: string) => {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const loadComments = async (novelId: number) => {
  try {
    const [listRes, statsRes]: any = await Promise.all([
      commentApi.list(novelId),
      commentApi.stats(novelId),
    ])
    comments.value = listRes.results || listRes
    commentStats.value = statsRes
  } catch (e) {
    console.error('加载评论失败', e)
  }
}

const onSubmitComment = async () => {
  if (!novel.value) return
  if (!localStorage.getItem('user')) {
    ElMessage.warning('请先登录后再发表评论')
    router.push('/login')
    return
  }
  if (!newContent.value.trim()) return
  submitting.value = true
  try {
    await commentApi.add({ novel: novel.value.id, content: newContent.value.trim(), rating: newRating.value })
    newContent.value = ''
    newRating.value = 0
    await loadComments(novel.value.id)
    ElMessage.success('评论已发表')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '发表失败')
  } finally {
    submitting.value = false
  }
}

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('user')
})

const formatCount = (num: number): string => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return String(num)
}

const isChapterRead = (chapterId: number) => readChapterIds.value.has(chapterId)

const loadReadChapters = async (novelId: number) => {
  try {
    const res: any = await progressApi.list()
    const readIds = new Set<number>()
    ;(res.results || []).forEach((progress: any) => {
      if (progress.novel === novelId && progress.chapter) {
        readIds.add(progress.chapter)
      }
    })
    readChapterIds.value = readIds
  } catch (error) {
    console.error('获取阅读记录失败:', error)
  }
}

const loadNovelDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const [novelRes, chaptersRes] = await Promise.all([
      novelApi.detail(id),
      novelApi.chapters(id),
    ])
    novel.value = novelRes
    chapters.value = (chaptersRes as any).chapters || (chaptersRes as any).results || []
    loadComments(id)
    if (isLoggedIn.value) {
      checkFavorite(id)
      loadReadChapters(id)
    }
  } catch (error) {
    console.error('加载小说详情失败:', error)
    novel.value = null
  } finally {
    loading.value = false
  }
}

const checkFavorite = async (novelId: number) => {
  try {
    const res: any = await favoriteApi.check(novelId)
    isFavorited.value = res.is_favorited
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }
}

const toggleFavorite = async () => {
  if (!novel.value) return
  try {
    if (isFavorited.value) {
      await favoriteApi.remove(novel.value.id)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.add(novel.value.id)
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (error: any) {
    const detail = error?.response?.data
    if (typeof detail === 'object' && detail !== null) {
      const msgs = []
      for (const key of Object.keys(detail)) {
        const val = detail[key]
        if (Array.isArray(val)) msgs.push(val.join(' '))
        else if (typeof val === 'string') msgs.push(val)
      }
      if (msgs.length) { ElMessage.error(msgs.join('; ')); return }
    }
    ElMessage.error(error?.response?.data?.detail || error?.response?.data?.message || '操作失败')
  }
}

const startReading = async () => {
  if (!novel.value || chapters.value.length === 0) return

  if (isLoggedIn.value) {
    try {
      const res: any = await progressApi.get(novel.value.id)
      if (res.chapter_id) {
        goToRead(res.chapter_id)
        return
      }
    } catch (error) {
      console.log('获取阅读进度失败，使用默认行为')
    }
  }

  goToRead(chapters.value[0].id)
}

const goToRead = (chapterId: number) => {
  router.push({ name: 'Reader', params: { id: chapterId } })
}

const goToCategory = () => {
  if (novel.value) {
    router.push({ name: 'NovelList', query: { category: novel.value.category } })
  }
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const goLogin = () => {
  router.push({ name: 'Login' })
}

const goUserCenter = () => {
  router.push({ name: 'UserCenter' })
}

onMounted(() => {
  loadNovelDetail()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500&display=swap');

:root {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-hover: #A97702;
  --border: #E0E0E0;
  --card-bg: #FFFFFF;
  --font-title: 'Cormorant Garamond', 'Noto Serif SC', serif;
  --font-body: 'Libre Baskerville', 'Noto Sans SC', sans-serif;
  --font-serif-cn: 'Noto Serif SC', serif;
  --font-sans-cn: 'Noto Sans SC', sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.novel-detail {
  min-height: 100vh;
  background: var(--paper-bg);
  color: var(--ink);
  font-family: var(--font-body);
}

.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  font-family: var(--font-serif-cn);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--ink);
  cursor: pointer;
  letter-spacing: 4px;
  user-select: none;
  transition: opacity 200ms;
}

.logo:hover {
  opacity: 0.7;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-sans-cn);
  font-size: 0.82rem;
}

.bc-item {
  color: var(--muted);
}

.bc-link {
  cursor: pointer;
  transition: color 200ms;
}

.bc-link:hover {
  color: var(--accent);
}

.bc-sep {
  color: var(--border);
  font-size: 0.75rem;
}

.bc-current {
  color: var(--ink);
  font-weight: 500;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-login,
.btn-user {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--ink);
  font-family: var(--font-sans-cn);
  font-size: 0.82rem;
  padding: 7px 18px;
  border-radius: 2px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: border-color 200ms, color 200ms, background 200ms;
}

.btn-login:hover,
.btn-user:hover {
  border-color: var(--ink);
  background: var(--ink);
  color: var(--paper-bg);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 64px 2rem 0;
  min-height: calc(100vh - 80px);
}

.loading-state {
  padding: 3rem 0;
}

.skeleton-shimmer {
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5df 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 3px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-hero {
  width: 100%;
  height: 320px;
  margin-bottom: 2.5rem;
  border-radius: 4px;
  overflow: hidden;
}

.skeleton-block {
  width: 100%;
  height: 100%;
}

.skeleton-info {
  display: flex;
  gap: 3rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid var(--border);
}

.skeleton-cover {
  width: 180px;
  height: 250px;
  flex-shrink: 0;
}

.skeleton-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 0.5rem;
}

.skeleton-line {
  border-radius: 3px;
}

.skeleton-desc {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2.5rem;
  border-bottom: 1px solid var(--border);
}

.skeleton-chapters {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.skeleton-chapter {
  height: 40px;
}

.hero-section {
  position: relative;
  width: 100%;
  height: 340px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 3rem;
  margin-top: 2rem;
}

.hero-blur-bg {
  position: absolute;
  inset: -20px;
}

.hero-blur-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(24px) brightness(0.45) saturate(0.7);
  transform: scale(1.15);
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(26,26,26,0.2) 0%, rgba(26,26,26,0.65) 100%);
}

.hero-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 2rem;
  text-align: center;
}

.hero-cover-frame {
  width: 120px;
  height: 168px;
  border-radius: 3px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 12px 40px rgba(0,0,0,0.5);
  border: 1px solid rgba(255,255,255,0.12);
}

.hero-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.hero-title {
  font-family: var(--font-serif-cn);
  font-size: clamp(2rem, 4vw, 3.5rem);
  font-weight: 700;
  color: #fff;
  letter-spacing: 4px;
  text-shadow: 0 2px 12px rgba(0,0,0,0.4);
  line-height: 1.2;
}

.hero-author {
  font-family: var(--font-sans-cn);
  font-size: 0.95rem;
  color: rgba(255,255,255,0.7);
  letter-spacing: 2px;
}

.hero-tags {
  display: flex;
  gap: 0.6rem;
  margin-top: 0.25rem;
}

.tag {
  font-family: var(--font-sans-cn);
  font-size: 0.72rem;
  padding: 3px 12px;
  border-radius: 2px;
  letter-spacing: 1px;
}

.tag-category {
  background: rgba(202,138,4,0.2);
  color: #FFD066;
  border: 1px solid rgba(202,138,4,0.4);
}

.tag-complete {
  background: rgba(107,114,128,0.2);
  color: #D1D5DB;
  border: 1px solid rgba(107,114,128,0.4);
}

.tag-ongoing {
  background: rgba(34,197,94,0.15);
  color: #86EFAC;
  border: 1px solid rgba(34,197,94,0.35);
}

.content-wrapper {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 3rem;
}

.info-section {
  margin-bottom: 3rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid var(--border);
}

.info-layout {
  display: flex;
  gap: 3rem;
  align-items: flex-start;
}

.info-left {
  flex-shrink: 0;
}

.cover-card {
  position: relative;
  width: 180px;
}

.side-cover {
  width: 180px;
  height: 250px;
  object-fit: cover;
  border-radius: 2px 4px 4px 2px;
  box-shadow: 6px 8px 24px rgba(0,0,0,0.15);
  display: block;
}

.cover-spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(180deg, #CA8A04 0%, #92600A 100%);
  border-radius: 2px 0 0 2px;
}

.info-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding-top: 0.25rem;
}

.stats-bar {
  display: flex;
  align-items: center;
  background: #F9F7F3;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 1.25rem 0;
  width: fit-content;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 2.5rem;
}

.stat-num {
  font-family: var(--font-title);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 1px;
}

.stat-lbl {
  font-family: var(--font-sans-cn);
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 4px;
  letter-spacing: 2px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border);
}

.action-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-read {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 12px 32px;
  border-radius: 2px;
  font-size: 0.92rem;
  font-family: var(--font-sans-cn);
  cursor: pointer;
  letter-spacing: 2px;
  transition: background 200ms, opacity 200ms;
}

.btn-read:hover {
  background: var(--accent-hover);
}

.btn-read:active {
  opacity: 0.85;
}

.btn-favorite {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--border);
  padding: 11px 24px;
  border-radius: 2px;
  font-size: 0.88rem;
  font-family: var(--font-sans-cn);
  cursor: pointer;
  letter-spacing: 1px;
  transition: border-color 200ms, color 200ms;
}

.btn-favorite:hover,
.btn-favorite.favorited {
  border-color: var(--accent);
  color: var(--accent);
}

/* Vue Transition: 心形收藏动画 */
.heart-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.heart-leave-active {
  transition: all 0.2s ease-in;
}
.heart-enter-from {
  opacity: 0;
  transform: scale(0.3) rotate(-15deg);
}
.heart-leave-to {
  opacity: 0;
  transform: scale(1.4) rotate(10deg);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-title {
  font-family: var(--font-serif-cn);
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 3px;
  white-space: nowrap;
  position: relative;
  padding-left: 14px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  background: var(--accent);
  border-radius: 2px;
}

.section-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.chapter-count {
  font-family: var(--font-sans-cn);
  font-size: 0.78rem;
  color: var(--muted);
  white-space: nowrap;
  letter-spacing: 1px;
}

.description-section {
  margin-bottom: 3rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid var(--border);
}

.description-body {
  overflow: hidden;
  transition: max-height 300ms ease;
  max-height: 9999px;
}

.description-body.collapsed {
  max-height: 5.7em;
  position: relative;
}

.description-body.collapsed::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2.5em;
  background: linear-gradient(to bottom, transparent, var(--card-bg));
}

.description-text {
  color: var(--muted);
  line-height: 1.9;
  font-size: 0.92rem;
  font-family: var(--font-serif-cn);
  letter-spacing: 0.5px;
}

.expand-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.75rem;
  background: none;
  border: none;
  color: var(--accent);
  font-size: 0.82rem;
  cursor: pointer;
  font-family: var(--font-sans-cn);
  letter-spacing: 1px;
  padding: 0;
  transition: opacity 200ms;
}

.expand-btn:hover {
  opacity: 0.75;
}

.chapter-section {
  margin-bottom: 0;
}

.chapter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
}

.chapter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #F9F7F3;
  border: 1px solid transparent;
  border-radius: 2px;
  cursor: pointer;
  font-family: var(--font-sans-cn);
  font-size: 0.85rem;
  color: var(--ink);
  transition: border-color 200ms, color 200ms, background 200ms;
  overflow: hidden;
}

.chapter-item:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(202,138,4,0.04);
}

.chapter-item.chapter-read {
  color: var(--muted);
  background: #F5F5F5;
}

.chapter-item.chapter-read:hover {
  color: var(--accent);
  background: rgba(202,138,4,0.04);
  border-color: var(--accent);
}

.chapter-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.read-icon {
  flex-shrink: 0;
  margin-left: 6px;
  color: var(--muted);
  transition: color 200ms;
}

.chapter-item:hover .read-icon {
  color: var(--accent);
}

.chapter-empty {
  color: var(--muted);
  font-family: var(--font-sans-cn);
  font-size: 0.88rem;
  padding: 3rem 0;
  text-align: center;
  letter-spacing: 1px;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  gap: 1.25rem;
}

.error-icon {
  color: var(--border);
}

.error-text {
  font-family: var(--font-sans-cn);
  font-size: 0.92rem;
  color: var(--muted);
  letter-spacing: 1px;
}

.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--ink);
  font-family: var(--font-sans-cn);
  font-size: 0.85rem;
  padding: 9px 24px;
  border-radius: 2px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: border-color 200ms, background 200ms, color 200ms;
}

.btn-retry:hover {
  border-color: var(--ink);
  background: var(--ink);
  color: var(--paper-bg);
}

.site-footer {
  text-align: center;
  padding: 2.5rem;
  color: var(--muted);
  font-family: var(--font-serif-cn);
  font-size: 0.82rem;
  letter-spacing: 2px;
  border-top: 1px solid var(--border);
  margin-top: 3rem;
}

@media (max-width: 1024px) {
  .content-wrapper {
    padding: 2.5rem;
  }

  .stat-cell {
    padding: 0 2rem;
  }
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 1.25rem;
    height: 56px;
  }

  .header-left {
    gap: 1rem;
  }

  .breadcrumb {
    display: none;
  }

  .main-content {
    padding: 56px 1.25rem 0;
  }

  .hero-section {
    height: 280px;
    margin-top: 1rem;
    margin-bottom: 2rem;
  }

  .hero-cover-frame {
    width: 90px;
    height: 126px;
  }

  .hero-title {
    letter-spacing: 2px;
  }

  .content-wrapper {
    padding: 1.5rem;
  }

  .info-layout {
    flex-direction: column;
    gap: 2rem;
    align-items: center;
  }

  .cover-card {
    width: 140px;
  }

  .side-cover {
    width: 140px;
    height: 195px;
  }

  .info-right {
    align-items: center;
    text-align: center;
  }

  .stats-bar {
    width: 100%;
    justify-content: center;
  }

  .stat-cell {
    padding: 0 1.5rem;
  }

  .action-buttons {
    justify-content: center;
  }

  .chapter-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}

@media (max-width: 375px) {
  .header-inner {
    padding: 0 1rem;
  }

  .logo {
    font-size: 1.2rem;
    letter-spacing: 2px;
  }

  .main-content {
    padding: 56px 1rem 0;
  }

  .hero-section {
    height: 240px;
  }

  .hero-cover-frame {
    width: 80px;
    height: 112px;
  }

  .content-wrapper {
    padding: 1.25rem;
  }

  .stat-cell {
    padding: 0 1rem;
  }

  .stat-num {
    font-size: 1.2rem;
  }

  .btn-read {
    padding: 10px 24px;
    font-size: 0.85rem;
  }

  .btn-favorite {
    padding: 9px 18px;
    font-size: 0.82rem;
  }

  .chapter-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}

.comment-section {
  margin-top: 56px;
}
.comment-form {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 22px 24px;
  margin-bottom: 24px;
}
.rating-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
  font-family: var(--font-sans-cn);
}
.rating-label { font-size: 14px; color: var(--muted); }
.stars { display: flex; gap: 4px; }
.star {
  font-size: 22px;
  color: #D8D2C4;
  cursor: pointer;
  transition: color 0.15s;
  user-select: none;
}
.star.active { color: var(--accent); }
.rating-tip { font-size: 13px; color: var(--muted); }
.comment-input {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--paper-bg);
  padding: 12px 14px;
  font-family: var(--font-serif-cn);
  font-size: 15px;
  line-height: 1.7;
  border-radius: 2px;
  outline: none;
  resize: vertical;
  box-sizing: border-box;
}
.comment-input:focus { border-color: var(--accent); }
.comment-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  margin-top: 12px;
}
.counter { font-size: 12px; color: #999; font-family: var(--font-sans-cn); }
.comment-submit {
  background: #B7830A;
  color: #fff;
  border: none;
  padding: 9px 26px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 3px;
  cursor: pointer;
  font-family: var(--font-sans-cn);
  letter-spacing: 1px;
  box-shadow: 0 1px 3px rgba(180,125,10,0.35);
}
.comment-submit:hover { background: #A67503; box-shadow: 0 2px 5px rgba(180,125,10,0.45); }
.comment-submit:disabled { opacity: 0.4; cursor: not-allowed; box-shadow: none; }

.comment-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 16px; }
.comment-item {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 18px 20px;
  display: flex;
  gap: 14px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #CA8A04, #A87403);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}
.comment-body { flex: 1; }
.comment-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  font-family: var(--font-sans-cn);
}
.comment-user { font-weight: 600; color: var(--ink); font-size: 14px; }
.comment-rating { display: inline-flex; gap: 1px; }
.mini-star { color: #D8D2C4; font-size: 13px; }
.mini-star.on { color: var(--accent); }
.comment-time { color: #999; font-size: 12px; margin-left: auto; }
.comment-text {
  margin: 0;
  color: var(--ink);
  font-size: 15px;
  line-height: 1.8;
  font-family: var(--font-serif-cn);
  white-space: pre-wrap;
  word-break: break-word;
}
.comment-empty {
  background: var(--card-bg);
  border: 1px dashed var(--border);
  border-radius: 4px;
  padding: 40px;
  text-align: center;
  color: #888;
  font-family: var(--font-sans-cn);
}
</style>
