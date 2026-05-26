<template>
  <div class="rankings-page">
    <header class="site-header">
      <div class="header-inner">
        <h1 class="logo" @click="goHome">墨香书阁</h1>
        <nav class="main-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
        </nav>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名或作者..."
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="auth-link">登录</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="user-avatar">
              <el-icon :size="20"><User /></el-icon>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <div class="page-hero">
      <div class="hero-content">
        <h2>排行榜</h2>
        <p>RANKINGS</p>
      </div>
      <div class="hero-decoration">
        <div class="trophy-icon">🏆</div>
      </div>
    </div>

    <main class="main-content">
      <div class="tabs-wrapper">
        <div class="rankings-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-name">{{ tab.name }}</span>
          </button>
        </div>
      </div>

      <div class="rankings-content">
        <div class="top-three" v-if="activeTab === 'hot'">
          <div
            v-for="(novel, index) in topThree"
            :key="novel.id"
            :class="['top-card', `rank-${index + 1}`]"
            @click="goToDetail(novel.id)"
          >
            <div class="rank-badge">
              <span class="rank-num">{{ index + 1 }}</span>
              <span class="rank-label">{{ index === 0 ? '桂冠' : index === 1 ? '银冠' : '铜冠' }}</span>
            </div>
            <div class="card-image">
              <img v-lazy="novel.cover" :alt="novel.title" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
              <div class="card-overlay"></div>
            </div>
            <div class="card-info">
              <h3>{{ novel.title }}</h3>
              <p class="author">{{ novel.author }}</p>
              <div class="stats">
                <span><el-icon><View /></el-icon> {{ formatCount(novel.view_count) }}</span>
                <span><el-icon><Star /></el-icon> {{ novel.favorite_count || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="ranking-list">
          <article
            v-for="(novel, index) in rankingList"
            :key="novel.id"
            class="ranking-item"
            @click="goToDetail(novel.id)"
          >
            <div class="item-rank">
              <span class="rank-number" :class="{ top: index < 3 }">{{ getDisplayRank(index) }}</span>
            </div>
            <div class="item-cover">
              <img v-lazy="novel.cover" :alt="novel.title" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
            </div>
            <div class="item-info">
              <h4>{{ novel.title }}</h4>
              <p class="author">{{ novel.author }}</p>
              <p class="category-tag">{{ novel.category }}</p>
            </div>
            <div class="item-stats">
              <div class="stat">
                <span class="stat-label">阅读</span>
                <span class="stat-value">{{ formatCount(novel.view_count) }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">字数</span>
                <span class="stat-value">{{ formatWordCount(novel.word_count) }}</span>
              </div>
            </div>
            <div class="item-action">
              <el-button type="primary" size="small" round @click.stop="goToRead(novel.id)">
                阅读
              </el-button>
            </div>
          </article>
        </div>

        <div class="loading-state" v-if="loading">
          <div class="skeleton-list">
            <div class="skeleton-item" v-for="i in 10" :key="i">
              <div class="skeleton-rank"></div>
              <div class="skeleton-cover"></div>
              <div class="skeleton-info">
                <div class="skeleton-title"></div>
                <div class="skeleton-author"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="site-footer">
      <div class="footer-content">
        <div class="footer-brand">
          <h3>墨香书阁</h3>
          <p>为阅读而生，为故事而活</p>
        </div>
        <p class="copyright">© 2026 墨香书阁. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search, User, View, Star } from '@element-plus/icons-vue'
import { novelApi, type Novel } from '../api'

const router = useRouter()

const searchKeyword = ref('')
const activeTab = ref('hot')
const loading = ref(false)
const allRankings = ref<Novel[]>([])

const isLoggedIn = computed(() => !!localStorage.getItem('user'))

const tabs = [
  { key: 'hot', name: '人气榜', icon: '🔥' },
  { key: 'new', name: '新书榜', icon: '✨' },
  { key: 'complete', name: '完结榜', icon: '📚' },
  { key: 'popular', name: '畅销榜', icon: '💰' },
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

    const res = await novelApi.list(params)
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

const goToRead = (id: number) => {
  router.push({ name: 'Reader', params: { id } })
}

const goHome = () => {
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadRankings()
})

watch(activeTab, () => {
  loadRankings()
})
</script>

<style scoped>
.rankings-page {
  min-height: 100vh;
  background: #faf8f5;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 248, 245, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  cursor: pointer;
  white-space: nowrap;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.main-nav a {
  color: #666;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
  position: relative;
}

.main-nav a:hover {
  color: #1a1a1a;
}

.main-nav a.router-link-active {
  color: #1a1a1a;
  font-weight: 500;
}

.main-nav a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1a1a1a;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.search-input {
  width: 200px;
}

.search-input :deep(.el-input__wrapper) {
  background: #f5f3f0;
  box-shadow: none;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1a1a1a;
  background: #fff;
}

.auth-link {
  color: #666;
  text-decoration: none;
  font-size: 0.9rem;
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #f5f3f0;
  border-radius: 50%;
  color: #666;
  transition: all 0.2s;
}

.user-avatar:hover {
  background: #1a1a1a;
  color: #fff;
}

.page-hero {
  position: relative;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  padding: 4rem 2rem;
  overflow: hidden;
}

.hero-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.hero-content h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 2.5rem;
  color: #fff;
  margin: 0 0 0.5rem;
}

.hero-content p {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 8px;
  margin: 0;
}

.hero-decoration {
  position: absolute;
  right: 10%;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

.trophy-icon {
  font-size: 8rem;
  opacity: 0.15;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.tabs-wrapper {
  margin-bottom: 2rem;
}

.rankings-tabs {
  display: flex;
  gap: 0.5rem;
  background: #fff;
  padding: 0.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.rankings-tabs button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95rem;
  color: #666;
}

.rankings-tabs button:hover {
  background: #f5f3f0;
}

.rankings-tabs button.active {
  background: #1a1a1a;
  color: #fff;
}

.tab-icon {
  font-size: 1.1rem;
}

.tab-name {
  font-weight: 500;
}

.top-three {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.top-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s ease;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.top-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.top-card.rank-1 {
  grid-row: span 2;
  height: 100%;
}

.top-card.rank-1 .card-image {
  height: 100%;
  min-height: 500px;
}

.rank-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  background: linear-gradient(135deg, #ffd700 0%, #ffb800 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(255, 184, 0, 0.4);
}

.rank-2 .rank-badge {
  background: linear-gradient(135deg, #c0c0c0 0%, #a8a8a8 100%);
  box-shadow: 0 4px 12px rgba(168, 168, 168, 0.4);
}

.rank-3 .rank-badge {
  background: linear-gradient(135deg, #cd7f32 0%, #b8702d 100%);
  box-shadow: 0 4px 12px rgba(184, 112, 45, 0.4);
}

.rank-num {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.rank-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 2px;
}

.card-image {
  position: relative;
  height: 280px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.top-card:hover .card-image img {
  transform: scale(1.08);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 50%);
}

.card-info {
  padding: 1.25rem;
}

.card-info h3 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.top-card.rank-1 .card-info h3 {
  font-size: 1.25rem;
}

.author {
  font-size: 0.85rem;
  color: #888;
  margin: 0 0 0.75rem;
}

.stats {
  display: flex;
  gap: 1rem;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #aaa;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 1.25rem;
  background: #fff;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.ranking-item:hover {
  border-color: #1a1a1a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transform: translateX(4px);
}

.item-rank {
  width: 40px;
  text-align: center;
}

.rank-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-family: 'Noto Serif SC', serif;
  font-size: 1rem;
  font-weight: 700;
  color: #888;
  background: #f0f0f0;
  border-radius: 8px;
}

.rank-number.top {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: #fff;
}

.item-cover {
  width: 70px;
  height: 95px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-info h4 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-info .author {
  font-size: 0.8rem;
  color: #888;
  margin: 0 0 0.25rem;
}

.category-tag {
  display: inline-block;
  padding: 2px 10px;
  background: #f5f3f0;
  color: #666;
  font-size: 0.75rem;
  border-radius: 12px;
  margin: 0;
}

.item-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 0.7rem;
  color: #aaa;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.item-action {
  flex-shrink: 0;
}

.item-action :deep(.el-button) {
  background: #1a1a1a;
  border-color: #1a1a1a;
}

.item-action :deep(.el-button:hover) {
  background: #333;
  border-color: #333;
}

.loading-state {
  margin-top: 2rem;
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem 1.25rem;
  background: #fff;
  border-radius: 16px;
}

.skeleton-rank {
  width: 40px;
  height: 32px;
  background: #f0f0f0;
  border-radius: 8px;
}

.skeleton-cover {
  width: 70px;
  height: 95px;
  background: #f0f0f0;
  border-radius: 8px;
}

.skeleton-info {
  flex: 1;
}

.skeleton-title {
  height: 20px;
  width: 60%;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeleton-author {
  height: 14px;
  width: 40%;
  background: #f0f0f0;
  border-radius: 4px;
}

.site-footer {
  background: #111;
  color: #fff;
  padding: 4rem 2rem 2rem;
  margin-top: 4rem;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand h3 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.footer-brand p {
  color: #666;
  margin: 0 0 2rem;
}

.copyright {
  color: #444;
  font-size: 0.85rem;
  margin: 0;
}

@media (max-width: 1024px) {
  .top-three {
    grid-template-columns: repeat(2, 1fr);
  }

  .top-card.rank-1 {
    grid-row: span 1;
  }

  .top-card.rank-1 .card-image {
    min-height: 280px;
    height: 280px;
  }

  .item-stats {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-inner {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .main-nav {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .page-hero {
    padding: 3rem 1.5rem;
  }

  .hero-content h2 {
    font-size: 2rem;
  }

  .hero-decoration {
    display: none;
  }

  .rankings-tabs {
    flex-wrap: wrap;
  }

  .rankings-tabs button {
    flex: 1 1 45%;
  }

  .top-three {
    grid-template-columns: 1fr;
  }

  .top-card {
    display: grid;
    grid-template-columns: 120px 1fr;
    grid-template-rows: auto auto;
  }

  .top-card.rank-1 {
    grid-row: span 1;
  }

  .rank-badge {
    grid-row: span 2;
    position: static;
    flex-direction: row;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
  }

  .card-image {
    height: 160px;
    grid-row: span 1;
  }

  .top-card.rank-1 .card-image {
    min-height: unset;
    height: 160px;
  }

  .card-info {
    grid-column: 2;
  }

  .ranking-item {
    padding: 0.75rem 1rem;
    gap: 0.75rem;
  }

  .item-cover {
    width: 50px;
    height: 70px;
  }

  .item-info h4 {
    font-size: 0.9rem;
  }

  .item-action {
    display: none;
  }
}
</style>
