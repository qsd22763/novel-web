<template>
  <div class="novel-list-page">
    <!-- ===== 顶部导航 ===== -->
    <header class="site-header">
      <div class="header-inner">
        <h1 class="logo" @click="goHome">墨香书阁</h1>
        <nav class="main-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/author">创作</router-link>
        </nav>
        <div class="header-actions">
          <div class="search-bar" @click="$refs.searchInputRef && $refs.searchInputRef.focus()">
            <svg class="search-bar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <el-input ref="searchInputRef" v-model="searchKeyword" placeholder="搜索书名、作者、分类" class="search-bar__input-inner" @keyup.enter="handleSearch" />
          </div>
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

    <!-- ===== 页面标题区 ===== -->
    <div class="page-head">
      <div class="page-head-inner">
        <nav class="breadcrumb" aria-label="breadcrumb">
          <router-link to="/" class="bc-item">首页</router-link>
          <span class="bc-sep">/</span>
          <span class="bc-item bc-current">书库</span>
          <template v-if="selectedCategory">
            <span class="bc-sep">/</span>
            <span class="bc-item bc-current">{{ selectedCategory }}</span>
          </template>
        </nav>
        <h2 class="page-title">{{ selectedCategory || '全部藏书' }}</h2>
        <p class="page-subtitle">共收录 <em>{{ totalNovels }}</em> 部作品，静心阅读，品味文字之美</p>
      </div>
    </div>

    <!-- ===== 主内容区 ===== -->
    <main class="main-content">
      <div class="content-layout">

        <!-- 左侧栏：分类 + 筛选 + 榜单 -->
        <aside class="sidebar">

          <!-- 分类 -->
          <div class="sidebar-card">
            <div class="sb-head">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#CA8A04" stroke-width="1.8"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
              <span>分类</span>
            </div>
            <ul class="cat-list">
              <li :class="{ active: !selectedCategory }" @click="selectCategory('')">
                <span>全部</span><em>{{ totalNovels }}</em>
              </li>
              <li v-for="cat in categories" :key="cat.name" :class="{ active: selectedCategory === cat.name }" @click="selectCategory(cat.name)">
                <span>{{ cat.name }}</span><em>{{ cat.count }}</em>
              </li>
            </ul>
          </div>

          <!-- 筛选 -->
          <div class="sidebar-card">
            <div class="sb-head">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#CA8A04" stroke-width="1.8"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
              <span>筛选</span>
            </div>
            <div class="filter-group">
              <label class="fl-label">连载状态</label>
              <div class="fl-chips">
                <button :class="{ on: filterStatus === '' }" @click="filterStatus = ''; handleFilterChange()">全部</button>
                <button :class="{ on: filterStatus === '0' }" @click="filterStatus = '0'; handleFilterChange()">连载中</button>
                <button :class="{ on: filterStatus === '1' }" @click="filterStatus = '1'; handleFilterChange()">已完结</button>
              </div>
            </div>
            <div class="filter-group">
              <label class="fl-label">字数范围</label>
              <el-select v-model="filterWordCount" size="small" placeholder="选择字数" class="fl-select" @change="handleFilterChange">
                <el-option label="全部" value="" />
                <el-option label="30万以下" value="0-300000" />
                <el-option label="30-50万" value="300000-500000" />
                <el-option label="50-100万" value="500000-1000000" />
                <el-option label="100-200万" value="1000000-2000000" />
                <el-option label="200万以上" value="2000000-" />
              </el-select>
            </div>
          </div>

          <!-- 人气榜单 -->
          <div class="sidebar-card sb-rank">
            <div class="sb-head">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#CA8A04" stroke-width="1.8"><path d="M6 9H4.5a2.5 2.5 0 010-5H6"/><path d="M18 9h1.5a2.5 2.5 0 010-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0012 0V2Z"/></svg>
              <span>人气榜单</span>
            </div>
            <ol class="rank-list">
              <li v-for="(novel, idx) in topNovels" :key="novel.id" @click="goToDetail(novel.id)">
                <span class="rk-num" :class="{ g: idx===0, s: idx===1, b: idx===2 }">{{ idx + 1 }}</span>
                <div class="rk-body">
                  <span class="rk-name">{{ novel.title }}</span>
                  <span class="rk-views">{{ formatCount(novel.view_count) }} 阅读</span>
                </div>
              </li>
            </ol>
          </div>

        </aside>

        <!-- 右侧：书籍列表 -->
        <section class="novels-section">

          <!-- 工具栏 -->
          <div class="toolbar">
            <div class="tb-left">
              <strong>{{ selectedCategory || '全部作品' }}</strong>
              <span class="tb-count">· {{ totalNovels }} 部</span>
            </div>
            <div class="tb-right">
              <span class="tb-sort-label">排序</span>
              <el-select v-model="sortBy" size="small" class="sort-sel" @change="handleSort">
                <el-option label="默认排序" value="default" />
                <el-option label="更新时间" value="updated" />
                <el-option label="人气最高" value="views" />
                <el-option label="字数最多" value="words" />
                <el-option label="收藏最多" value="recommend" />
              </el-select>
            </div>
          </div>

          <!-- 书籍网格 -->
          <div class="novel-grid" v-if="!loading && novels.length > 0">
            <article v-for="novel in novels" :key="novel.id" class="novel-card" @click="goToDetail(novel.id)">
              <div class="nc-cover">
                <img v-lazy="novel.cover || defaultCover" :alt="novel.title" @error="onCoverError" />
                <div class="nc-overlay">
                  <span class="nc-read-btn">开始阅读</span>
                </div>
                <span class="nc-badge" :class="{ done: novel.status === 1 }">{{ novel.status === 1 ? '完结' : '连载' }}</span>
              </div>
              <div class="nc-body">
                <h3 class="nc-title">{{ novel.title }}</h3>
                <p class="nc-author">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  {{ novel.author }}
                </p>
                <div class="nc-tags">
                  <span class="nc-tag nc-tag--cat">{{ novel.category }}</span>
                  <span class="nc-tag nc-tag--wc">{{ formatWordCount(novel.word_count) }}</span>
                </div>
                <p class="nc-desc">{{ novel.description || '暂无简介' }}</p>
                <div class="nc-meta">
                  <span class="nc-meta__item">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    {{ formatCount(novel.view_count) }}
                  </span>
                  <span class="nc-meta__item">{{ formatDate(novel.updated_at) }}</span>
                </div>
              </div>
            </article>
          </div>

          <!-- 骨架屏 -->
          <div class="novel-grid sk-grid" v-else-if="loading">
            <div class="sk-card" v-for="i in 16" :key="i">
              <div class="sk-cover"></div>
              <div class="sk-bd">
                <div class="sk-ln" style="width:72%;height:14px"></div>
                <div class="sk-ln" style="width:45%;height:11px;margin-top:6px"></div>
                <div class="sk-ln" style="width:90%;height:10px;margin-top:8px"></div>
                <div class="sk-ln" style="width:60%;height:10px;margin-top:5px"></div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div class="empty-state" v-else>
            <svg width="48" height="48" viewBox="0 0 64 64" fill="none">
              <rect x="14" y="10" width="26" height="38" rx="2" fill="#F5F1EA" stroke="#E0D6CC" stroke-width="1.2"/>
              <circle cx="27" cy="22" r="3.5" fill="#E8DDD0"/>
              <line x1="19" y1="29" x2="35" y2="29" stroke="#E0D6CC" stroke-width="1.2"/>
              <line x1="19" y1="34" x2="30" y2="34" stroke="#E0D6CC" stroke-width="1.2"/>
            </svg>
            <p class="empty-title">此处空空如也</p>
            <p class="empty-hint">换个分类试试吧</p>
          </div>

          <!-- 分页 -->
          <div class="pagination-bar" v-if="totalPages > 1">
            <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="totalNovels" layout="prev, pager, next" @current-change="handlePageChange" />
          </div>

        </section>

      </div>
    </main>

    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">墨香书阁</span>
          <p>让阅读成为一种习惯</p>
        </div>
        <div class="footer-links">
          <a href="#">关于我们</a>
          <a href="#">联系方式</a>
          <a href="#">用户协议</a>
          <a href="#">隐私政策</a>
        </div>
        <p class="copyright">&copy; 2026 墨香书阁 &middot; All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User } from '@element-plus/icons-vue'
