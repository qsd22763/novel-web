<template>
  <div class="novel-list-page">
    <header class="site-header">
      <div class="header-inner">
        <h1 class="logo" @click="goHome">墨香書閣</h1>
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
              <img v-if="userAvatar" :src="userAvatar" alt="头像" class="user-avatar-img" />
              <el-icon v-else :size="18"><User /></el-icon>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <div class="page-head">
      <div class="page-head-inner">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <router-link to="/" class="bc-item">首页</router-link>
          <span class="bc-sep">›</span>
          <span class="bc-item bc-current">书库</span>
          <template v-if="selectedCategory">
            <span class="bc-sep">›</span>
            <span class="bc-item bc-current">{{ selectedCategory }}</span>
          </template>
        </nav>
        <h2 class="page-title">
          <span class="title-deco">〔</span>
          {{ selectedCategory || '全部藏书' }}
          <span class="title-deco">〕</span>
        </h2>
        <p class="page-subtitle">共收录 <em>{{ totalNovels }}</em> 部作品，静心阅读，品味文字之美</p>
      </div>
    </div>

    <main class="main-content">
      <div class="content-layout">

        <aside class="sidebar">
          <div class="sidebar-section">
            <h3 class="sidebar-heading">
              <span class="heading-mark">◆</span>
              分类
            </h3>
            <ul class="category-list">
              <li
                :class="{ active: !selectedCategory }"
                @click="selectCategory('')"
              >
                <span class="cat-icon">📚</span>
                <span class="cat-name">全部</span>
                <span class="cat-count">{{ totalNovels }}</span>
              </li>
              <li
                v-for="cat in categories"
                :key="cat.name"
                :class="{ active: selectedCategory === cat.name }"
                @click="selectCategory(cat.name)"
              >
                <span class="cat-icon">{{ cat.icon }}</span>
                <span class="cat-name">{{ cat.name }}</span>
                <span class="cat-count">{{ cat.count }}</span>
              </li>
            </ul>
          </div>

          <div class="sidebar-section">
            <h3 class="sidebar-heading">
              <span class="heading-mark">◆</span>
              筛选
            </h3>
            <div class="filter-block">
              <p class="filter-label">连载状态</p>
              <div class="status-btns">
                <button
                  :class="{ active: filterStatus === '' }"
                  @click="filterStatus = ''; handleFilterChange()"
                >全部</button>
                <button
                  :class="{ active: filterStatus === '0' }"
                  @click="filterStatus = '0'; handleFilterChange()"
                >连载中</button>
                <button
                  :class="{ active: filterStatus === '1' }"
                  @click="filterStatus = '1'; handleFilterChange()"
                >已完结</button>
              </div>
            </div>
            <div class="filter-block">
              <p class="filter-label">字数范围</p>
              <el-select
                v-model="filterWordCount"
                size="small"
                placeholder="选择字数"
                class="word-select"
                @change="handleFilterChange"
              >
                <el-option label="全部" value="" />
                <el-option label="30万以下" value="0-300000" />
                <el-option label="30 - 50万" value="300000-500000" />
                <el-option label="50 - 100万" value="500000-1000000" />
                <el-option label="100 - 200万" value="1000000-2000000" />
                <el-option label="200万以上" value="2000000-" />
              </el-select>
            </div>
          </div>

          <div class="sidebar-section ranking-section">
            <h3 class="sidebar-heading">
              <span class="heading-mark">◆</span>
              人气榜单
            </h3>
            <ol class="ranking-list">
              <li
                v-for="(novel, index) in topNovels"
                :key="novel.id"
                @click="goToDetail(novel.id)"
              >
                <span class="rank-num" :class="{ gold: index === 0, silver: index === 1, bronze: index === 2 }">
                  {{ index + 1 }}
                </span>
                <div class="rank-info">
                  <span class="rank-title">{{ novel.title }}</span>
                  <span class="rank-views">{{ formatCount(novel.view_count) }} 阅读</span>
                </div>
              </li>
            </ol>
          </div>
        </aside>

        <section class="novels-section">
          <div class="novels-toolbar">
            <div class="toolbar-left">
              <span class="result-label">
                {{ selectedCategory ? selectedCategory : '全部作品' }}
              </span>
              <span class="result-count">· {{ totalNovels }} 部</span>
            </div>
            <div class="toolbar-right">
              <span class="sort-label">排序：</span>
              <el-select v-model="sortBy" size="small" class="sort-select" @change="handleSort">
                <el-option label="默认排序" value="default" />
                <el-option label="更新时间" value="updated" />
                <el-option label="人气最高" value="views" />
                <el-option label="字数最多" value="words" />
                <el-option label="收藏最多" value="recommend" />
              </el-select>
            </div>
          </div>

          <div class="novel-grid" v-if="!loading && novels.length > 0">
            <article
              v-for="novel in novels"
              :key="novel.id"
              class="novel-card"
              @click="goToDetail(novel.id)"
            >
              <div class="card-cover">
                <img
                  v-lazy="novel.cover"
                  :alt="novel.title"
                  @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x420/D4C5A9/6B5344?text=%E5%B0%81%E9%9D%A2'"
                />
                <div class="cover-overlay">
                  <span class="read-btn">开始阅读</span>
                </div>
                <span class="status-badge" :class="{ finished: novel.status === 1 }">
                  {{ novel.status === 1 ? '完结' : '连载' }}
                </span>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ novel.title }}</h3>
                <p class="card-author">
                  <el-icon><User /></el-icon>
                  {{ novel.author }}
                </p>
                <div class="card-tags">
                  <span class="tag-cat">{{ novel.category }}</span>
                  <span class="tag-words">{{ formatWordCount(novel.word_count) }}</span>
                </div>
                <p class="card-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="card-meta">
                  <span class="meta-view">
                    <el-icon><View /></el-icon>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="meta-time">{{ formatDate(novel.updated_at) }}</span>
                </div>
              </div>
            </article>
          </div>

          <div class="skeleton-grid" v-else-if="loading">
            <div class="skeleton-card" v-for="i in 12" :key="i">
              <div class="sk-cover"></div>
              <div class="sk-body">
                <div class="sk-line sk-title"></div>
                <div class="sk-line sk-author"></div>
                <div class="sk-line sk-desc"></div>
                <div class="sk-line sk-desc short"></div>
              </div>
            </div>
          </div>

          <div class="empty-state" v-else>
            <div class="empty-books">
              <div class="book-spine sp1"></div>
              <div class="book-spine sp2"></div>
              <div class="book-spine sp3"></div>
            </div>
            <p class="empty-text">此处空空如也，换个分类试试</p>
          </div>

          <div class="pagination-bar" v-if="totalPages > 1">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalNovels"
              layout="prev, pager, next"
              @current-change="handlePageChange"
            />
          </div>
        </section>

      </div>
    </main>

    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">墨香書閣</span>
          <p>為閱讀而生，為故事而活</p>
        </div>
        <div class="footer-divider"></div>
        <div class="footer-links">
          <a href="#">关于我们</a>
          <a href="#">联系方式</a>
          <a href="#">用户协议</a>
          <a href="#">隐私政策</a>
        </div>
        <p class="copyright">© 2026 墨香書閣 · All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, User, Grid, Trophy, View, Document, Filter } from '@element-plus/icons-vue'
