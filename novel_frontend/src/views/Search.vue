<template>
  <div class="sp-root">
    <header class="sp-header">
      <div class="sp-header__inner">
        <h1 class="sp-logo" @click="goHome">墨香书阁</h1>
        <div class="sp-header__actions">
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="sp-auth-link">登录</router-link>
          </template>
          <template v-else>
            <router-link to="/user" class="sp-user-avatar">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <section class="sp-hero">
      <div class="sp-hero__inner">
        <h2 class="sp-hero__title">寻觅你的故事</h2>
        <p class="sp-hero__sub">在浩瀚书海中，找到那本专属于你的书</p>

        <div class="sp-search-wrap">
          <div class="sp-search-box">
            <svg class="sp-search-box__icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              ref="searchInputRef"
              v-model="keyword"
              type="text"
              class="sp-search-box__input"
              placeholder="搜索书名、作者、分类"
              @keyup.enter="handleSearch"
            />
            <button class="sp-search-box__btn" @click="handleSearch">搜索</button>
          </div>

          <div class="sp-filters" v-if="searched">
            <select v-model="filterStatus" class="sp-filter-select" @change="doSearch">
              <option value="">全部状态</option>
              <option value="0">连载中</option>
              <option value="1">已完结</option>
            </select>
            <select v-model="sortBy" class="sp-filter-select" @change="doSearch">
              <option value="">综合排序</option>
              <option value="-view_count">人气最高</option>
              <option value="-updated_at">最新更新</option>
              <option value="-word_count">字数最多</option>
            </select>
          </div>
        </div>

        <div class="sp-hot" v-if="!searched">
          <span class="sp-hot__label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            热搜
          </span>
          <span
            v-for="(item, i) in hotSearches"
            :key="i"
            class="sp-hot__tag"
            :class="{ 'sp-hot__tag--top': i < 3 }"
            @click="handleHotSearch(item.keyword)"
          >
            {{ item.keyword }}
          </span>
        </div>

        <div class="sp-history" v-if="!searched && searchHistory.length > 0">
          <span class="sp-history__label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            最近搜索
          </span>
          <span
            v-for="(item, i) in searchHistory.slice(0, 5)"
            :key="i"
            class="sp-history__tag"
            @click="handleHistorySearch(item)"
          >
            {{ item }}
            <span class="sp-history__del" @click.stop="deleteHistory(i)">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </span>
          </span>
          <span class="sp-history__clear" @click="clearHistory">清空</span>
        </div>
      </div>
    </section>

    <main class="sp-main">
      <div v-if="keyword && searched">
        <div class="sp-results-header">
          <div class="sp-results-info">
            <span class="sp-results-title">「<em>{{ keyword }}</em>」的搜索结果</span>
            <span class="sp-results-count" v-if="novels.length > 0">共 {{ totalNovels }} 部</span>
          </div>
        </div>

        <div v-if="loading" class="sp-loading">
          <div class="sp-skeleton" v-for="n in 5" :key="n">
            <div class="sp-skeleton__cover"></div>
            <div class="sp-skeleton__body">
              <div class="sp-skeleton__line sp-skeleton__line--w60"></div>
              <div class="sp-skeleton__line sp-skeleton__line--w40"></div>
              <div class="sp-skeleton__line sp-skeleton__line--w80"></div>
              <div class="sp-skeleton__line sp-skeleton__line--w30"></div>
            </div>
          </div>
        </div>

        <div class="sp-results" v-else-if="novels.length > 0">
          <div
            v-for="novel in novels"
            :key="novel.id"
            class="sp-result"
            @click="goToDetail(novel.id)"
          >
            <div class="sp-result__cover-wrap">
              <img
                v-lazy="novel.cover || defaultCover"
                :alt="novel.title"
                class="sp-result__cover"
                @error="onCoverError"
              />
            </div>
            <div class="sp-result__body">
              <h3 class="sp-result__title" v-html="highlightKeyword(novel.title)"></h3>
              <p class="sp-result__author">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <span v-html="highlightKeyword(novel.author)"></span>
              </p>
              <p class="sp-result__desc" v-html="highlightKeyword(novel.description || '暂无简介')"></p>
              <div class="sp-result__meta">
                <span class="sp-meta__badge">{{ novel.category }}</span>
                <span class="sp-meta__item">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  {{ formatCount(novel.view_count) }}
                </span>
                <span class="sp-meta__item">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                  {{ novel.word_count }}字
                </span>
              </div>
            </div>
            <div class="sp-result__arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          </div>
        </div>

        <div class="sp-empty" v-else>
          <svg class="sp-empty__icon" width="120" height="100" viewBox="0 0 120 100" fill="none">
            <rect x="10" y="24" width="30" height="48" rx="3" fill="#E8D5B0" stroke="#CA8A04" stroke-width="1"/>
            <rect x="30" y="18" width="30" height="48" rx="3" fill="#A07850" stroke="#8B6914" stroke-width="1"/>
            <rect x="50" y="28" width="30" height="48" rx="3" fill="#3D5A4A" stroke="#2A4035" stroke-width="1"/>
            <rect x="70" y="22" width="30" height="48" rx="3" fill="#6B4226" stroke="#4A2E1A" stroke-width="1"/>
            <ellipse cx="55" cy="84" rx="50" ry="5" fill="#E0E0E0"/>
          </svg>
          <p class="sp-empty__title">未找到相关书目</p>
          <p class="sp-empty__hint">换个关键词试试，或许会有惊喜</p>
        </div>

        <div class="sp-pagination" v-if="totalPages > 1">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalNovels"
            layout="prev, pager, next"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <div class="sp-welcome" v-else-if="!keyword">
        <div class="sp-welcome__deco">
          <div class="sp-welcome__line"></div>
          <span class="sp-welcome__text">开始你的阅读之旅</span>
          <div class="sp-welcome__line"></div>
        </div>
        <p class="sp-welcome__hint">在上方搜索框输入关键词，即刻开启探索</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { novelApi } from '../api'