import { novelApi, type Novel } from '../api'
import { DEFAULT_COVER } from '../utils/image'

const defaultCover = DEFAULT_COVER
const onCoverError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== defaultCover) img.src = defaultCover
}

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

interface Category { name: string; icon: string; count: number }
const categories = ref<Category[]>([])

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
  const diff = Date.now() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今日'
  if (days === 1) return '昨日'
  if (days < 7) return days + '天前'
  if (days < 30) return Math.floor(days / 7) + '周前'
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const loadNovels = async () => {
  loading.value = true; novels.value = []
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (selectedCategory.value) params.category = selectedCategory.value
    if (filterStatus.value !== '') params.status = filterStatus.value
    if (filterWordCount.value) { const [min, max] = filterWordCount.value.split('-'); if (min) params.word_count_min = min; if (max) params.word_count_max = max }
    if (sortBy.value === 'views') params.ordering = '-view_count'
    else if (sortBy.value === 'words') params.ordering = '-word_count'
    else if (sortBy.value === 'updated') params.ordering = '-updated_at'
    else if (sortBy.value === 'recommend') params.ordering = '-view_count'

    const res = await novelApi.list(params)
    novels.value = res.results || []; totalNovels.value = res.count || 0
  } catch (error) { console.error('加载小说列表失败:', error) }
  finally { loading.value = false }
}

