<template>
  <div class="novel-list-page">
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

    <div class="page-banner">
      <div class="banner-content">
        <h2>探索无限故事世界</h2>
        <p>发现你最喜欢的小说，开启阅读之旅</p>
      </div>
      <div class="banner-decoration">
        <div class="deco-circle circle-1"></div>
        <div class="deco-circle circle-2"></div>
        <div class="deco-circle circle-3"></div>
      </div>
    </div>

    <main class="main-content">
      <div class="content-layout">
        <aside class="sidebar">
          <div class="sidebar-section">
            <h3 class="section-title">
              <el-icon><Grid /></el-icon>
              分类
            </h3>
            <ul class="category-list">
              <li
                :class="{ active: !selectedCategory }"
                @click="selectCategory('')"
              >
                <span class="category-icon">📚</span>
                <span class="category-name">全部</span>
                <span class="category-count">{{ totalNovels }}</span>
              </li>
              <li
                v-for="cat in categories"
                :key="cat"
                :class="{ active: selectedCategory === cat }"
                @click="selectCategory(cat)"
              >
                <span class="category-icon">{{ getCategoryIcon(cat) }}</span>
                <span class="category-name">{{ cat }}</span>
                <span class="category-count">{{ getCategoryCount(cat) }}</span>
              </li>
            </ul>
          </div>

          <div class="sidebar-section ranking">
            <h3 class="section-title">
              <el-icon><Trophy /></el-icon>
              人气榜单
            </h3>
            <ol class="ranking-list">
              <li v-for="(novel, index) in topNovels" :key="novel.id" @click="goToDetail(novel.id)">
                <span class="rank-num" :class="{ top: index < 3 }">{{ index + 1 }}</span>
                <div class="rank-info">
                  <span class="rank-title">{{ novel.title }}</span>
                  <span class="rank-views">{{ formatCount(novel.view_count) }}阅读</span>
                </div>
              </li>
            </ol>
          </div>
        </aside>

        <section class="novels-section">
          <div class="section-header">
            <div class="results-info">
              <h2 v-if="selectedCategory">{{ selectedCategory }}</h2>
              <h2 v-else>全部作品</h2>
              <span class="novel-count">共 {{ totalNovels }} 部小说</span>
            </div>
            <div class="sort-options">
              <span class="sort-label">排序：</span>
              <el-select v-model="sortBy" size="small" @change="handleSort">
                <el-option label="默认排序" value="default" />
                <el-option label="更新时间" value="updated" />
                <el-option label="人气最高" value="views" />
                <el-option label="字数最多" value="words" />
              </el-select>
            </div>
          </div>

          <div class="novel-grid" v-if="novels.length > 0">
            <article
              v-for="novel in novels"
              :key="novel.id"
              class="novel-card"
              @click="goToDetail(novel.id)"
            >
              <div class="card-image">
                <img v-lazy="novel.cover" :alt="novel.title" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
                <div class="card-overlay">
                  <span class="read-btn">开始阅读</span>
                </div>
                <span class="category-tag">{{ novel.category }}</span>
              </div>
              <div class="card-content">
                <h3 class="novel-title">{{ novel.title }}</h3>
                <p class="novel-author">
                  <el-icon><User /></el-icon>
                  {{ novel.author }}
                </p>
                <p class="novel-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="novel-meta">
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

          <div class="loading-state" v-else-if="loading">
            <div class="skeleton-grid">
              <div class="skeleton-card" v-for="i in 8" :key="i">
                <div class="skeleton-image"></div>
                <div class="skeleton-content">
                  <div class="skeleton-title"></div>
                  <div class="skeleton-author"></div>
                  <div class="skeleton-desc"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="empty-state" v-else>
            <div class="empty-illustration">
              <div class="book-stack">
                <div class="book b1"></div>
                <div class="book b2"></div>
              </div>
            </div>
            <p>暂无相关小说</p>
          </div>

          <div class="pagination-wrapper" v-if="totalPages > 1">
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
      <div class="footer-content">
        <div class="footer-brand">
          <h3>墨香书阁</h3>
          <p>为阅读而生，为故事而活</p>
        </div>
        <div class="footer-links">
          <a href="#">关于我们</a>
          <a href="#">联系方式</a>
          <a href="#">用户协议</a>
          <a href="#">隐私政策</a>
        </div>
        <p class="copyright">© 2026 墨香书阁. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Search, User, Grid, Trophy, View, Document } from '@element-plus/icons-vue'
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

const isLoggedIn = computed(() => !!localStorage.getItem('user'))

const categories = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']

const totalPages = computed(() => Math.ceil(totalNovels.value / pageSize.value))

const getCategoryIcon = (cat: string) => {
  const icons: Record<string, string> = {
    '玄幻': '🐉', '都市': '🌆', '穿越': '⏳', '科幻': '🚀',
    '游戏': '🎮', '悬疑': '🔮', '武侠': '⚔️', '历史': '📜'
  }
  return icons[cat] || '📖'
}

const getCategoryCount = (cat: string) => {
  return Math.floor(Math.random() * 500) + 100
}

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatWordCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万字'
  return num + '字'
}