import { DEFAULT_COVER } from '../utils/image'

const defaultCover = DEFAULT_COVER
const onCoverError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== defaultCover) img.src = defaultCover
}

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const novels = ref<any[]>([])
const searched = ref(false)
const searchHistory = ref<string[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalNovels = ref(0)
const sortBy = ref('')
const filterStatus = ref('')
const loading = ref(false)
const searchInputRef = ref<HTMLInputElement>()

const totalPages = computed(() => Math.ceil(totalNovels.value / pageSize.value))

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

const escapeHtml = (text: string) => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

const highlightKeyword = (text: string) => {
  if (!keyword.value || !text) return escapeHtml(text)
  const escaped = keyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  return escapeHtml(text).replace(regex, '<span class="highlight">$1</span>')
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
  currentPage.value = 1
  doSearch()
}

const doSearch = async () => {
  loading.value = true
  try {
    const params: any = {
      search: keyword.value,
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (sortBy.value) {
      params.ordering = sortBy.value
    }
    if (filterStatus.value !== '') {
      params.status = filterStatus.value
    }
    const res: any = await novelApi.list(params)
    novels.value = res.results || []
    totalNovels.value = res.count || 0
    searched.value = true
  } catch (error) {
    console.error('搜索失败:', error)
    novels.value = []
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  doSearch()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.sp-root {
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

.sp-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(253, 251, 247, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
}

.sp-header__inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 0.875rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sp-logo {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  cursor: pointer;
  letter-spacing: 0.04em;
}

.sp-header__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sp-auth-link {
  font-size: 0.875rem;
  color: var(--muted);
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.sp-auth-link:hover {
  color: var(--ink);
}

.sp-user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--muted);
  transition: border-color 0.2s, color 0.2s;
  cursor: pointer;
}

.sp-user-avatar:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.sp-hero {
  background: linear-gradient(180deg, #F5F0E8 0%, var(--paper-bg) 100%);
  border-bottom: 1px solid var(--border);
  padding: 3.5rem 2rem 3rem;
}

.sp-hero__inner {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
}

.sp-hero__title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.5rem;
  letter-spacing: 0.05em;
}

.sp-hero__sub {
  font-family: 'Libre Baskerville', 'Noto Sans SC', sans-serif;
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0 0 2rem;
  letter-spacing: 0.03em;
}

.sp-search-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.sp-search-box {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 640px;
  background: var(--card-bg);
  border: 1.5px solid var(--border);
  border-radius: 4px;
  padding: 0 0.5rem 0 1.25rem;
  transition: border-color 0.25s, box-shadow 0.25s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.sp-search-box:focus-within {
  border-color: var(--accent);
  box-shadow: 0 2px 16px rgba(202, 138, 4, 0.12);
}

.sp-search-box__icon {
  color: var(--muted);
  flex-shrink: 0;
  margin-right: 0.75rem;
}

.sp-search-box__input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 1rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--ink);
  padding: 0.85rem 0;
}

.sp-search-box__input::placeholder {
  color: #9CA3AF;
}

.sp-search-box__btn {
  flex-shrink: 0;
  padding: 0.5rem 1.5rem;
  background: var(--ink);
  color: var(--paper-bg);
  border: none;
  border-radius: 3px;
  font-size: 0.9rem;
  font-family: 'Noto Sans SC', sans-serif;
  cursor: pointer;
  transition: background-color 0.2s;
  letter-spacing: 0.04em;
}

.sp-search-box__btn:hover {
  background: var(--accent);
}

.sp-filters {
  display: flex;
  gap: 0.75rem;
}

.sp-filter-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: var(--card-bg);
  font-size: 0.85rem;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--ink);
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.sp-filter-select:focus {
  border-color: var(--accent);
}

.sp-hot {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1.75rem;
}

.sp-hot__label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--muted);
  margin-right: 0.25rem;
}

