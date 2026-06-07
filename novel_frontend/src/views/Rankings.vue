<template>
  <div class="rk-root">
    <header class="rk-header">
      <div class="rk-header__inner">
        <h1 class="rk-logo" @click="goHome">墨香书阁</h1>
        <nav class="rk-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/author">创作</router-link>
        </nav>
        <div class="rk-header__actions">
          <div class="rk-header__search">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              v-model="searchKeyword"
              type="text"
              class="rk-header__search-input"
              placeholder="搜索书名或作者..."
              @keyup.enter="handleSearch"
            />
          </div>
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="rk-auth-link">登录</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="rk-user-avatar">
              <img v-if="userAvatar" :src="userAvatar" alt="头像" class="rk-avatar-img" />
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <section class="rk-banner">
      <div class="rk-banner__inner">
        <div class="rk-banner__text">
          <div class="rk-banner__eyebrow">RANKINGS · 书榜</div>
          <h2 class="rk-banner__title">排行榜</h2>
          <p class="rk-banner__desc">汇聚万千读者的阅读选择，发现最受欢迎的好书</p>
        </div>
        <div class="rk-banner__ornament">
          <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
            <circle cx="40" cy="36" r="20" stroke="#CA8A04" stroke-width="1.5" fill="none" opacity="0.3"/>
            <path d="M40 16l5.5 11.2 12.3 1.8-8.9 8.7 2.1 12.3L40 44l-11 5.8 2.1-12.3-8.9-8.7 12.3-1.8L40 16z" fill="#CA8A04" opacity="0.25"/>
            <rect x="28" y="56" width="24" height="4" rx="2" fill="#CA8A04" opacity="0.15"/>
          </svg>
        </div>
      </div>
    </section>

    <main class="rk-main">
      <div class="rk-tabs-section">
        <div class="rk-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="['rk-tab', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            <span class="rk-tab__icon" v-html="tab.svg"></span>
            <span class="rk-tab__name">{{ tab.name }}</span>
          </button>
        </div>
        <p class="rk-tab-desc">{{ tabs.find(t => t.key === activeTab)?.desc }}</p>
      </div>

      <div class="rk-content" v-if="!loading">
        <div class="rk-podium-section" v-if="activeTab === 'hot' && topThree.length > 0">
          <div class="rk-section-divider">
            <div class="rk-section-divider__line"></div>
            <span>TOP 3</span>
            <div class="rk-section-divider__line"></div>
          </div>
          <div class="rk-podium">
            <div
              v-for="(novel, index) in topThree"
              :key="novel.id"
              :class="['rk-podium-card', `rk-podium-card--${index + 1}`]"
              @click="goToDetail(novel.id)"
            >
              <div :class="['rk-medal', `rk-medal--${index + 1}`]">
                <span class="rk-medal__icon" v-html="medalSvgs[index]"></span>
                <span class="rk-medal__num">{{ index + 1 }}</span>
              </div>
              <div class="rk-podium-card__cover">
                <img
                  v-lazy="novel.cover || defaultCover"
                  :alt="novel.title"
                  @error="onCoverError"
                />
                <div class="rk-podium-card__vignette"></div>
              </div>
              <div class="rk-podium-card__info">
                <h3 class="rk-podium-card__title">{{ novel.title }}</h3>
                <p class="rk-podium-card__author">{{ novel.author }}</p>
                <div class="rk-podium-card__stats">
                  <span class="rk-podium-stat">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="rk-podium-stat">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                    {{ novel.favorite_count || 0 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="rk-list-section">
          <div class="rk-section-divider" v-if="activeTab === 'hot'">
            <div class="rk-section-divider__line"></div>
            <span>完整榜单</span>
            <div class="rk-section-divider__line"></div>
          </div>

          <div class="rk-table">
            <article
              v-for="(novel, index) in rankingList"
              :key="novel.id"
              class="rk-row"
              @click="goToDetail(novel.id)"
            >
              <div class="rk-row__rank">
                <span
                  class="rk-rank-badge"
                  :class="{
                    'rk-rank-badge--gold': getDisplayRank(index) === 1,
                    'rk-rank-badge--silver': getDisplayRank(index) === 2,
                    'rk-rank-badge--bronze': getDisplayRank(index) === 3,
                  }"
                >
                  {{ getDisplayRank(index) }}
                </span>
              </div>
              <div class="rk-row__cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'"
                />
              </div>
              <div class="rk-row__info">
                <h4 class="rk-row__title">{{ novel.title }}</h4>
                <p class="rk-row__author">{{ novel.author }}</p>
                <span class="rk-row__category">{{ novel.category }}</span>
              </div>
              <div class="rk-row__stats">
                <div class="rk-row-stat">
                  <span class="rk-row-stat__val">{{ formatCount(novel.view_count) }}</span>
                  <span class="rk-row-stat__lbl">阅读量</span>
                </div>
                <div class="rk-row-stat">
                  <span class="rk-row-stat__val">{{ formatWordCount(novel.word_count) }}</span>
                  <span class="rk-row-stat__lbl">字数</span>
                </div>
              </div>
              <div class="rk-row__action">
                <button class="rk-read-btn" @click.stop="goToDetail(novel.id)">查看</button>
              </div>
            </article>
          </div>
        </div>
      </div>

      <div class="rk-loading" v-if="loading">
        <div class="rk-skeleton-list">
          <div class="rk-skeleton-row" v-for="i in 10" :key="i">
            <div class="rk-sk-rank"></div>
            <div class="rk-sk-cover"></div>
            <div class="rk-sk-info">
              <div class="rk-sk-line rk-sk-line--w55"></div>
              <div class="rk-sk-line rk-sk-line--w35"></div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="rk-footer">
      <div class="rk-footer__inner">
        <div class="rk-footer__brand">
          <span class="rk-footer__logo">墨香书阁</span>
          <span class="rk-footer__slogan">为阅读而生，为故事而活</span>
        </div>
        <p class="rk-footer__copy">&copy; 2026 墨香书阁. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { novelApi } from '../api'
import { DEFAULT_COVER } from '../utils/image'

const defaultCover = DEFAULT_COVER
const onCoverError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== defaultCover) img.src = defaultCover
}