const loadCategoryStats = async () => {
  try {
    const res: any = await novelApi.category_stats()
    // 动态构建分类列表（后端返回 {分类名: 数量}）
    categories.value = Object.keys(res || {}).map(name => ({
      name,
      icon: '',
      count: res[name] || 0,
    })).sort((a, b) => b.count - a.count)
  } catch (e) { console.error('加载分类统计失败:', e) }
}

const handleFilterChange = () => { currentPage.value = 1; loadNovels() }

const loadTopNovels = async () => {
  try {
    const res = await novelApi.list({ page_size: 5, ordering: '-view_count' })
    topNovels.value = (res.results || []).slice(0, 5)
  } catch (e) { console.error('加载榜单失败:', e) }
}

const selectCategory = (cat: string) => { selectedCategory.value = cat; currentPage.value = 1; loadNovels() }
const handleSort = () => { currentPage.value = 1; loadNovels() }
const handlePageChange = (page: number) => { currentPage.value = page; loadNovels(); window.scrollTo({ top: 0, behavior: 'smooth' }) }
const handleSearch = () => { if (searchKeyword.value.trim()) router.push({ name: 'Search', query: { q: searchKeyword.value } }) }
const goToDetail = (id: number) => router.push({ name: 'NovelDetail', params: { id } })
const goHome = () => router.push({ name: 'Home' })

onMounted(() => {
  const category = route.query.category as string
  if (category) selectedCategory.value = category
  loadNovels(); loadTopNovels(); loadCategoryStats()
  try { const user = JSON.parse(localStorage.getItem('user') || '{}'); userAvatar.value = user.avatar || '' } catch {}
})

watch(() => route.query.category, (newCat) => { selectedCategory.value = (newCat as string) || ''; loadNovels() })
</script>

<style scoped>
/* ============================================================
   书库页面 — Luxury Refined 风格（与详情页统一）
   ============================================================
   设计方向：Editorial / Warm Paper / Gold Accent
   字体：系统安全栈，零外部依赖
   配色：暖纸色底 + 金色强调 #CA8A04 + 低饱和辅助色
   ============================================================ */

:root {
  --ink: #1A1A1A;
  --muted: #6B7280;
  --subtle: #9CA3AF;
  --accent: #CA8A04;
  --accent-light: rgba(202,138,4,.07);
  --border: #E5DED4;
  --border-light: #EEE9E1;
  --card: #FFFEFA;
  --card-alt: #FCFBF7;
  --ff-base: system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
  --ff-serif: Georgia, "SimSun", "STSong", serif;
  --r-sm: 6px; --r-md: 8px;
  --t: all 180ms ease;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.05);
  --shadow-md: 0 3px 12px rgba(0,0,0,.06);
  --shadow-lg: 0 8px 28px rgba(0,0,0,.08);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