import { novelApi, type Novel } from '../api'

const router = useRouter()
const route = useRoute()

const novels = ref<Novel[]>([])
const topNovels = ref<Novel[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalNovels = ref(0)
const selectedCategory = ref('')
const sortBy = ref('default')
const searchKeyword = ref('')
const filterStatus = ref('')
const filterWordCount = ref('')

const isLoggedIn = computed(() => !!localStorage.getItem('user'))
const userAvatar = ref('')

interface Category {
  name: string
  icon: string
  count: number
}

const categories = ref<Category[]>([
  { name: '玄幻', icon: '🐉', count: 0 },
  { name: '都市', icon: '🌆', count: 0 },
  { name: '穿越', icon: '⏳', count: 0 },
  { name: '科幻', icon: '🚀', count: 0 },
  { name: '游戏', icon: '🎮', count: 0 },
  { name: '悬疑', icon: '🔮', count: 0 },
  { name: '武侠', icon: '⚔️', count: 0 },
  { name: '历史', icon: '📜', count: 0 },
])

const totalPages = computed(() => Math.ceil(totalNovels.value / pageSize.value))

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今日'
  if (days === 1) return '昨日'
  if (days < 7) return days + '天前'
  if (days < 30) return Math.floor(days / 7) + '周前'
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const loadNovels = async () => {
  loading.value = true
  novels.value = []
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    if (filterStatus.value !== '') {
      params.status = filterStatus.value
    }
    if (filterWordCount.value) {
      const [min, max] = filterWordCount.value.split('-')
      if (min) params.word_count_min = min
      if (max) params.word_count_max = max
    }
    if (sortBy.value === 'views') {
      params.ordering = '-view_count'
    } else if (sortBy.value === 'words') {
      params.ordering = '-word_count'
    } else if (sortBy.value === 'updated') {
      params.ordering = '-updated_at'
    } else if (sortBy.value === 'recommend') {
      params.ordering = '-view_count'
    }

    const res = await novelApi.list(params)
    novels.value = res.results || []
    totalNovels.value = res.count || 0
  } catch (error) {
    console.error('加载小说列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadCategoryStats = async () => {
  try {
    const res: any = await novelApi.category_stats()
    categories.value = categories.value.map(cat => ({
      ...cat,
      count: res[cat.name] || 0
    }))
  } catch (error) {
    console.error('加载分类统计失败:', error)
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadNovels()
}

const loadTopNovels = async () => {
  try {
    const res = await novelApi.list({ page_size: 5, ordering: '-view_count' })
    topNovels.value = (res.results || []).slice(0, 5)
  } catch (error) {
    console.error('加载榜单失败:', error)
  }
}

const selectCategory = (cat: string) => {
  selectedCategory.value = cat
  currentPage.value = 1
  loadNovels()
}

const handleSort = () => {
  currentPage.value = 1
  loadNovels()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadNovels()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
  const category = route.query.category as string
  if (category) {
    selectedCategory.value = category
  }
  loadNovels()
  loadTopNovels()
  loadCategoryStats()
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    userAvatar.value = user.avatar || ''
  } catch {}
})

watch(() => route.query.category, (newCat) => {
  selectedCategory.value = (newCat as string) || ''
  loadNovels()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+TC:wght@400;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

:root {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-light: #FEF3C7;
  --border: #E0E0E0;
  --card-bg: #FFFFFF;
  --sidebar-bg: #FAF8F4;
}

* {
  box-sizing: border-box;
}

.novel-list-page {
  min-height: 100vh;
  background: var(--paper-bg);
  font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft YaHei', sans-serif;
  color: var(--ink);
}

/* ========== HEADER ========== */
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.97);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.header-inner {
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.logo {
  font-family: 'Noto Serif TC', 'STSong', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  cursor: pointer;
  white-space: nowrap;
  letter-spacing: 0.05em;
}

.main-nav {
  display: flex;
  gap: 2rem;
}

.main-nav a {
  font-size: 0.88rem;
  color: var(--muted);
  text-decoration: none;
  letter-spacing: 0.03em;
  padding-bottom: 2px;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.main-nav a:hover {
  color: var(--ink);
}

.main-nav a.router-link-active {
  color: var(--ink);
  border-bottom-color: var(--accent);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.search-input {
  width: 210px;
}

.search-input :deep(.el-input__wrapper) {
  background: #F5F2EC;
  box-shadow: none !important;
  border: 1px solid transparent;
  border-radius: 6px;
  transition: all 0.25s;
}

.search-input :deep(.el-input__wrapper:hover),
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent);
  background: var(--card-bg);
}

.auth-link {
  font-size: 0.88rem;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
}

.auth-link:hover {
  color: var(--accent);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: #F5F2EC;
  border-radius: 50%;
  color: var(--muted);
  border: 1px solid var(--border);
  transition: all 0.2s;
}

.user-avatar:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

/* ========== PAGE HEAD ========== */
.page-head {
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  padding: 2rem 0 1.75rem;
}

.page-head-inner {
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 2rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.75rem;
}

.bc-item {
  font-size: 0.8rem;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
}

a.bc-item:hover {
  color: var(--accent);
}

.bc-current {
  color: var(--ink);
}

.bc-sep {
  font-size: 0.75rem;
  color: var(--border);
}

.page-title {
  font-family: 'Noto Serif TC', 'STSong', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.5rem;
  letter-spacing: 0.06em;
}

.title-deco {
  color: var(--accent);
  font-size: 1.5rem;
  margin: 0 0.25rem;
}

.page-subtitle {
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
}

.page-subtitle em {
  font-style: normal;
  color: var(--accent);
  font-weight: 600;
}

/* ========== MAIN LAYOUT ========== */
.main-content {
  max-width: 1360px;
  margin: 0 auto;
  padding: 2rem 2rem 3rem;
}

.content-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

/* ========== SIDEBAR ========== */
.sidebar {
  width: 248px;
  flex-shrink: 0;
  position: sticky;
  top: 76px;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.sidebar-section {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.25rem;
}

.sidebar-heading {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  letter-spacing: 0.08em;
}

.heading-mark {
  color: var(--accent);
  font-size: 0.6rem;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.category-list li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.7rem;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.category-list li:hover {
  background: var(--accent-light);
  border-color: #FDE68A;
}

.category-list li.active {
  background: var(--accent-light);
  border-color: var(--accent);
}

.category-list li.active .cat-name {
  color: #92400E;
  font-weight: 600;
}

.category-list li.active .cat-count {
  background: var(--accent);
  color: #fff;
}

.cat-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.cat-name {
  flex: 1;
  font-size: 0.875rem;
  color: var(--ink);
}

.cat-count {
  font-size: 0.7rem;
  color: var(--muted);
  background: #F3F0EB;
  padding: 2px 7px;
  border-radius: 10px;
  min-width: 28px;
  text-align: center;
}

.filter-block {
  margin-bottom: 1rem;
}

.filter-block:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
  letter-spacing: 0.04em;
}

.status-btns {
  display: flex;
  gap: 6px;
}

.status-btns button {
  flex: 1;
  padding: 5px 0;
  font-size: 0.78rem;
  font-family: inherit;
  border: 1px solid var(--border);
  background: var(--card-bg);
  color: var(--muted);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.status-btns button:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.status-btns button.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  font-weight: 600;
}

.word-select {
  width: 100%;
}

.word-select :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px;
  background: var(--card-bg);
  font-size: 0.8rem;
}

.word-select :deep(.el-select__wrapper:hover) {
  border-color: var(--accent) !important;
}

.ranking-section {}

.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.ranking-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  cursor: pointer;
  border-bottom: 1px dashed #F0ECE4;
  transition: opacity 0.2s;
}

.ranking-list li:last-child {
  border-bottom: none;
}

.ranking-list li:hover {
  opacity: 0.7;
}

.rank-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  font-size: 0.78rem;
  font-weight: 700;
  flex-shrink: 0;
  border-radius: 3px;
  background: #F3F0EB;
  color: var(--muted);
}

.rank-num.gold {
  background: var(--accent);
  color: #fff;
}

.rank-num.silver {
  background: #9CA3AF;
  color: #fff;
}

.rank-num.bronze {
  background: #B45309;
  color: #fff;
}

.rank-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.rank-title {
  font-size: 0.82rem;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-views {
  font-size: 0.7rem;
  color: var(--muted);
}

/* ========== NOVELS SECTION ========== */
.novels-section {
  flex: 1;
  min-width: 0;
}

.novels-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.result-label {
  font-family: 'Noto Serif TC', serif;
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
}

.result-count {
  font-size: 0.8rem;
  color: var(--muted);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  font-size: 0.82rem;
  color: var(--muted);
}

.sort-select {
  width: 110px;
}

.sort-select :deep(.el-select__wrapper) {
  box-shadow: none !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px;
  font-size: 0.82rem;
}

.sort-select :deep(.el-select__wrapper:hover) {
  border-color: var(--accent) !important;
}

/* ========== NOVEL GRID ========== */
.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: 1.5rem;
}

.novel-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.28s ease, border-color 0.28s ease, transform 0.28s ease;
}