.sp-hot__tag {
  padding: 0.3rem 0.875rem;
  border: 1px solid var(--border);
  border-radius: 2px;
  font-size: 0.85rem;
  color: var(--muted);
  background: var(--card-bg);
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background-color 0.2s;
  letter-spacing: 0.02em;
}

.sp-hot__tag:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: #FFF9ED;
}

.sp-hot__tag--top {
  border-color: var(--accent);
  color: #92650A;
  background: #FFFBEB;
  font-weight: 500;
}

.sp-history {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-top: 1rem;
}

.sp-history__label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #9CA3AF;
}

.sp-history__tag {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.625rem;
  background: #F3F4F6;
  border-radius: 2px;
  font-size: 0.82rem;
  color: var(--muted);
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}

.sp-history__tag:hover {
  background: #FFF9ED;
  color: var(--accent);
}

.sp-history__del {
  display: flex;
  align-items: center;
  opacity: 0.5;
  transition: opacity 0.2s;
  cursor: pointer;
}

.sp-history__del:hover {
  opacity: 1;
}

.sp-history__clear {
  font-size: 0.78rem;
  color: #9CA3AF;
  cursor: pointer;
  margin-left: 0.25rem;
  transition: color 0.2s;
}

.sp-history__clear:hover {
  color: #EF4444;
}

.sp-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
}

.sp-results-header {
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.sp-results-info {
  display: flex;
  align-items: baseline;
  gap: 1rem;
}

.sp-results-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.1rem;
  color: var(--ink);
}

.sp-results-title em {
  font-style: normal;
  color: var(--accent);
  font-weight: 600;
}

.sp-results-count {
  font-size: 0.85rem;
  color: #9CA3AF;
}