.novel-list-page {
  min-height: 100vh;
  background:
    linear-gradient(175deg, #FAF8F5 0%, #FDFBF7 40%, #F6F2EC 100%),
    radial-gradient(circle at 85% 10%, rgba(202,138,4,.03) 0%, transparent 50%);
  color: var(--ink); font-family: var(--ff-base);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ==================== 导航栏 ====================
   实心半透明背景（无 backdrop-filter），与详情页统一 */
.site-header {
  position: sticky; top: 0; z-index: 100;
  background: rgba(253,251,247,.92);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.header-inner {
  max-width: 1280px; margin: 0 auto;
  padding: 0 1.5rem; height: 56px;
  display: flex; align-items: center; gap: 2rem;
}
.logo {
  font-family: var(--ff-serif); font-size: 1.2rem; font-weight: 700;
  color: var(--ink); cursor: pointer; letter-spacing: 2px; user-select: none; white-space: nowrap;
}
.logo:hover { opacity: .72; }

.main-nav { display: flex; gap: .2rem; }
.main-nav a {
  font-size: .82rem; color: var(--muted); text-decoration: none;
  padding: 6px 14px; border-radius: var(--r-sm); transition: var(--t); letter-spacing: .2px;
}
.main-nav a:hover { color: var(--accent); background: var(--accent-light); }
/* 当前页高亮：金色而非紫色，与全站统一 */
.main-nav a.router-link-active {
  color: var(--accent); font-weight: 600;
  background: var(--accent-light);
  box-shadow: inset 0 0 0 1px rgba(202,138,4,.15);
}

.header-actions { display: flex; align-items: center; gap: .75rem; margin-left: auto; }

.search-bar {
  position: relative; display: flex; align-items: center;
  width: 260px; background: #FAF8F5; border: 1px solid var(--border-light);
  border-radius: 22px; padding: 0 14px; height: 36px; cursor: text; transition: border-color .18s;
}
.search-bar:hover, .search-bar:focus-within { border-color: var(--border); background: #FFF; }
.search-bar__icon { width: 15px; height: 15px; color: var(--subtle); flex-shrink: 0; }
.search-bar__input-inner { width: 100%; }
.search-bar__input-inner :deep(.el-input__wrapper) { background: transparent !important; box-shadow: none !important; border: none !important; padding-left: 26px; }
.search-bar__input-inner :deep(.el-input__inner) { font-size: .82rem; color: var(--ink); }
.search-bar__input-inner :deep(.el-input__inner::placeholder) { color: var(--subtle); }

.auth-link {
  font-size: .82rem; color: var(--muted); text-decoration: none;
  padding: 6px 14px; border-radius: var(--r-sm); border: 1px solid var(--border-light); transition: var(--t);
}
.auth-link:hover { border-color: var(--accent); color: var(--accent); }

.user-avatar {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #F5F2EE, #EBE6DD);
  border: 1px solid var(--border-light); transition: var(--t);
}
.user-avatar:hover { border-color: var(--accent); }
.user-avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }

/* ==================== 页面标题 ==================== */
.page-head {
  background: linear-gradient(180deg, var(--card) 0%, var(--card-alt) 100%);
  border-bottom: 1px solid var(--border-light);
  padding: 1.5rem 0 1.25rem;
}
.page-head-inner {
  max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
}
.breadcrumb { display: flex; align-items: center; gap: .35rem; margin-bottom: .65rem; }
.bc-item { font-size: .78rem; color: var(--muted); text-decoration: none; transition: color .15s; }
a.bc-item:hover { color: var(--accent); }
.bc-current { color: var(--ink); font-weight: 500; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bc-sep { font-size: .7rem; color: var(--border); }

.page-title {
  font-family: var(--ff-serif); font-size: 1.5rem; font-weight: 700;
  color: var(--ink); letter-spacing: 2px; margin: 0 0 .3rem;
}
.page-subtitle { font-size: .82rem; color: var(--muted); margin: 0; letter-spacing: .2px; }
.page-subtitle em { font-style: normal; color: var(--accent); font-weight: 600; }

/* ==================== 主内容 ==================== */
.main-content { max-width: 1280px; margin: 0 auto; padding: 1.5rem 1.5rem 2.5rem; }
.content-layout { display: flex; gap: 1.5rem; align-items: flex-start; }

/* ==================== 侧边栏 ====================
   统一卡片容器：浅底色 + 细边框 + 圆角 */
.sidebar { width: 230px; flex-shrink: 0; display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 70px; }

.sidebar-card {
  background: var(--card); border: 1px solid var(--border-light);
  border-radius: var(--r-md); padding: 1rem 1.1rem; box-shadow: var(--shadow-sm);
}
.sb-head {
  display: flex; align-items: center; gap: .4rem;
  font-size: .82rem; font-weight: 600; color: var(--ink);
  padding-bottom: .7rem; margin-bottom: .7rem;
  border-bottom: 1px solid var(--border-light); letter-spacing: .3px;
}

/* ---- 分类按钮：圆角药丸式 ---- */
.cat-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.cat-list li {
  display: flex; align-items: center; justify-content: space-between;
  padding: 7px 12px; border-radius: 20px;
  cursor: pointer; border: 1px solid transparent;
  font-size: .81rem; color: var(--ink); transition: all 180ms ease;
}
.cat-list li:hover { background: var(--accent-light); border-color: rgba(202,138,4,.2); }
.cat-list li.active {
  background: linear-gradient(135deg, #FEF7E0, #FEF3CD);
  border-color: rgba(202,138,4,.3);
  color: #92400E; font-weight: 600;
}
.cat-list li em {
  font-style: normal; font-size: .7rem; color: var(--subtle);
  background: #F3F0EB; padding: 1px 8px; border-radius: 10px; min-width: 26px; text-align: center;
}
.cat-list li.active em {
  background: var(--accent); color: #fff;
}

/* ---- 筛选组 ---- */
.filter-group { margin-bottom: .85rem; }
.filter-group:last-child { margin-bottom: 0; }
.fl-label { display: block; font-size: .74rem; color: var(--muted); margin-bottom: .4rem; letter-spacing: .2px; }
.fl-chips { display: flex; gap: 5px; }
.fl-chips button {
  flex: 1; padding: 5px 0; font-family: var(--ff-base); font-size: .76rem;
  border: 1px solid var(--border-light); background: var(--card); color: var(--muted);
  border-radius: 16px; cursor: pointer; transition: all 180ms ease;
}
.fl-chips button:hover { border-color: var(--accent); color: var(--accent); }
.fl-chips button.on {
  background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600;
}
.fl-select { width: 100%; }
.fl-select :deep(.el-select__wrapper) { box-shadow: none !important; border: 1px solid var(--border-light) !important; border-radius: var(--r-sm); font-size: .78rem; }
.fl-select :deep(.el-select__wrapper:hover) { border-color: var(--accent) !important; }

/* ---- 榜单 ---- */
.rank-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0; }
.rank-list li {
  display: flex; align-items: center; gap: 8px;
  padding: .55rem 0; cursor: pointer;
  border-bottom: 1px dashed var(--border-light); transition: background .15s;
  border-radius: 4px; margin: 0 -.3rem; padding-left: .3rem; padding-right: .3rem;
}
.rank-list li:last-child { border-bottom: none; }
.rank-list li:hover { background: var(--accent-light); }

.rk-num {
  display: flex; align-items: center; justify-content: center;
  width: 20px; height: 20px; font-size: .72rem; font-weight: 700;
  border-radius: 4px; background: #F3F0EB; color: var(--muted); flex-shrink: 0;
}
.rk-num.g { background: var(--accent); color: #fff; }
.rk-num.s { background: #9CA3AF; color: #fff; }
.rk-num.b { background: #B45309; color: #fff; }
.rk-body { flex: 1; display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.rk-name { font-size: .8rem; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rk-views { font-size: .68rem; color: var(--subtle); }

/* ==================== 工具栏 ==================== */
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: .75rem 1.1rem; background: var(--card); border: 1px solid var(--border-light);
  border-radius: var(--r-md); margin-bottom: 1.25rem; box-shadow: var(--shadow-sm);
}
.tb-left { display: flex; align-items: baseline; gap: .35rem; }
.tb-left strong { font-family: var(--ff-serif); font-size: .95rem; font-weight: 700; }
.tb-count { font-size: .78rem; color: var(--muted); }
.tb-right { display: flex; align-items: center; gap: .4rem; }
.tb-sort-label { font-size: .78rem; color: var(--muted); }
.sort-sel { width: 115px; }
.sort-sel :deep(.el-select__wrapper) { box-shadow: none !important; border: 1px solid var(--border-light) !important; border-radius: var(--r-sm); font-size: .78rem; }
.sort-sel :deep(.el-select__wrapper:hover) { border-color: var(--accent) !important; }

/* ==================== 书籍网格 ==================== */
.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(172px, 1fr));
  gap: 1.25rem;
}

.novel-card {
  background: var(--card); border: 1px solid var(--border-light);
  border-radius: var(--r-md); overflow: hidden; cursor: pointer;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.novel-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg), 0 0 0 1px rgba(202,138,4,.08);
  border-color: rgba(202,138,4,.25);
}

.nc-cover {
  position: relative; width: 100%; aspect-ratio: 3/4;
  overflow: hidden; background: #EDE8DF;
}
.nc-cover img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  transition: transform .32s ease;
}
.novel-card:hover .nc-cover img { transform: scale(1.05); }

.nc-overlay {
  position: absolute; inset: 0;
  background: rgba(26,26,26,.5);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity .25s ease;
}
.novel-card:hover .nc-overlay { opacity: 1; }
.nc-read-btn {
  padding: 7px 20px; background: var(--accent); color: #fff;
  font-size: .82rem; font-weight: 600; border-radius: 20px;
  letter-spacing: .5px; transform: translateY(8px); transition: transform .25s ease;
}
.novel-card:hover .nc-read-btn { transform: translateY(0); }

.nc-badge {
  position: absolute; bottom: 8px; right: 8px;
  padding: 2px 8px; font-size: .65rem; font-weight: 600;
  border-radius: 10px; letter-spacing: .3px;
  background: rgba(59,130,246,.88); color: #fff;
}
.nc-badge.done { background: rgba(202,138,4,.9); }

/* 卡片信息体 */
.nc-body { padding: .85rem .9rem; }
.nc-title {
  font-family: var(--ff-base); font-size: .88rem; font-weight: 700;
  color: var(--ink); margin: 0 0 .3rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.3;
}
.nc-author {
  display: flex; align-items: center; gap: 4px;
  font-size: .73rem; color: var(--muted); margin: 0 0 .5rem;
}
.nc-tags { display: flex; gap: 5px; margin-bottom: .5rem; flex-wrap: wrap; }
.nc-tag {
  font-size: .67rem; padding: 2px 7px; border-radius: 10px; letter-spacing: .2px;
}
.nc-tag--cat { background: var(--accent-light); color: #92400E; border: 1px solid rgba(202,138,4,.2); }
.nc-tag--wc { background: #F3F0EB; color: var(--muted); border: 1px solid var(--border-light); }

.nc-desc {
  font-size: .73rem; color: #999; line-height: 1.58; margin: 0 0 .55rem;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.nc-meta {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: .5rem; border-top: 1px solid var(--border-light);
}
.nc-meta__item {
  display: flex; align-items: center; gap: 3px;
  font-size: .68rem; color: var(--subtle);
}

/* ==================== 骨架屏 ==================== */
.sk-grid { grid-template-columns: repeat(auto-fill, minmax(172px, 1fr)); gap: 1.25rem; }
.sk-card { background: var(--card); border: 1px solid var(--border-light); border-radius: var(--r-md); overflow: hidden; }
.sk-cover { width: 100%; aspect-ratio: 3/4; background: linear-gradient(90deg,#f0ede8 25%,#e8e5df 50%,#f0ede8 75%); background-size: 200% 100%; animation: sk-shimmer 1.5s infinite; }
.sk-bd { padding: .85rem .9rem; display: flex; flex-direction: column; gap: .5rem; }
.sk-ln { border-radius: 3px; background: linear-gradient(90deg,#f0ede8 25%,#e8e5df 50%,#f0ede8 75%); background-size: 200% 100%; animation: sk-shimmer 1.5s infinite; }
@keyframes sk-shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ==================== 空状态 ==================== */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 340px; background: var(--card); border: 1px solid var(--border-light);
  border-radius: var(--r-md); gap: .5rem;
}
.empty-title { font-size: .9rem; color: var(--muted); font-weight: 500; margin: 0; }
.empty-hint { font-size: .78rem; color: #BBB5AC; margin: 0; }

/* ==================== 分页 ==================== */
.pagination-bar { display: flex; justify-content: center; margin-top: 2rem; }
.pagination-bar :deep(.el-pagination) { gap: 4px; }
.pagination-bar :deep(.el-pager li) {
  border-radius: var(--r-sm); border: 1px solid var(--border-light);
  background: var(--card); color: var(--ink); font-size: .82rem;
  min-width: 32px; height: 32px; line-height: 30px; transition: var(--t);
}
.pagination-bar :deep(.el-pager li:hover) { border-color: var(--accent); color: var(--accent); }
.pagination-bar :deep(.el-pager li.is-active) { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 700; }
.pagination-bar :deep(.btn-prev), .pagination-bar :deep(.btn-next) {
  border-radius: var(--r-sm); border: 1px solid var(--border-light);
  background: var(--card); height: 32px; width: 32px; transition: var(--t);
}
.pagination-bar :deep(.btn-prev:hover), .pagination-bar :deep(.btn-next:hover) { border-color: var(--accent); color: var(--accent); }

/* ==================== 页脚 ==================== */
.site-footer {
  background: #1C1A17; padding: 2.5rem 1.5rem 1.8rem; margin-top: 3rem;
}
.footer-inner { max-width: 1280px; margin: 0 auto; text-align: center; }
.footer-brand { margin-bottom: 1.2rem; }
.footer-logo { font-family: var(--ff-serif); font-size: 1.2rem; font-weight: 700; color: #F5F0E8; letter-spacing: 2px; }
.footer-brand p { font-size: .78rem; color: #6B6560; margin: .35rem 0 0; letter-spacing: .3px; }
.footer-links { display: flex; justify-content: center; gap: 1.8rem; margin-bottom: 1.2rem; }
.footer-links a { font-size: .78rem; color: #6B6560; text-decoration: none; transition: color .15s; }
.footer-links a:hover { color: var(--accent); }
.copyright { font-size: .72rem; color: #4A4540; margin: 0; letter-spacing: .2px; }

/* ==================== 响应式 ==================== */

@media (max-width: 1100px) {
  .content-layout { flex-direction: column; }
  .sidebar { width: 100%; position: static; display: grid; grid-template-columns: repeat(2, 1fr); gap: .85rem; }
  .sb-rank { grid-column: span 2; }
}

@media (max-width: 768px) {
  .header-inner { padding: 0 1rem; gap: .8rem; height: 52px; }
  .main-nav { display: none; }
  .search-bar { width: 180px; }
  .page-head-inner, .main-content { padding-left: 1rem; padding-right: 1rem; }
  .page-title { font-size: 1.25rem; letter-spacing: 1.5px; }
  .sidebar { grid-template-columns: 1fr; }
  .sb-rank { grid-column: span 1; }
  .novel-grid, .sk-grid { grid-template-columns: repeat(3, 1fr); gap: .85rem; }
  .toolbar { flex-wrap: wrap; gap: .5rem; }
}

@media (max-width: 520px) {
  .novel-grid, .sk-grid { grid-template-columns: repeat(2, 1fr); gap: .7rem; }
  .search-bar { display: none; }
}
</style>