const loadNovels = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    if (sortBy.value === 'views') {
      params.ordering = '-view_count'
    } else if (sortBy.value === 'words') {
      params.ordering = '-word_count'
    } else if (sortBy.value === 'updated') {
      params.ordering = '-updated_at'
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

const loadTopNovels = async () => {
  try {
    const res = await novelApi.recommend(5)
    topNovels.value = res.slice(0, 5)
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
})

watch(() => route.query.category, (newCat) => {
  selectedCategory.value = (newCat as string) || ''
  loadNovels()
})
</script>

<style scoped>
.novel-list-page {
  min-height: 100vh;
  background: #faf8f5;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 248, 245, 0.95);
  backdrop-filter: blur(10px);
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

.page-banner {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
}

.banner-content {
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.banner-content h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 2.5rem;
  color: #fff;
  margin: 0 0 0.5rem;
}

.banner-content p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.banner-decoration {
  position: absolute;
  top: 0;
  right: 10%;
  bottom: 0;
  width: 400px;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.circle-1 {
  width: 300px;
  height: 300px;
  background: #fff;
  top: -100px;
  right: 0;
}

.circle-2 {
  width: 200px;
  height: 200px;
  background: #fff;
  top: 50px;
  right: 150px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  background: #fff;
  bottom: -50px;
  right: 50px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.content-layout {
  display: flex;
  gap: 2rem;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-section {
  background: #fff;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1a1a1a;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-list li:hover {
  background: #f9f9f9;
}

.category-list li.active {
  background: #1a1a1a;
  color: #fff;
}

.category-list li.active .category-count {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.category-icon {
  font-size: 1.1rem;
}

.category-name {
  flex: 1;
  font-size: 0.9rem;
}

.category-count {
  font-size: 0.75rem;
  color: #888;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
}

.ranking {
  flex: 1;
}

.ranking-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ranking-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.ranking-list li:hover {
  opacity: 0.7;
}

.rank-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #888;
  background: #f0f0f0;
  border-radius: 4px;
}

.rank-num.top {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: #fff;
}

.rank-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.rank-title {
  font-size: 0.85rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-views {
  font-size: 0.75rem;
  color: #aaa;
}

.novels-section {
  flex: 1;
  min-width: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-info h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.5rem;
  margin: 0 0 0.25rem;
  color: #1a1a1a;
}

.novel-count {
  font-size: 0.85rem;
  color: #888;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  font-size: 0.85rem;
  color: #888;
}

.sort-options :deep(.el-select) {
  width: 120px;
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.novel-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.novel-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.1);
  border-color: #1a1a1a;
}

.card-image {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.novel-card:hover .card-image img {
  transform: scale(1.08);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.novel-card:hover .card-overlay {
  opacity: 1;
}

.read-btn {
  padding: 0.6rem 1.5rem;
  background: #fff;
  color: #1a1a1a;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 24px;
  transform: translateY(10px);
  transition: transform 0.3s;
}

.novel-card:hover .read-btn {
  transform: translateY(0);
}

.category-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 0.75rem;
  border-radius: 4px;
}

.card-content {
  padding: 1.25rem;
}

.novel-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.novel-author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #888;
  margin: 0 0 0.75rem;
}

.novel-desc {
  font-size: 0.8rem;
  color: #666;
  line-height: 1.5;
  margin: 0 0 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.novel-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: #aaa;
}

.loading-state {
  min-height: 400px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.skeleton-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.skeleton-image {
  height: 260px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-content {
  padding: 1.25rem;
}

.skeleton-title {
  height: 20px;
  width: 80%;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 0.5rem;
}

.skeleton-author {
  height: 14px;
  width: 50%;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 0.75rem;
}

.skeleton-desc {
  height: 14px;
  width: 100%;
  background: #f0f0f0;
  border-radius: 4px;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: #fff;
  border-radius: 16px;
}

.empty-illustration {
  width: 120px;
  height: 100px;
  margin-bottom: 1.5rem;
}

.book-stack {
  position: relative;
  width: 100%;
  height: 100%;
}

.book {
  position: absolute;
  border-radius: 4px;
}

.b1 {
  width: 50px;
  height: 70px;
  background: linear-gradient(135deg, #e8d5b7 0%, #d4c4a8 100%);
  top: 10px;
  left: 10px;
  transform: rotate(-5deg);
}

.b2 {
  width: 50px;
  height: 70px;
  background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
  top: 0;
  left: 50px;
  transform: rotate(3deg);
}

.empty-state p {
  font-size: 0.95rem;
  color: #888;
  margin: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.pagination-wrapper :deep(.el-pager li) {
  border-radius: 8px;
  margin: 0 2px;
}

.pagination-wrapper :deep(.el-pager li.is-active) {
  background: #1a1a1a;
}

.site-footer {
  background: #1a1a1a;
  color: #fff;
  padding: 4rem 2rem;
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
  color: #888;
  margin: 0 0 2rem;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-links a {
  color: #888;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: #fff;
}

.copyright {
  color: #555;
  font-size: 0.85rem;
  margin: 0;
}

@media (max-width: 1024px) {
  .content-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
  }

  .sidebar-section {
    min-width: 280px;
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

  .page-banner {
    padding: 2rem 1rem;
  }

  .banner-content h2 {
    font-size: 1.75rem;
  }

  .novel-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .card-image {
    height: 180px;
  }
}
</style>