const router = useRouter()

const searchKeyword = ref('')
const activeTab = ref('hot')
const loading = ref(false)
const allRankings = ref<any[]>([])

const isLoggedIn = computed(() => !!localStorage.getItem('user'))
const userAvatar = ref('')

const medalSvgs = [
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="#CA8A04"><circle cx="12" cy="12" r="10" fill="none" stroke="#CA8A04" stroke-width="1.5"/><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>',
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="#9CA3AF"><circle cx="12" cy="12" r="10" fill="none" stroke="#9CA3AF" stroke-width="1.5"/><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>',
  '<svg width="16" height="16" viewBox="0 0 24 24" fill="#B45309"><circle cx="12" cy="12" r="10" fill="none" stroke="#B45309" stroke-width="1.5"/><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>',
]

const tabs = [
  {
    key: 'hot',
    name: '人气榜',
    desc: '按总阅读量排名，反映读者最喜爱的作品',
    svg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c1.5 4 5.5 6 5.5 10a5.5 5.5 0 01-11 0C6.5 8 10.5 6 12 2z"/></svg>',
  },
  {
    key: 'new',
    name: '新书榜',
    desc: '最新上架作品，发现正在崛起的新锐故事',
    svg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
  },
  {
    key: 'complete',
    name: '完结榜',
    desc: '已完结精品，从头到尾的完整阅读体验',
    svg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>',
  },
  {
    key: 'popular',
    name: '畅销榜',
    desc: '收藏最多的作品，口碑与人气双重认证',
    svg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>',
  },
]

const topThree = computed(() => allRankings.value.slice(0, 3))

const rankingList = computed(() => {
  if (activeTab.value === 'hot') {
    return allRankings.value.slice(3)
  }
  return allRankings.value
})