.sp-loading {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sp-skeleton {
  display: flex;
  gap: 1.25rem;
  padding: 1.25rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.sp-skeleton__cover {
  width: 76px;
  height: 104px;
  background: linear-gradient(90deg, #F0EDE8 25%, #E8E4DC 50%, #F0EDE8 75%);
  background-size: 200% 100%;
  border-radius: 3px;
  animation: sp-shimmer 1.5s infinite;
  flex-shrink: 0;
}

.sp-skeleton__body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding-top: 0.25rem;
}

.sp-skeleton__line {
  height: 12px;
  background: linear-gradient(90deg, #F0EDE8 25%, #E8E4DC 50%, #F0EDE8 75%);
  background-size: 200% 100%;
  border-radius: 2px;
  animation: sp-shimmer 1.5s infinite;
}

.sp-skeleton__line--w30 { width: 30%; }
.sp-skeleton__line--w40 { width: 40%; }
.sp-skeleton__line--w60 { width: 60%; }
.sp-skeleton__line--w80 { width: 80%; }

@keyframes sp-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.sp-results {
  display: flex;
  flex-direction: column;
}

.sp-result {
  display: flex;
  align-items: flex-start;
  gap: 1.25rem;
  padding: 1.25rem 1rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-bottom: none;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.sp-result:first-child {
  border-radius: 4px 4px 0 0;
}

.sp-result:last-child {
  border-bottom: 1px solid var(--border);
  border-radius: 0 0 4px 4px;
}

.sp-result:only-child {
  border-radius: 4px;
  border-bottom: 1px solid var(--border);
}

.sp-result:hover {
  background: #FFFBEF;
}

.sp-result__cover-wrap {
  flex-shrink: 0;
  width: 76px;
  height: 104px;
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.08);
}

.sp-result__cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.sp-result__body {
  flex: 1;
  min-width: 0;
}

.sp-result__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.4rem;
  line-height: 1.4;
}

.sp-result__title :deep(.highlight) {
  color: var(--accent);
  background: #FFF9C4;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 700;
}

.sp-result__author {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.83rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
}

.sp-result__author :deep(.highlight) {
  color: var(--accent);
  background: #FFF9C4;
  padding: 0 2px;
  border-radius: 2px;
}

.sp-result__desc {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.65;
  margin: 0 0 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sp-result__desc :deep(.highlight) {
  color: var(--accent);
  background: #FFF9C4;
  padding: 0 2px;
  border-radius: 2px;
}

.sp-result__meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.sp-meta__badge {
  padding: 0.15rem 0.6rem;
  background: #F3F4F6;
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.76rem;
  border-radius: 2px;
  letter-spacing: 0.02em;
}

.sp-meta__item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.8rem;
  color: #9CA3AF;
}

.sp-result__arrow {
  color: #D1D5DB;
  align-self: center;
  flex-shrink: 0;
  transition: color 0.2s;
}

.sp-result:hover .sp-result__arrow {
  color: var(--accent);
}

.sp-empty {
  padding: 5rem 2rem;
  text-align: center;
}

.sp-empty__icon {
  margin-bottom: 1rem;
}

.sp-empty__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.sp-empty__hint {
  font-size: 0.875rem;
  color: #9CA3AF;
  margin: 0.5rem 0 0;
}

.sp-pagination {
  display: flex;
  justify-content: center;
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.sp-pagination :deep(.el-pagination.is-background .el-pager li.is-active) {
  background: var(--accent);
}

.sp-welcome {
  padding: 5rem 2rem;
  text-align: center;
}

.sp-welcome__deco {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  justify-content: center;
  margin-bottom: 1.25rem;
}

.sp-welcome__line {
  flex: 1;
  max-width: 120px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
}

.sp-welcome__text {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.2rem;
  color: var(--ink);
  letter-spacing: 0.08em;
}

.sp-welcome__hint {
  font-size: 0.875rem;
  color: #9CA3AF;
  margin: 0;
  letter-spacing: 0.03em;
}

@media (max-width: 768px) {
  .sp-hero {
    padding: 2.5rem 1.25rem 2rem;
  }

  .sp-hero__title {
    font-size: 1.5rem;
  }

  .sp-search-box {
    padding: 0 0.375rem 0 1rem;
  }

  .sp-search-box__btn {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
  }

  .sp-main {
    padding: 1.5rem 1rem;
  }

  .sp-result {
    padding: 1rem 0.75rem;
    gap: 0.875rem;
  }

  .sp-result__cover-wrap {
    width: 60px;
    height: 84px;
  }

  .sp-result__arrow {
    display: none;
  }

  .sp-header__inner {
    padding: 0.75rem 1.25rem;
  }
}

@media (max-width: 375px) {
  .sp-hero {
    padding: 2rem 1rem 1.5rem;
  }

  .sp-hero__title {
    font-size: 1.25rem;
  }

  .sp-main {
    padding: 1rem 0.75rem;
  }

  .sp-result__cover-wrap {
    width: 52px;
    height: 72px;
  }
}
</style>
