<template>
  <div class="home-page">

    <!-- ===== HEADER ===== -->
    <header class="site-header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <span class="logo-text">墨香书阁</span>
        </router-link>

        <nav class="main-nav">
          <router-link to="/" class="nav-link" :class="{ active: currentRoute === '/' }">首页</router-link>
          <router-link to="/novels" class="nav-link" :class="{ active: currentRoute === '/novels' }">书库</router-link>
          <router-link to="/rankings" class="nav-link" :class="{ active: currentRoute === '/rankings' }">排行榜</router-link>
          <router-link to="/author" class="nav-link" :class="{ active: currentRoute.startsWith('/author') }">创作</router-link>
        </nav>

        <div class="header-actions">
          <div class="search-box" @click="focusSearch">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              ref="searchInput"
              v-model="searchKeyword"
              class="search-input"
              placeholder="搜索书名或作者…"
              @keyup.enter="handleSearch"
            />
          </div>

          <template v-if="!isLoggedIn">
            <router-link to="/login" class="action-btn action-btn--text">登录</router-link>
            <router-link to="/login" class="action-btn action-btn--primary">注册</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="user-menu">
              <svg class="user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="12" cy="8" r="4"/>
                <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
              </svg>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">

      <!-- ===== HERO ===== -->
      <section class="hero-section">
        <div class="hero-bg"></div>
        <div class="hero-inner">
          <div class="hero-content">
            <p class="hero-badge">精选文学 · 沉浸阅读</p>
            <h1 class="hero-title">在文字间<br/>发现新世界</h1>
            <p class="hero-desc">海量免费小说，让阅读成为一种享受</p>
            <div class="hero-actions">
              <router-link to="/novels" class="btn btn-primary">开始探索</router-link>
              <router-link to="/rankings" class="btn btn-secondary">热门排行</router-link>
            </div>
          </div>
          <div class="hero-book-showcase">
            <div
              v-for="(novel, i) in featuredNovels.slice(0, 5)"
              :key="novel.id"
              class="book-item"
              :class="`book-${i + 1}`"
              @click="goToDetail(novel.id)"
            >
              <img
                v-lazy="novel.cover"
                :alt="novel.title"
                class="book-cover"
                @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
              />
              <div class="book-overlay">
                <span class="book-title">{{ novel.title }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== QUICK STATS ===== -->
      <section class="quick-stats">
        <div class="stats-container">
          <div class="stat-item">
            <span class="stat-value">10K+</span>
            <span class="stat-label">精选小说</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">500万+</span>
            <span class="stat-label">阅读次数</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">100%</span>
            <span class="stat-label">免费阅读</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">每日更新</span>
            <span class="stat-label">持续更新</span>
          </div>
        </div>
      </section>

      <!-- ===== FEATURED NOVELS ===== -->
      <section class="featured-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">精选推荐</span>
              <h2 class="section-title">编辑精选</h2>
            </div>
            <router-link to="/novels" class="see-all">查看全部</router-link>
          </div>

          <div class="featured-grid">
            <article
              v-for="(novel, index) in featuredNovels.slice(0, 6)"
              :key="novel.id"
              class="novel-card"
              @click="goToDetail(novel.id)"
            >
              <div class="card-cover-wrap">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  class="card-cover"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
                <span class="card-category">{{ novel.category }}</span>
                <div class="card-hover-overlay">
                  <span class="hover-text">开始阅读</span>
                </div>
              </div>
              <div class="card-content">
                <h3 class="card-title">{{ novel.title }}</h3>
                <p class="card-author">{{ novel.author }}</p>
                <div v-if="novel.tags" class="card-tags">
                  <span v-for="tag in novel.tags.split(',').map(t=>t.trim()).filter(Boolean)" :key="tag" class="card-tag">{{ tag }}</span>
                </div>
                <p class="card-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="meta-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                    {{ formatWordCount(novel.word_count) }}
                  </span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ===== CATEGORIES ===== -->
      <section class="categories-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">分类浏览</span>
              <h2 class="section-title">探索分类</h2>
            </div>
          </div>

          <div class="categories-grid">
            <div
              v-for="cat in categories"
              :key="cat.name"
              class="category-card"
              :style="{ '--category-color': cat.color }"
              @click="goToCategory(cat.name)"
            >
              <div class="cat-icon">
                <svg v-if="cat.name === '玄幻'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                  <path d="M2 17l10 5 10-5"/>
                  <path d="M2 12l10 5 10-5"/>
                </svg>
                <svg v-else-if="cat.name === '都市'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                <svg v-else-if="cat.name === '穿越'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <svg v-else-if="cat.name === '科幻'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 2v4M12 18v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M2 12h4M18 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
                </svg>
                <svg v-else-if="cat.name === '游戏'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="2" y="6" width="20" height="12" rx="2"/>
                  <path d="M6 12h4M8 10v4"/>
                  <circle cx="16" cy="11" r="1" fill="currentColor"/>
                  <circle cx="18" cy="13" r="1" fill="currentColor"/>
                </svg>
                <svg v-else-if="cat.name === '悬疑'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                  <path d="M11 8v3l2 2"/>
                </svg>
                <svg v-else-if="cat.name === '武侠'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14.5 17.5L3 6V3h3l11.5 11.5"/>
                  <path d="M13 19l6-6"/>
                  <path d="M16 16l4 4"/>
                  <path d="M19 21l2-2"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count">{{ cat.count }} 本</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== LATEST UPDATES ===== -->
      <section class="latest-section">
        <div class="section-container">
          <div class="section-header">
            <div class="section-title-wrap">
              <span class="section-label">最新更新</span>
              <h2 class="section-title">今日更新</h2>
            </div>
            <router-link to="/novels" class="see-all">更多更新</router-link>
          </div>

          <div class="latest-list">
            <article
              v-for="novel in recentNovels"
              :key="novel.id"
              class="latest-item"
              @click="goToDetail(novel.id)"
            >
              <div class="item-cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://neeko-copilot.bytedance.net/api/text_to_image?prompt=book%20cover%20art%20literary%20novel%20elegant&image_size=portrait_4_3'"
                />
              </div>
              <div class="item-info">
                <h3 class="item-title">{{ novel.title }}</h3>
                <p class="item-author">{{ novel.author }}</p>
                <p class="item-chapter">更新至第 {{ novel.chapter_count }} 章</p>
              </div>
              <div class="item-meta">
                <span class="item-category">{{ novel.category }}</span>
                <span class="item-time">{{ formatTime(novel.updated_at) }}</span>
              </div>
            </article>
          </div>
        </div>
      </section>

    </main>

    <!-- ===== FOOTER ===== -->
    <footer class="site-footer">
      <div class="footer-container">
        <div class="footer-content">
          <div class="footer-brand">
            <div class="footer-logo">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
              </svg>
              <span>墨香书阁</span>
            </div>
            <p class="footer-desc">为阅读而生，为故事而活</p>
            <div class="social-links">
              <a href="#" class="social-link" aria-label="微博">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="微信">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </a>
              <a href="#" class="social-link" aria-label="GitHub">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
                </svg>
              </a>
            </div>
          </div>

          <div class="footer-links">
            <div class="link-group">
              <h4>产品</h4>
              <a href="/novels">书库</a>
              <a href="/rankings">排行榜</a>
              <a href="/search">搜索</a>
            </div>
            <div class="link-group">
              <h4>支持</h4>
              <a href="#">帮助中心</a>
              <a href="#">联系我们</a>
              <a href="#">用户反馈</a>
            </div>
            <div class="link-group">
              <h4>法律</h4>
              <a href="#">用户协议</a>
              <a href="#">隐私政策</a>
              <a href="#">版权声明</a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 墨香书阁. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onMounted as onMountedVue, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { novelApi, type Novel } from '../api'

const router = useRouter()
const route = useRoute()

const searchKeyword = ref('')
const searchInput = ref<HTMLInputElement>()
const featuredNovels = ref<Novel[]>([])
const recentNovels = ref<Novel[]>([])
const isScrolled = ref(false)

const currentRoute = computed(() => route.path)
const isLoggedIn = computed(() => !!localStorage.getItem('user'))

const categories = ref<{ name: string; color: string; count: number }[]>([
  { name: '玄幻', color: '#8b5cf6', count: 0 },
  { name: '都市', color: '#ec4899', count: 0 },
  { name: '穿越', color: '#f59e0b', count: 0 },
  { name: '科幻', color: '#3b82f6', count: 0 },
  { name: '游戏', color: '#10b981', count: 0 },
  { name: '悬疑', color: '#6366f1', count: 0 },
  { name: '武侠', color: '#ef4444', count: 0 },
  { name: '历史', color: '#84cc16', count: 0 },
])

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const formatTime = (time?: string) => {
  if (!time) return '刚刚'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return '刚刚'
  if (hours < 24) return hours + '小时前'
  const days = Math.floor(hours / 24)
  if (days < 30) return days + '天前'
  return date.toLocaleDateString()
}

const loadFeaturedNovels = async () => {
  try {
    const res = await novelApi.recommend(8)
    featuredNovels.value = res
  } catch (error) {
    console.error('加载推荐小说失败:', error)
  }
}

const loadRecentNovels = async () => {
  try {
    const res = await novelApi.list({ page_size: 8, ordering: '-updated_at' })
    recentNovels.value = res.results || []
  } catch (error) {
    console.error('加载最新小说失败:', error)
  }
}

const loadCategoryStats = async () => {
  try {
    const res = await (novelApi as any).category_stats()
    categories.value = categories.value.map(cat => ({
      ...cat,
      count: res[cat.name] || 0
    }))
  } catch (error) {
    console.error('加载分类统计失败:', error)
  }
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ name: 'Search', query: { q: searchKeyword.value } })
  }
}