const getDisplayRank = (index: number) => {
  if (activeTab.value === 'hot') {
    return index + 4
  }
  return index + 1
}

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const loadRankings = async () => {
  loading.value = true
  try {
    let params: any = { page_size: 50 }

    switch (activeTab.value) {
      case 'hot':
        params.ordering = '-view_count'
        break
      case 'new':
        params.ordering = '-created_at'
        break
      case 'complete':
        params.status = 1
        params.ordering = '-view_count'
        break
      case 'popular':
        params.ordering = '-favorite_count'
        break
    }

    const res: any = await novelApi.list(params)
    allRankings.value = res.results || []
  } catch (error) {
    console.error('加载排行榜失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ name: 'Search', query: { q: searchKeyword.value } })
  }
}

const goToDetail = (id: number) => {
  router.push({ name: 'NovelDetail', params: { id } })
}

const goHome = () => {
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadRankings()
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    userAvatar.value = user.avatar || ''
  } catch {}
})

watch(activeTab, () => {
  loadRankings()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.rk-root {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-dark: #A67C00;
  --border: #E0E0E0;
  --card-bg: #FFFFFF;

  min-height: 100vh;
  background: var(--paper-bg);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
  color: var(--ink);
}

.rk-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.rk-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.875rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.rk-logo {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  cursor: pointer;
  white-space: nowrap;
  letter-spacing: 0.04em;
}

.rk-nav {
  display: flex;
  gap: 1.75rem;
}

.rk-nav a {
  font-size: 0.9rem;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
  position: relative;
  padding-bottom: 2px;
  cursor: pointer;
}

.rk-nav a:hover {
  color: var(--ink);
}

.rk-nav a.router-link-active {
  color: var(--ink);
  font-weight: 500;
}

.rk-nav a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent);
  border-radius: 1px;
}

.rk-header__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.rk-header__search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.875rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: #F9F7F3;
  transition: border-color 0.2s, background-color 0.2s;
}

.rk-header__search:focus-within {
  border-color: var(--accent);
  background: var(--card-bg);
}

.rk-header__search svg {
  color: #9CA3AF;
  flex-shrink: 0;
}

.rk-header__search-input {
  width: 160px;
  border: none;
  outline: none;
  background: transparent;
  font-size: 0.85rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--ink);
}

.rk-header__search-input::placeholder {
  color: #9CA3AF;
}

.rk-auth-link {
  font-size: 0.875rem;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.rk-auth-link:hover {
  color: var(--ink);
}

.rk-user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--muted);
  transition: border-color 0.2s, color 0.2s;
  cursor: pointer;
}

.rk-user-avatar:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.rk-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.rk-banner {
  background: var(--ink);
  padding: 3.5rem 2rem;
  position: relative;
  overflow: hidden;
}

.rk-banner::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 40px,
    rgba(255, 255, 255, 0.015) 40px,
    rgba(255, 255, 255, 0.015) 80px
  );
}

.rk-banner__inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 2;
}

.rk-banner__eyebrow {
  font-family: 'Cormorant Garamond', serif;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: var(--accent);
  margin-bottom: 0.75rem;
  font-weight: 500;
}

.rk-banner__title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--paper-bg);
  margin: 0 0 0.75rem;
  letter-spacing: 0.05em;
}

.rk-banner__desc {
  font-family: 'Libre Baskerville', 'Noto Sans SC', sans-serif;
  font-size: 0.9rem;
  color: rgba(253, 251, 247, 0.5);
  margin: 0;
  letter-spacing: 0.02em;
}

.rk-banner__ornament {
  flex-shrink: 0;
}

.rk-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

.rk-tabs-section {
  margin-bottom: 2.5rem;
}

.rk-tabs {
  display: flex;
  border-bottom: 1.5px solid var(--border);
  gap: 0;
  margin-bottom: 0.875rem;
}

.rk-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.75rem;
  background: transparent;
  border: none;
  border-bottom: 2.5px solid transparent;
  margin-bottom: -1.5px;
  cursor: pointer;
  font-size: 0.95rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--muted);
  transition: color 0.2s, border-color 0.2s;
  position: relative;
}

