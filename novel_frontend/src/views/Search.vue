<template>
  <div class="search-page">
    <header class="site-header">
      <div class="header-content">
        <h1 class="logo" @click="goHome">墨香书阁</h1>
        <div class="search-bar">
          <el-input
            v-model="keyword"
            placeholder="搜索书名或作者..."
            size="large"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="handleSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
        <div class="header-actions">
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

    <main class="main-content">
      <div class="search-container">
        <aside class="search-sidebar">
          <div class="hot-search" v-if="!searched">
            <h3 class="sidebar-title">
              <el-icon><Star /></el-icon>
              热门搜索
            </h3>
            <ul class="hot-list">
              <li
                v-for="(item, index) in hotSearches"
                :key="index"
                :class="{ top: index < 3 }"
                @click="handleHotSearch(item.keyword)"
              >
                <span class="rank">{{ index + 1 }}</span>
                <span class="keyword">{{ item.keyword }}</span>
                <span class="heat">{{ item.heat }}</span>
              </li>
            </ul>
          </div>

          <div class="search-history" v-if="searchHistory.length > 0">
            <h3 class="sidebar-title">
              <el-icon><Clock /></el-icon>
              搜索历史
            </h3>
            <ul class="history-list">
              <li
                v-for="(item, index) in searchHistory"
                :key="index"
                @click="handleHistorySearch(item)"
              >
                <span class="keyword">{{ item }}</span>
                <el-icon class="delete" @click.stop="deleteHistory(index)"><Close /></el-icon>
              </li>
            </ul>
            <el-button size="small" text @click="clearHistory">清空历史</el-button>
          </div>
        </aside>

        <div class="search-results">
          <div v-if="keyword && searched">
            <div class="results-header">
              <h2>搜索结果：<span class="keyword-highlight">{{ keyword }}</span></h2>
              <span class="results-count" v-if="novels.length > 0">找到 {{ novels.length }} 部小说</span>
            </div>

            <div class="results-list" v-if="novels.length > 0">
              <div
                v-for="novel in novels"
                :key="novel.id"
                class="result-item"
                @click="goToDetail(novel.id)"
              >
                <img v-lazy="novel.cover || '/placeholder.png'" :alt="novel.title" class="result-cover" />
                <div class="result-info">
                  <h3 v-html="highlightKeyword(novel.title)"></h3>
                  <p class="result-author">
                    <el-icon><User /></el-icon>
                    <span v-html="highlightKeyword(novel.author)"></span>
                  </p>
                  <p class="result-desc" v-html="highlightKeyword(novel.description || '暂无简介')"></p>
                  <div class="result-meta">
                    <span class="meta-item">
                      <el-icon><Collection /></el-icon>
                      {{ novel.category }}
                    </span>
                    <span class="meta-item">
                      <el-icon><View /></el-icon>
                      {{ formatCount(novel.view_count) }}
                    </span>
                    <span class="meta-item">
                      <el-icon><Document /></el-icon>
                      {{ novel.word_count }}字
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="no-result" v-else>
              <el-empty description="未找到相关小说，换个关键词试试吧~">
                <template #image>
                  <div class="empty-illustration">
                    <div class="book-stack">
                      <div class="book b1"></div>
                      <div class="book b2"></div>
                      <div class="book b3"></div>
                    </div>
                  </div>
                </template>
              </el-empty>
            </div>
          </div>

          <div class="search-tips" v-else-if="!keyword">
            <div class="tips-content">
              <h2>发现你的下一个故事</h2>
              <p>输入关键词开始搜索</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, User, Star, Clock, Close, Collection, View, Document } from '@element-plus/icons-vue'
import { novelApi, type Novel } from '../api'

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const novels = ref<Novel[]>([])
const searched = ref(false)
const searchHistory = ref<string[]>([])

const isLoggedIn = computed(() => !!localStorage.getItem('user'))

const hotSearches = ref([
  { keyword: '斗破苍穹', heat: '123万' },
  { keyword: '凡人修仙传', heat: '98万' },
  { keyword: '完美世界', heat: '89万' },
  { keyword: '全职高手', heat: '76万' },
  { keyword: '庆余年', heat: '65万' },
  { keyword: '择天记', heat: '54万' },
  { keyword: '雪中悍刀行', heat: '48万' },
  { keyword: '诡秘之主', heat: '42万' },
])

const formatCount = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const highlightKeyword = (text: string) => {
  if (!keyword.value || !text) return text
  const regex = new RegExp(`(${keyword.value})`, 'gi')
  return text.replace(regex, '<span class="highlight">$1</span>')
}

const loadHistory = () => {
  const history = localStorage.getItem('searchHistory')
  if (history) {
    searchHistory.value = JSON.parse(history)
  }
}

const saveHistory = (kw: string) => {
  if (!kw.trim()) return
  const history = searchHistory.value.filter((h) => h !== kw)
  history.unshift(kw)
  if (history.length > 10) history.pop()
  searchHistory.value = history
  localStorage.setItem('searchHistory', JSON.stringify(history))
}

