<template>
  <div class="home-page">
    <header class="site-header">
      <div class="header-inner">
        <h1 class="logo">墨香书阁</h1>
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
            <router-link to="/login" class="auth-btn">注册</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="user-avatar">
              <el-icon :size="20"><User /></el-icon>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <section class="hero-section">
        <div class="hero-content">
          <h2 class="hero-title">发现你的<br/>下一个故事</h2>
          <p class="hero-subtitle">海量免费小说，沉浸式阅读体验</p>
          <div class="hero-actions">
            <router-link to="/novels" class="btn-primary">开始探索</router-link>
            <router-link to="/login" class="btn-secondary">免费加入</router-link>
          </div>
        </div>
        <div class="hero-decoration">
          <div class="book-stack">
            <div class="book-decoration">
              <div class="book-spine spine-1"></div>
              <div class="book-spine spine-2"></div>
              <div class="book-spine spine-3"></div>
            </div>
          </div>
        </div>
        <div class="hero-bg-text">READ</div>
      </section>

      <section class="featured-section">
        <div class="section-container">
          <div class="section-header">
            <div class="header-line"></div>
            <h3 class="section-title">编辑推荐</h3>
            <span class="section-subtitle">EDITOR'S PICKS</span>
          </div>
          <div class="featured-grid">
            <article
              v-for="(novel, index) in featuredNovels"
              :key="novel.id"
              class="featured-card"
              :class="`card-${index + 1}`"
              @click="goToDetail(novel.id)"
            >
              <div class="card-image">
                <img v-lazy="novel.cover" :alt="novel.title" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
                <div class="card-overlay">
                  <span class="overlay-cta">阅读详情</span>
                </div>
              </div>
              <div class="card-badge">{{ novel.category }}</div>
              <div class="card-body">
                <h4 class="card-title">{{ novel.title }}</h4>
                <p class="card-author">{{ novel.author }}</p>
                <p class="card-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="card-meta">
                  <span class="meta-item">
                    <el-icon><View /></el-icon>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Document /></el-icon>
                    {{ formatWordCount(novel.word_count) }}
                  </span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="categories-section">
        <div class="section-container">
          <div class="section-header">
            <div class="header-line"></div>
            <h3 class="section-title">分类浏览</h3>
            <span class="section-subtitle">BROWSE BY GENRE</span>
          </div>
          <div class="categories-grid">
            <div
              v-for="cat in categories"
              :key="cat.name"
              class="category-card"
              :style="{ '--accent': cat.color }"
              @click="goToCategory(cat.name)"
            >
              <span class="category-icon">{{ cat.icon }}</span>
              <span class="category-name">{{ cat.name }}</span>
              <span class="category-count">{{ cat.count }}本</span>
              <div class="category-bg">{{ cat.icon }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="recent-section">
        <div class="section-container">
          <div class="section-header">
            <div class="header-line"></div>
            <h3 class="section-title">最新更新</h3>
            <span class="section-subtitle">LATEST UPDATES</span>
            <router-link to="/novels" class="see-more">查看全部 →</router-link>
          </div>
          <div class="recent-grid">
            <article
              v-for="novel in recentNovels"
              :key="novel.id"
              class="recent-item"
              @click="goToDetail(novel.id)"
            >
              <div class="item-image">
                <img v-lazy="novel.cover" :alt="novel.title" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
              </div>
              <div class="item-info">
                <h4>{{ novel.title }}</h4>
                <p class="author">{{ novel.author }}</p>
                <p class="chapter">更新至：第{{ novel.chapter_count }}章</p>
              </div>
              <div class="item-meta">
                <span class="time">{{ formatTime(novel.updated_at) }}</span>
                <span class="category-tag">{{ novel.category }}</span>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="stats-section">
        <div class="section-container">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-number">10K+</span>
              <span class="stat-label">精选小说</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">1M+</span>
              <span class="stat-label">活跃读者</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">100%</span>
              <span class="stat-label">免费阅读</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">Daily</span>
              <span class="stat-label">持续更新</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="footer-content">
        <div class="footer-main">
          <div class="footer-brand">
            <h3>墨香书阁</h3>
            <p>为阅读而生，为故事而活</p>
            <div class="social-links">
              <a href="#" class="social-link">微</a>
              <a href="#" class="social-link">博</a>
              <a href="#" class="social-link">信</a>
            </div>
          </div>
          <div class="footer-links">
            <div class="link-group">
              <h4>产品</h4>
              <a href="#">书库</a>
              <a href="#">排行榜</a>
              <a href="#">分类</a>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, User, View, Document } from '@element-plus/icons-vue'