.rk-tab:hover {
  color: var(--ink);
}

.rk-tab.active {
  color: var(--ink);
  font-weight: 600;
  border-bottom-color: var(--accent);
}

.rk-tab__icon {
  display: flex;
  align-items: center;
}

.rk-tab__name {
  letter-spacing: 0.02em;
}

.rk-tab-desc {
  font-size: 0.85rem;
  color: #9CA3AF;
  margin: 0;
  padding-left: 0.25rem;
  letter-spacing: 0.02em;
}

.rk-podium-section {
  margin-bottom: 3rem;
}

.rk-section-divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.85rem;
  color: #9CA3AF;
  letter-spacing: 0.1em;
}

.rk-section-divider__line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.rk-podium {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.rk-podium-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.25s, box-shadow 0.25s, opacity 0.25s;
  position: relative;
}

.rk-podium-card:hover {
  border-color: var(--accent);
  box-shadow: 0 8px 32px rgba(202, 138, 4, 0.1);
}

.rk-podium-card--1 {
  border-top: 3px solid var(--accent);
}

.rk-podium-card--2 {
  border-top: 3px solid #9CA3AF;
}

.rk-podium-card--3 {
  border-top: 3px solid #B45309;
}

.rk-medal {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.625rem;
  border-radius: 3px;
  backdrop-filter: blur(4px);
}

.rk-medal--1 {
  background: rgba(202, 138, 4, 0.92);
}

.rk-medal--2 {
  background: rgba(107, 114, 128, 0.88);
}

.rk-medal--3 {
  background: rgba(120, 53, 15, 0.88);
}

.rk-medal__icon {
  display: flex;
  align-items: center;
}

.rk-medal__num {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
}

.rk-podium-card__cover {
  position: relative;
  height: 220px;
  overflow: hidden;
}

.rk-podium-card--1 .rk-podium-card__cover {
  height: 260px;
}

.rk-podium-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.rk-podium-card__vignette {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(26, 26, 26, 0.5) 0%, transparent 50%);
}

.rk-podium-card__info {
  padding: 1.125rem 1.25rem;
}

.rk-podium-card__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.35rem;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rk-podium-card--1 .rk-podium-card__title {
  font-size: 1.1rem;
}

.rk-podium-card__author {
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0 0 0.75rem;
}

.rk-podium-card__stats {
  display: flex;
  gap: 1rem;
}

.rk-podium-stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #9CA3AF;
}

.rk-list-section {
  margin-top: 1rem;
}

.rk-table {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
  background: var(--card-bg);
}

.rk-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid #F3F4F6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.rk-row:last-child {
  border-bottom: none;
}

.rk-row:hover {
  background: #FFFBEF;
}

.rk-row__rank {
  width: 36px;
  text-align: center;
  flex-shrink: 0;
}

.rk-rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  font-family: 'Noto Serif SC', serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: #9CA3AF;
  background: #F3F4F6;
  border-radius: 3px;
}

.rk-rank-badge--gold {
  background: var(--accent);
  color: #fff;
}

.rk-rank-badge--silver {
  background: #6B7280;
  color: #fff;
}

.rk-rank-badge--bronze {
  background: #92400E;
  color: #fff;
}

.rk-row__cover {
  flex-shrink: 0;
  width: 52px;
  height: 72px;
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.rk-row__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.rk-row__info {
  flex: 1;
  min-width: 0;
}

.rk-row__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rk-row__author {
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0 0 0.3rem;
}

.rk-row__category {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  background: #F3F4F6;
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.72rem;
  border-radius: 2px;
}

.rk-row__stats {
  display: flex;
  gap: 2rem;
  flex-shrink: 0;
}

.rk-row-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.rk-row-stat__val {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
}

.rk-row-stat__lbl {
  font-size: 0.7rem;
  color: #9CA3AF;
}

.rk-row__action {
  flex-shrink: 0;
}

.rk-read-btn {
  padding: 0.35rem 1.125rem;
  background: transparent;
  border: 1px solid var(--ink);
  border-radius: 2px;
  font-size: 0.82rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--ink);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  letter-spacing: 0.04em;
}