const deleteHistory = (index: number) => {
  searchHistory.value.splice(index, 1)
  localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
}

const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem('searchHistory')
}

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  saveHistory(keyword.value)
  try {
    const res = await novelApi.search(keyword.value)
    novels.value = res.results || []
    searched.value = true
  } catch (error) {
    console.error('搜索失败:', error)
    novels.value = []
  }
}

const handleHotSearch = (kw: string) => {
  keyword.value = kw
  handleSearch()
}

const handleHistorySearch = (kw: string) => {
  keyword.value = kw
  handleSearch()
}

const goToDetail = (id: number) => {
  router.push({ name: 'NovelDetail', params: { id } })
}

const goHome = () => {
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadHistory()
  const q = route.query.q as string
  if (q) {
    keyword.value = q
    handleSearch()
  }
})
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background: #faf8f5;
}

.site-header {
  background: rgba(250, 248, 245, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
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

.search-bar {
  flex: 1;
  max-width: 500px;
}

.search-bar :deep(.el-input__wrapper) {
  border-radius: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
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

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-container {
  display: flex;
  gap: 2rem;
}

.search-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #1a1a1a;
}

.hot-search {
  background: #fff;
  padding: 1.25rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.hot-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.hot-list li {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  cursor: pointer;
  transition: color 0.2s;
}

.hot-list li:hover .keyword {
  color: #1a1a1a;
}

.hot-list li.top .rank {
  background: #ff4757;
  color: #fff;
}

.hot-list .rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background: #e5e5e5;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #888;
  margin-right: 0.75rem;
}

.hot-list .keyword {
  flex: 1;
  font-size: 0.9rem;
  color: #333;
}

.hot-list .heat {
  font-size: 0.75rem;
  color: #aaa;
}

.search-history {
  background: #fff;
  padding: 1.25rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0 0 0.75rem;
}

.history-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0;
  cursor: pointer;
  font-size: 0.85rem;
  color: #666;
}

.history-list li:hover {
  color: #1a1a1a;
}

.history-list li .delete {
  opacity: 0;
  transition: opacity 0.2s;
}

.history-list li:hover .delete {
  opacity: 1;
}

.search-results {
  flex: 1;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.results-header h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.25rem;
  margin: 0;
  color: #1a1a1a;
}

.keyword-highlight {
  color: #ff4757;
}

.results-count {
  font-size: 0.85rem;
  color: #888;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  display: flex;
  gap: 1.25rem;
  padding: 1.25rem;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.result-item:hover {
  border-color: #1a1a1a;
  transform: translateX(4px);
}

.result-cover {
  width: 80px;
  height: 110px;
  object-fit: cover;
  border-radius: 6px;
  background: #f0f0f0;
  flex-shrink: 0;
}

.result-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.result-info h3 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
  color: #1a1a1a;
}

.result-info h3 :deep(.highlight) {
  background: #fff3cf;
  color: #ff4757;
  padding: 0 2px;
  border-radius: 2px;
}

.result-author {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #888;
  margin: 0 0 0.5rem;
}

.result-author :deep(.highlight) {
  background: #fff3cf;
  color: #ff4757;
  padding: 0 2px;
  border-radius: 2px;
}

.result-desc {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.6;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-desc :deep(.highlight) {
  background: #fff3cf;
  color: #ff4757;
  padding: 0 2px;
  border-radius: 2px;
}

.result-meta {
  display: flex;
  gap: 1rem;
  margin-top: auto;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #999;
}

.no-result {
  padding: 3rem;
  background: #fff;
  border-radius: 12px;
}

.empty-illustration {
  width: 120px;
  height: 100px;
  margin: 0 auto;
  position: relative;
}

.book-stack {
  position: relative;
  width: 100%;
  height: 100%;
}

.book {
  position: absolute;
  width: 40px;
  height: 60px;
  border-radius: 3px;
}

.b1 {
  background: linear-gradient(135deg, #e8d5b7 0%, #d4c4a8 100%);
  top: 15px;
  left: 10px;
  transform: rotate(-6deg);
}

.b2 {
  background: linear-gradient(135deg, #8b7355 0%, #6b5344 100%);
  top: 10px;
  left: 35px;
  transform: rotate(-1deg);
}

.b3 {
  background: linear-gradient(135deg, #2d4a3e 0%, #1a2f28 100%);
  top: 5px;
  left: 60px;
  transform: rotate(3deg);
}

.search-tips {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: #fff;
  border-radius: 12px;
}

.tips-content {
  text-align: center;
}

.tips-content h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.75rem;
  color: #1a1a1a;
  margin: 0 0 0.5rem;
}

.tips-content p {
  color: #888;
  font-size: 1rem;
  margin: 0;
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }

  .search-bar {
    order: 3;
    width: 100%;
    max-width: none;
    margin-top: 1rem;
  }

  .search-container {
    flex-direction: column;
  }

  .search-sidebar {
    width: 100%;
    display: flex;
    gap: 1rem;
    overflow-x: auto;
  }

  .hot-search,
  .search-history {
    min-width: 240px;
  }
}
</style>