.novel-card:hover {
  border-color: var(--accent);
  box-shadow: 0 8px 32px rgba(202, 138, 4, 0.12), 0 2px 8px rgba(0,0,0,0.08);
  transform: translateY(-4px);
}

.card-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  overflow: hidden;
  background: #E8E2D8;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.32s ease;
}

.novel-card:hover .card-cover img {
  transform: scale(1.06);
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(26, 26, 26, 0.52);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.28s;
}

.novel-card:hover .cover-overlay {
  opacity: 1;
}

.read-btn {
  padding: 7px 18px;
  background: var(--card-bg);
  color: var(--ink);
  font-size: 0.82rem;
  font-weight: 600;
  border-radius: 2px;
  letter-spacing: 0.06em;
  transform: translateY(8px);
  transition: transform 0.28s;
}

.novel-card:hover .read-btn {
  transform: translateY(0);
}

.status-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 3px 8px;
  font-size: 0.65rem;
  font-weight: 600;
  border-radius: 2px;
  letter-spacing: 0.04em;
  background: rgba(59, 130, 246, 0.85);
  color: #fff;
  backdrop-filter: blur(4px);
}

.status-badge.finished {
  background: rgba(202, 138, 4, 0.9);
}

.card-body {
  padding: 0.875rem;
}