.rk-read-btn:hover {
  background: var(--ink);
  color: var(--paper-bg);
}

.rk-row:hover .rk-read-btn {
  border-color: var(--accent);
  color: var(--accent);
}

.rk-row:hover .rk-read-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.rk-loading {
  margin-top: 1rem;
}

.rk-skeleton-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.rk-skeleton-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 0.875rem 1.25rem;
  background: var(--card-bg);
  border-bottom: 1px solid #F3F4F6;
}

.rk-skeleton-row:last-child {
  border-bottom: none;
}

.rk-sk-rank {
  width: 30px;
  height: 30px;
  background: linear-gradient(90deg, #F0EDE8 25%, #E8E4DC 50%, #F0EDE8 75%);
  background-size: 200% 100%;
  border-radius: 3px;
  animation: rk-shimmer 1.5s infinite;
  flex-shrink: 0;
}

.rk-sk-cover {
  width: 52px;
  height: 72px;
  background: linear-gradient(90deg, #F0EDE8 25%, #E8E4DC 50%, #F0EDE8 75%);
  background-size: 200% 100%;
  border-radius: 3px;
  animation: rk-shimmer 1.5s infinite;
  flex-shrink: 0;
}

.rk-sk-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.rk-sk-line {
  height: 12px;
  background: linear-gradient(90deg, #F0EDE8 25%, #E8E4DC 50%, #F0EDE8 75%);
  background-size: 200% 100%;
  border-radius: 2px;
  animation: rk-shimmer 1.5s infinite;
}

.rk-sk-line--w35 { width: 35%; }
.rk-sk-line--w55 { width: 55%; }

@keyframes rk-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.rk-footer {
  background: #111;
  padding: 3rem 2rem 2rem;
  margin-top: 5rem;
}

.rk-footer__inner {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.rk-footer__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.rk-footer__logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--paper-bg);
  letter-spacing: 0.04em;
}

.rk-footer__slogan {
  font-size: 0.85rem;
  color: #4B5563;
}

.rk-footer__copy {
  font-size: 0.8rem;
  color: #374151;
  margin: 0;
}

@media (max-width: 1024px) {
  .rk-podium {
    grid-template-columns: repeat(2, 1fr);
  }

  .rk-podium-card--1 {
    grid-column: 1 / -1;
  }

  .rk-podium-card--1 .rk-podium-card__cover {
    height: 260px;
  }

  .rk-row__stats {
    display: none;
  }
}

@media (max-width: 768px) {
  .rk-header__inner {
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .rk-nav {
    order: 3;
    width: 100%;
  }

  .rk-banner {
    padding: 2.5rem 1.25rem;
  }

  .rk-banner__title {
    font-size: 1.875rem;
  }

  .rk-banner__ornament {
    display: none;
  }

  .rk-main {
    padding: 1.5rem 1rem;
  }

  .rk-podium {
    grid-template-columns: 1fr;
  }

  .rk-podium-card--1 {
    grid-column: auto;
  }

  .rk-podium-card__cover {
    height: 200px;
  }

  .rk-podium-card--1 .rk-podium-card__cover {
    height: 220px;
  }

  .rk-tabs {
    overflow-x: auto;
  }

  .rk-tab {
    padding: 0.75rem 1.25rem;
    white-space: nowrap;
  }

  .rk-row {
    padding: 0.75rem 0.875rem;
    gap: 0.875rem;
  }

  .rk-row__action {
    display: none;
  }

  .rk-header__search {
    display: none;
  }
}

@media (max-width: 375px) {
  .rk-banner {
    padding: 2rem 1rem;
  }

  .rk-banner__title {
    font-size: 1.5rem;
  }

  .rk-main {
    padding: 1rem 0.75rem;
  }

  .rk-row__cover {
    width: 44px;
    height: 60px;
  }
}
</style>