import { novelApi, type Novel } from '../api'

const router = useRouter()

const searchKeyword = ref('')
const featuredNovels = ref<Novel[]>([])
const recentNovels = ref<Novel[]>([])

const isLoggedIn = computed(() => !!localStorage.getItem('user'))

const categories = [
  { name: '玄幻', icon: '🐉', color: '#8b5cf6', count: 1234 },
  { name: '都市', icon: '🌆', color: '#ec4899', count: 2156 },
  { name: '穿越', icon: '⏳', color: '#f59e0b', count: 987 },
  { name: '科幻', icon: '🚀', color: '#3b82f6', count: 654 },
  { name: '游戏', icon: '🎮', color: '#10b981', count: 543 },
  { name: '悬疑', icon: '🔮', color: '#6366f1', count: 432 },
  { name: '武侠', icon: '⚔️', color: '#ef4444', count: 321 },
  { name: '历史', icon: '📜', color: '#84cc16', count: 287 },
]

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const formatTime = (time: string) => {
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
    const res = await novelApi.recommend(6)
    featuredNovels.value = res
  } catch (error) {
    console.error('加载推荐小说失败:', error)
  }
}

const loadRecentNovels = async () => {
  try {
    const res = await novelApi.list({ page_size: 6, ordering: '-updated_at' })
    recentNovels.value = res.results || []
  } catch (error) {
    console.error('加载最新小说失败:', error)
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

const goToCategory = (category: string) => {
  router.push({ name: 'NovelList', query: { category } })
}

onMounted(() => {
  loadFeaturedNovels()
  loadRecentNovels()
})
</script>

<style scoped>
.home-page {
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
  width: 220px;
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

.auth-btn {
  padding: 0.5rem 1.25rem;
  background: #1a1a1a;
  color: #fff;
  text-decoration: none;
  font-size: 0.85rem;
  border-radius: 24px;
  transition: all 0.2s;
}

.auth-btn:hover {
  background: #333;
  transform: translateY(-1px);
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

.hero-section {
  position: relative;
  background: linear-gradient(160deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
  padding: 6rem 2rem;
  overflow: hidden;
}

.hero-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.hero-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 4rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 1rem;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  padding: 0.875rem 2rem;
  background: #fff;
  color: #1a1a1a;
  text-decoration: none;
  font-weight: 500;
  border-radius: 30px;
  transition: all 0.3s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.btn-secondary {
  padding: 0.875rem 2rem;
  background: transparent;
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 30px;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.hero-decoration {
  position: absolute;
  top: 50%;
  right: 10%;
  transform: translateY(-50%);
  z-index: 1;
}

.book-stack {
  position: relative;
  width: 300px;
  height: 400px;
}

.book-decoration {
  position: relative;
  width: 100%;
  height: 100%;
}

.book-spine {
  position: absolute;
  border-radius: 4px 12px 12px 4px;
  transform-origin: left center;
}

.spine-1 {
  width: 60px;
  height: 320px;
  background: linear-gradient(90deg, #e8d5b7 0%, #d4c4a8 100%);
  left: 60px;
  top: 40px;
  transform: rotate(-8deg);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.3);
}

.spine-2 {
  width: 70px;
  height: 340px;
  background: linear-gradient(90deg, #8b7355 0%, #6b5344 100%);
  left: 110px;
  top: 30px;
  transform: rotate(-2deg);
  box-shadow: 4px 4px 16px rgba(0, 0, 0, 0.4);
}

.spine-3 {
  width: 55px;
  height: 300px;
  background: linear-gradient(90deg, #c9a959 0%, #a08040 100%);
  left: 170px;
  top: 50px;
  transform: rotate(6deg);
  box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.3);
}

.hero-bg-text {
  position: absolute;
  bottom: -60px;
  right: -20px;
  font-family: 'Noto Serif SC', serif;
  font-size: 12rem;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.03);
  z-index: 0;
  letter-spacing: -10px;
}

.section-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  position: relative;
  margin-bottom: 2rem;
}

.header-line {
  position: absolute;
  left: 0;
  top: 50%;
  width: 60px;
  height: 2px;
  background: #1a1a1a;
}

.section-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 0.25rem;
  padding-left: 80px;
}

.section-subtitle {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: #aaa;
  letter-spacing: 3px;
  padding-left: 80px;
}

.see-more {
  position: absolute;
  right: 0;
  bottom: 0.5rem;
  color: #666;
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s;
}

.see-more:hover {
  color: #1a1a1a;
}

.featured-section {
  padding: 5rem 0;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 1.5rem;
}

.featured-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s ease;
  background: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.featured-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.featured-card.card-1 {
  grid-row: span 2;
}

.featured-card.card-1 .card-image {
  height: 100%;
}

.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.featured-card.card-1 .card-image {
  height: 100%;
  min-height: 450px;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.featured-card:hover .card-image img {
  transform: scale(1.08);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, transparent 60%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 1.5rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.featured-card:hover .card-overlay {
  opacity: 1;
}

.overlay-cta {
  padding: 0.5rem 1.25rem;
  background: #fff;
  color: #1a1a1a;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 20px;
  transform: translateY(10px);
  transition: transform 0.3s;
}

.featured-card:hover .overlay-cta {
  transform: translateY(0);
}

.card-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 14px;
  background: rgba(26, 26, 26, 0.85);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.card-body {
  padding: 1.25rem;
}

.card-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.featured-card.card-1 .card-title {
  font-size: 1.25rem;
}

.card-author {
  font-size: 0.85rem;
  color: #888;
  margin: 0 0 0.75rem;
}

.card-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.6;
  margin: 0 0 1rem;
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
  font-size: 0.8rem;
  color: #aaa;
}

.categories-section {
  padding: 4rem 0;
  background: #fff;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.category-card {
  position: relative;
  padding: 2rem 1.5rem;
  background: var(--accent);
  border-radius: 16px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.category-icon {
  position: relative;
  z-index: 1;
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
}

.category-name {
  position: relative;
  z-index: 1;
  display: block;
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.25rem;
}

.category-count {
  position: relative;
  z-index: 1;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.category-bg {
  position: absolute;
  right: -20px;
  bottom: -20px;
  font-size: 6rem;
  opacity: 0.15;
  transform: rotate(-15deg);
}

.recent-section {
  padding: 5rem 0;
}

.recent-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1rem;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.recent-item:hover {
  border-color: #1a1a1a;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.item-image {
  width: 70px;
  height: 95px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-image img {
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

.item-info .chapter {
  font-size: 0.8rem;
  color: #666;
  margin: 0;
}

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.time {
  font-size: 0.8rem;
  color: #aaa;
}

.category-tag {
  padding: 4px 10px;
  background: #f5f3f0;
  color: #666;
  font-size: 0.75rem;
  border-radius: 12px;
}

.stats-section {
  padding: 4rem 0;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  text-align: center;
}

.stat-item {
  padding: 2rem;
}

.stat-number {
  display: block;
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.site-footer {
  background: #111;
  color: #fff;
  padding: 4rem 2rem 2rem;
}

.footer-main {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 4rem;
  padding-bottom: 3rem;
  border-bottom: 1px solid #222;
}

.footer-brand h3 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.5rem;
  margin: 0 0 0.5rem;
}

.footer-brand p {
  color: #666;
  margin: 0 0 1.5rem;
}

.social-links {
  display: flex;
  gap: 0.75rem;
}

.social-link {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  color: #888;
  border-radius: 50%;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.social-link:hover {
  background: #fff;
  color: #1a1a1a;
}

.footer-links {
  display: flex;
  gap: 4rem;
}

.link-group h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #fff;
}

.link-group a {
  display: block;
  color: #666;
  text-decoration: none;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  transition: color 0.2s;
}

.link-group a:hover {
  color: #fff;
}

.footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 2rem;
  text-align: center;
}

.footer-bottom p {
  color: #444;
  font-size: 0.85rem;
  margin: 0;
}

@media (max-width: 1024px) {
  .hero-title {
    font-size: 3rem;
  }

  .hero-decoration {
    display: none;
  }

  .featured-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .featured-card.card-1 {
    grid-row: span 1;
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
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

  .hero-section {
    padding: 4rem 1.5rem;
  }

  .hero-title {
    font-size: 2.25rem;
  }

  .hero-bg-text {
    display: none;
  }

  .featured-grid {
    grid-template-columns: 1fr;
  }

  .featured-card.card-1 .card-image {
    min-height: 250px;
  }

  .categories-grid {
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .category-card {
    padding: 1.5rem 1rem;
  }

  .category-icon {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .stat-number {
    font-size: 1.75rem;
  }

  .footer-main {
    flex-direction: column;
    gap: 2rem;
  }

  .footer-links {
    flex-wrap: wrap;
    gap: 2rem;
  }
}
</style>