.card-title {
  font-family: 'Noto Serif TC', serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.35rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.03em;
}

.card-author {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
}

.card-tags {
  display: flex;
  gap: 5px;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.tag-cat,
.tag-words {
  font-size: 0.65rem;
  padding: 2px 7px;
  border-radius: 2px;
  letter-spacing: 0.03em;
}

.tag-cat {
  background: var(--accent-light);
  color: #92400E;
  border: 1px solid #FDE68A;
}

.tag-words {
  background: #F3F0EB;
  color: var(--muted);
  border: 1px solid var(--border);
}

.card-desc {
  font-size: 0.75rem;
  color: #9CA3AF;
  line-height: 1.55;
  margin: 0 0 0.6rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
  border-top: 1px solid #F3F0EB;
}

.meta-view {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.7rem;
  color: var(--muted);
}

.meta-time {
  font-size: 0.68rem;
  color: #D1C9BC;
}

/* ========== SKELETON ========== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: 1.5rem;
}

.skeleton-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.sk-cover {
  width: 100%;
  aspect-ratio: 3 / 4;
  background: linear-gradient(90deg, #F3F0EB 25%, #EDE8E0 50%, #F3F0EB 75%);
  background-size: 300% 100%;
  animation: sk-shimmer 1.6s infinite;
}

.sk-body {
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sk-line {
  height: 12px;
  border-radius: 3px;
  background: linear-gradient(90deg, #F3F0EB 25%, #EDE8E0 50%, #F3F0EB 75%);
  background-size: 300% 100%;
  animation: sk-shimmer 1.6s infinite;
}

.sk-title {
  height: 15px;
  width: 75%;
}

.sk-author {
  width: 50%;
}

.sk-desc {
  width: 100%;
}

.sk-desc.short {
  width: 65%;
}

@keyframes sk-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}

/* ========== EMPTY STATE ========== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 360px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.empty-books {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  margin-bottom: 1.5rem;
}

.book-spine {
  border-radius: 3px 0 0 3px;
}

.sp1 {
  width: 28px;
  height: 80px;
  background: linear-gradient(180deg, #D4C5A9 0%, #B8A88A 100%);
}

.sp2 {
  width: 32px;
  height: 100px;
  background: linear-gradient(180deg, #8B7355 0%, #6B5344 100%);
}

.sp3 {
  width: 24px;
  height: 64px;
  background: linear-gradient(180deg, #C9AE80 0%, #A8906A 100%);
}

.empty-text {
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
  letter-spacing: 0.04em;
}

/* ========== PAGINATION ========== */
.pagination-bar {
  display: flex;
  justify-content: center;
  margin-top: 2.5rem;
}

.pagination-bar :deep(.el-pagination) {
  gap: 4px;
}

.pagination-bar :deep(.el-pager li) {
  border-radius: 3px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  color: var(--ink);
  font-size: 0.85rem;
  min-width: 34px;
  height: 34px;
  line-height: 32px;
  transition: all 0.2s;
}

.pagination-bar :deep(.el-pager li:hover) {
  border-color: var(--accent);
  color: var(--accent);
}

.pagination-bar :deep(.el-pager li.is-active) {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  font-weight: 700;
}

.pagination-bar :deep(.btn-prev),
.pagination-bar :deep(.btn-next) {
  border-radius: 3px;
  border: 1px solid var(--border);
  background: var(--card-bg);
  height: 34px;
  width: 34px;
  transition: all 0.2s;
}

.pagination-bar :deep(.btn-prev:hover),
.pagination-bar :deep(.btn-next:hover) {
  border-color: var(--accent);
  color: var(--accent);
}

/* ========== FOOTER ========== */
.site-footer {
  background: #1C1A17;
  padding: 3rem 2rem 2rem;
  margin-top: 4rem;
}

.footer-inner {
  max-width: 1360px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand {
  margin-bottom: 1.5rem;
}

.footer-logo {
  font-family: 'Noto Serif TC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #F5F0E8;
  letter-spacing: 0.08em;
}

.footer-brand p {
  font-size: 0.82rem;
  color: #6B6560;
  margin: 0.4rem 0 0;
  letter-spacing: 0.06em;
}

.footer-divider {
  width: 60px;
  height: 1px;
  background: #3A3530;
  margin: 0 auto 1.5rem;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.footer-links a {
  font-size: 0.82rem;
  color: #6B6560;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--accent);
}

.copyright {
  font-size: 0.75rem;
  color: #4A4540;
  margin: 0;
  letter-spacing: 0.04em;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1100px) {
  .content-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    position: static;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .ranking-section {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .header-inner {
    padding: 0 1rem;
    gap: 1rem;
  }

  .main-nav {
    display: none;
  }

  .page-head-inner,
  .main-content {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .page-title {
    font-size: 1.35rem;
  }

  .sidebar {
    grid-template-columns: 1fr;
  }

  .ranking-section {
    grid-column: span 1;
  }

  .novel-grid,
  .skeleton-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}

@media (max-width: 420px) {
  .novel-grid,
  .skeleton-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
}
</style>