const focusSearch = () => {
  searchInput.value?.focus()
}

const goToDetail = (id: number) => {
  router.push({ name: 'NovelDetail', params: { id } })
}

const goToCategory = (category: string) => {
  router.push({ name: 'NovelList', query: { category } })
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMountedVue(() => {
  loadFeaturedNovels()
  loadRecentNovels()
  loadCategoryStats()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

:root {
  --primary: #CA8A04;
  --primary-dark: #A67C00;
  --bg-paper: #FDFBF7;
  --bg-card: #FFFFFF;
  --text-primary: #1A1A1A;
  --text-muted: #6B7280;
  --border-color: #E5E7EB;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.home-page {
  min-height: 100vh;
  background: var(--bg-paper);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
  color: var(--text-primary);
}

/* ===== HEADER ===== */
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.header-scrolled {
  background: rgba(253, 251, 247, 0.98);
  box-shadow: var(--shadow-sm);
}

.header-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 70px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
}

.logo-icon {
  width: 28px;
  height: 28px;
  color: var(--primary);
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.375rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.main-nav {
  display: flex;
  gap: 1.75rem;
}

.nav-link {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-decoration: none;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.2s ease;
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--primary);
  border-radius: 1px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 220px;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  height: 38px;
  padding: 0 12px 0 36px;
  background: #F3F4F6;
  border: 1px solid transparent;
  border-radius: 20px;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s ease;
}

.search-input:focus {
  background: var(--bg-card);
  border-color: var(--border-color);
  box-shadow: var(--shadow-sm);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.action-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.action-btn--text {
  color: var(--text-muted);
}

.action-btn--text:hover {
  color: var(--text-primary);
}

.action-btn--primary {
  background: var(--text-primary);
  color: #fff;
}

.action-btn--primary:hover {
  opacity: 0.9;
}

.user-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  transition: all 0.2s ease;
}

.user-menu:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.user-icon {
  width: 20px;
  height: 20px;
}

/* ===== MAIN CONTENT ===== */
.main-content {
  padding-top: 70px;
}

/* ===== HERO ===== */
.hero-section {
  position: relative;
  min-height: 56vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 50%, #1A1A1A 100%);
}

.hero-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(202, 138, 4, 0.15) 0%, transparent 50%);
}

.hero-inner {
  position: relative;
  z-index: 1;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: center;
}

.hero-content {
  text-align: left;
}

.hero-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: rgba(202, 138, 4, 0.15);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 20px;
  margin-bottom: 1rem;
  letter-spacing: 0.05em;
}

.hero-title {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  color: #fff;
  line-height: 1.1;
  margin: 0 0 1rem;
}

.hero-desc {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 1.5rem;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.875rem 2rem;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  border-radius: 30px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(202, 138, 4, 0.3);
}

.btn-secondary {
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-book-showcase {
  position: relative;
  height: 340px;
}

.book-item {
  position: absolute;
  width: 140px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  transition: all 0.3s ease;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 60%);
  display: flex;
  align-items: flex-end;
  padding: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.book-item:hover .book-overlay {
  opacity: 1;
}

.book-title {
  font-size: 0.75rem;
  color: #fff;
  font-family: 'Noto Serif SC', serif;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-1 {
  top: 60px;
  left: 5%;
  transform: rotate(-8deg);
}

.book-2 {
  top: 40px;
  left: 28%;
  width: 160px;
  height: 220px;
  z-index: 2;
}

.book-3 {
  top: 70px;
  left: 52%;
  transform: rotate(5deg);
}

.book-4 {
  top: 50px;
  right: 15%;
  width: 150px;
  height: 210px;
  transform: rotate(8deg);
}

.book-5 {
  top: 80px;
  right: 2%;
  width: 130px;
  height: 185px;
  transform: rotate(-3deg);
}

.book-item:hover {
  transform: translateY(-8px) rotate(0deg) !important;
  z-index: 10;
}

/* ===== QUICK STATS ===== */
.quick-stats {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  display: block;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
}

.stat-label {
  font-size: 0.825rem;
  color: var(--text-muted);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

/* ===== SECTION SHARED ===== */
.section-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1.2rem;
}

.section-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.section-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--primary);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.see-all {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s ease;
}

.see-all:hover {
  color: var(--primary);
}

/* ===== FEATURED SECTION ===== */
.featured-section {
  padding: 1.5rem 0;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.novel-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.novel-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-cover-wrap {
  position: relative;
  aspect-ratio: 3/4;
  overflow: hidden;
}

.card-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.novel-card:hover .card-cover {
  transform: scale(1.05);
}

.card-category {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 3px 10px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 0.675rem;
  font-weight: 500;
  border-radius: 12px;
}

.card-hover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.novel-card:hover .card-hover-overlay {
  opacity: 1;
}

.hover-text {
  padding: 0.5rem 1.25rem;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 20px;
}

.card-content {
  padding: 0.75rem;
}

.card-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.2rem;
  line-height: 1.3;
}

.card-author {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0 0 0.25rem;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}
.card-tag {
  font-size: 0.68rem;
  color: #9CA3AF;
  background: rgba(156,163,175,0.1);
  border: 1px solid rgba(156,163,175,0.2);
  padding: 1px 8px;
  border-radius: 10px;
  font-family: var(--font-sans-cn);
}

.card-desc {
  font-size: 0.8rem;
  color: #6B7280;
  line-height: 1.5;
  margin: 0 0 0.4rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.775rem;
  color: #9CA3AF;
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

/* ===== CATEGORIES SECTION ===== */
.categories-section {
  padding: 2.5rem 0;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}

.category-card {
  padding: 1.5rem 1rem;
  background: var(--bg-paper);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--category-color);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.category-card:hover::before {
  opacity: 1;
}

.category-card:hover {
  border-color: var(--category-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.cat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: color-mix(in srgb, var(--category-color) 10%, transparent);
  color: var(--category-color);
}

.cat-icon svg {
  width: 22px;
  height: 22px;
}

.cat-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.cat-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ===== LATEST SECTION ===== */
.latest-section {
  padding: 3rem 0;
}

.latest-list {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.latest-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s ease;
}

.latest-item:last-child {
  border-bottom: none;
}

.latest-item:hover {
  background: #FAFAFA;
}

.item-cover {
  width: 56px;
  height: 78px;
  border-radius: 6px;
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

.item-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-author {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0 0 0.2rem;
}

.item-chapter {
  font-size: 0.78rem;
  color: #9CA3AF;
  margin: 0;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.375rem;
}

.item-category {
  padding: 2px 9px;
  background: #F3F4F6;
  color: var(--text-muted);
  font-size: 0.675rem;
  border-radius: 12px;
}

.item-time {
  font-size: 0.75rem;
  color: #9CA3AF;
}

/* ===== FOOTER ===== */
.site-footer {
  background: #111111;
  color: #fff;
  padding: 2rem 0 1.5rem;
}

.footer-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 2rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  gap: 4rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #222;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.footer-logo svg {
  width: 24px;
  height: 24px;
  color: var(--primary);
}

.footer-desc {
  color: #6B7280;
  font-size: 0.875rem;
  margin: 0 0 1.25rem;
}

.social-links {
  display: flex;
  gap: 0.5rem;
}

.social-link {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1E1E1E;
  border: 1px solid #2A2A2A;
  border-radius: 50%;
  color: #6B7280;
  transition: all 0.2s ease;
}

.social-link:hover {
  color: #fff;
  border-color: #444;
}

.social-link svg {
  width: 16px;
  height: 16px;
}

.footer-links {
  display: flex;
  gap: 3rem;
}

.link-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.link-group h4 {
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 0.75rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.link-group a {
  color: #6B7280;
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s ease;
}

.link-group a:hover {
  color: #D1D5DB;
}

.footer-bottom {
  padding-top: 2rem;
  text-align: center;
}

.footer-bottom p {
  color: #374151;
  font-size: 0.8rem;
  margin: 0;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
  .hero-inner {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }

  .hero-content {
    text-align: center;
  }

  .hero-book-showcase {
    height: 320px;
  }

  .book-item {
    width: 110px;
    height: 160px;
  }

  .book-2 {
    width: 130px;
    height: 180px;
  }

  .book-4 {
    width: 120px;
    height: 170px;
  }

  .book-5 {
    width: 100px;
    height: 145px;
  }

  .stats-container {
    flex-wrap: wrap;
  }

  .stat-divider {
    display: none;
  }

  .stat-item {
    min-width: calc(50% - 1rem);
  }
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 1.25rem;
    gap: 1rem;
  }

  .main-nav {
    display: none;
  }

  .search-box {
    width: 150px;
  }

  .hero-inner {
    padding: 2rem 1.25rem;
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-book-showcase {
    height: 260px;
  }

  .book-item {
    width: 90px;
    height: 130px;
  }

  .book-2 {
    width: 105px;
    height: 150px;
  }

  .book-4 {
    width: 100px;
    height: 140px;
  }

  .book-5 {
    display: none;
  }

  .section-container {
    padding: 0 1.25rem;
  }

  .featured-section,
  .latest-section {
    padding: 1.5rem 0;
  }

  .categories-section {
    padding: 1.75rem 0;
  }

  .categories-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
  }

  .category-card {
    padding: 1rem 0.5rem;
  }

  .cat-icon {
    width: 32px;
    height: 32px;
  }

  .cat-icon svg {
    width: 18px;
    height: 18px;
  }

  .cat-name {
    font-size: 0.85rem;
  }

  .footer-content {
    flex-direction: column;
    gap: 2rem;
  }

  .footer-links {
    flex-wrap: wrap;
    gap: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-book-showcase {
    height: 200px;
  }

  .book-item {
    width: 70px;
    height: 100px;
  }

  .book-2 {
    width: 85px;
    height: 120px;
  }

  .book-3,
  .book-4 {
    display: none;
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-item {
    min-width: 100%;
  }
}
</style>