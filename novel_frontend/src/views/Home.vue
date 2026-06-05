<template>
  <div class="home-page">

    <!-- ===== 顶部导航 ===== -->
    <header class="site-header" :class="{ 'header-scrolled': isScrolled }">
      <div class="header-inner">
        <router-link to="/" class="logo">
          <span class="logo-text">墨香书阁</span>
        </router-link>

        <nav class="main-nav">
          <router-link to="/" class="nav-link active">首页</router-link>
          <router-link to="/novels" class="nav-link">分类</router-link>
          <router-link to="/rankings" class="nav-link">排行榜</router-link>
          <a href="#" class="nav-link">征文活动</a>
          <router-link to="/author" class="nav-link">作家专区</router-link>
        </nav>

        <div class="header-actions">
          <div class="search-box" @click="focusSearch">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input ref="searchInput" v-model="searchKeyword" class="search-input"
                   placeholder="搜索书名或作者..." @keyup.enter="handleSearch" />
          </div>
          <template v-if="!isLoggedIn">
            <router-link to="/login" class="btn-login">登录</router-link>
          </template>
          <template v-else>
            <div class="user-dropdown" @mouseenter="showUserMenu = true" @mouseleave="showUserMenu = false">
              <img v-if="userAvatar" :src="userAvatar" alt="" class="user-avatar-sm" />
              <div v-else class="user-avatar-placeholder">{{ (displayName || '读').charAt(0) }}</div>
              <span class="user-name">{{ displayName }}</span>
              <Transition name="dropdown-fade">
                <div v-if="showUserMenu" class="user-menu-list">
                  <router-link to="/user" class="menu-item">个人中心</router-link>
                  <a href="#" class="menu-item" @click.prevent="handleLogout">退出登录</a>
                </div>
              </Transition>
            </div>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">

      <!-- ===== 1. 轮播Banner ===== -->
      <section class="banner-section" @mouseenter="pauseCarousel" @mouseleave="resumeCarousel">
        <div class="banner-container">
          <div class="banner-track">
            <div v-for="(item, idx) in homeData.banner || []" :key="'b-'+idx"
                 class="banner-slide" :class="{ active: idx === currentSlide }"
                 @click="goToDetail(item.id)">
              <img :src="item.cover || defaultCover" :alt="item.title" class="banner-img" loading="eager" decoding="async" @error="onImgError" />
              <div class="banner-overlay">
                <span class="banner-tag">{{ item.category || '精选' }}</span>
                <h2 class="banner-title">{{ item.title }}</h2>
                <p class="banner-desc">{{ item.description ? item.description.slice(0,60) + '...' : '' }}</p>
              </div>
            </div>
          </div>
          <button class="banner-arrow banner-arrow--prev" @click.stop="prevSlide">&#10094;</button>
          <button class="banner-arrow banner-arrow--next" @click.stop="nextSlide">&#10095;</button>
          <div class="banner-dots">
            <span v-for="(item, idx) in (homeData.banner || [])" :key="'d-'+idx"
                  class="dot" :class="{ active: idx === currentSlide }" @click="goToSlide(idx)"></span>
          </div>
        </div>
      </section>

      <!-- ===== 2. 作家专区 / 网站公告 两列 ===== -->
      <section class="info-bar-section">
        <div class="page-width">
          <div class="info-grid">
            <div class="info-card info-card--writer" @click="$router.push('/author')">
              <div class="info-card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/></svg>
              </div>
              <h4>作家专区</h4>
              <p>投稿发布新书 · 创作你的故事</p>
            </div>
            <div class="info-card info-card--notice">
              <div class="info-card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
              </div>
              <h4>网站公告</h4>
              <p>{{ publicAnnouncements.length > 0 ? publicAnnouncements[0].title : '暂无公告' }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 3. 四大榜单 ===== -->
      <section class="rank-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>排行榜</h2>
          </div>
          <div class="rank-grid">
            <!-- 女生大热榜 -->
            <div class="rank-col">
              <div class="rank-header rank-header--pink">
                <span class="rank-label">大热榜 · 女生</span>
                <span class="rank-more">&gt;</span>
              </div>
              <ul class="rank-list">
                <li v-for="(book, i) in (homeData.rankings?.hot_female || []).slice(0,10)" :key="book.id"
                    class="rank-item" @click="goToDetail(book.id)">
                  <span class="rank-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="rank-cover" @error="onImgError" />
                  <div class="rank-info">
                    <h5 class="rank-book-title">{{ book.title }}</h5>
                    <p class="rank-book-author">{{ book.author }}</p>
                  </div>
                  <span class="rank-hot">{{ formatCount(book.view_count) }}热度</span>
                </li>
                <li v-if="!homeData.rankings?.hot_female?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
            <!-- 男生大热榜 -->
            <div class="rank-col">
              <div class="rank-header rank-header--blue">
                <span class="rank-label">大热榜 · 男生</span>
                <span class="rank-more">&gt;</span>
              </div>
              <ul class="rank-list">
                <li v-for="(book, i) in (homeData.rankings?.hot_male || []).slice(0,10)" :key="book.id"
                    class="rank-item" @click="goToDetail(book.id)">
                  <span class="rank-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="rank-cover" @error="onImgError" />
                  <div class="rank-info">
                    <h5 class="rank-book-title">{{ book.title }}</h5>
                    <p class="rank-book-author">{{ book.author }}</p>
                  </div>
                  <span class="rank-hot">{{ formatCount(book.view_count) }}热度</span>
                </li>
                <li v-if="!homeData.rankings?.hot_male?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
            <!-- 女生新书榜 -->
            <div class="rank-col">
              <div class="rank-header rank-header--orange">
                <span class="rank-label">新书榜 · 女生</span>
                <span class="rank-more">&gt;</span>
              </div>
              <ul class="rank-list">
                <li v-for="(book, i) in (homeData.rankings?.new_female || []).slice(0,10)" :key="book.id"
                    class="rank-item" @click="goToDetail(book.id)">
                  <span class="rank-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="rank-cover" @error="onImgError" />
                  <div class="rank-info">
                    <h5 class="rank-book-title">{{ book.title }}</h5>
                    <p class="rank-book-author">{{ book.author }}</p>
                  </div>
                  <span class="rank-hot">新书上架</span>
                </li>
                <li v-if="!homeData.rankings?.new_female?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
            <!-- 男生新书榜 -->
            <div class="rank-col">
              <div class="rank-header rank-header--green">
                <span class="rank-label">新书榜 · 男生</span>
                <span class="rank-more">&gt;</span>
              </div>
              <ul class="rank-list">
                <li v-for="(book, i) in (homeData.rankings?.new_male || []).slice(0,10)" :key="book.id"
                    class="rank-item" @click="goToDetail(book.id)">
                  <span class="rank-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="rank-cover" @error="onImgError" />
                  <div class="rank-info">
                    <h5 class="rank-book-title">{{ book.title }}</h5>
                    <p class="rank-book-author">{{ book.author }}</p>
                  </div>
                  <span class="rank-hot">新书上架</span>
                </li>
                <li v-if="!homeData.rankings?.new_male?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 4. 男女频专题区 ===== -->
      <section v-if="(homeData.topics?.female?.length || homeData.topics?.male?.length)" class="topic-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>专题推荐</h2>
          </div>
          <!-- 女频专题 -->
          <div v-if="homeData.topics?.female?.length" class="topic-block">
            <h3 class="topic-subtitle topic-subtitle--pink">「 新信意·快节奏·长线战·好笔力·女频创新大征文 」</h3>
            <div class="scroll-row">
              <button class="scroll-btn scroll-btn--left" @click="scrollLeft('femaleTopic')">&#10094;</button>
              <div ref="femaleTopic" class="scroll-track">
                <div v-for="book in (homeData.topics?.female || [])" :key="book.id" class="topic-card" @click="goToDetail(book.id)">
                  <img :src="book.cover || defaultCover" class="topic-cover" @error="onImgError" />
                  <h4 class="topic-name">{{ book.title }}</h4>
                  <p class="topic-author">{{ book.author }}</p>
                </div>
              </div>
              <button class="scroll-btn scroll-btn--right" @click="scrollRight('femaleTopic')">&#10095;</button>
            </div>
          </div>
          <!-- 男频专题 -->
          <div v-if="homeData.topics?.male?.length" class="topic-block">
            <h3 class="topic-subtitle topic-subtitle--blue">「 热血玄幻·快节奏爽文·男频精品 」</h3>
            <div class="scroll-row">
              <button class="scroll-btn scroll-btn--left" @click="scrollLeft('maleTopic')">&#10094;</button>
              <div ref="maleTopic" class="scroll-track">
                <div v-for="book in (homeData.topics?.male || [])" :key="book.id" class="topic-card" @click="goToDetail(book.id)">
                  <img :src="book.cover || defaultCover" class="topic-cover" @error="onImgError" />
                  <h4 class="topic-name">{{ book.title }}</h4>
                  <p class="topic-author">{{ book.author }}</p>
                </div>
              </div>
              <button class="scroll-btn scroll-btn--right" @click="scrollRight('maleTopic')">&#10095;</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 5. 影视改编专区 ===== -->
      <section v-if="homeData.adapted?.length" class="adapted-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>改编出版</h2>
          </div>
          <div class="scroll-row">
            <button class="scroll-btn scroll-btn--left" @click="scrollLeft('adaptedTrack')">&#10094;</button>
            <div ref="adaptedTrack" class="scroll-track">
              <div v-for="book in (homeData.adapted || [])" :key="book.id" class="adapted-card" @click="goToDetail(book.id)">
                <img :src="book.cover || defaultCover" class="adapted-cover" @error="onImgError" />
                <div class="adapted-info">
                  <h4 class="adapted-title">{{ book.title }}</h4>
                  <p class="adapted-author">{{ book.author }}</p>
                  <span class="adapted-tag">影视改编</span>
                </div>
              </div>
            </div>
            <button class="scroll-btn scroll-btn--right" @click="scrollRight('adaptedTrack')">&#10095;</button>
          </div>
        </div>
      </section>

      <!-- ===== 6. 总编推荐 ===== -->
      <section v-if="homeData.recommended?.length" class="editor-pick-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>总编推荐</h2>
          </div>
          <div class="editor-grid">
            <div v-for="book in (homeData.recommended || [])" :key="book.id" class="editor-card" @click="goToDetail(book.id)">
              <img :src="book.cover || defaultCover" class="editor-cover" @error="onImgError" />
              <div class="editor-body">
                <h4 class="editor-title">{{ book.title }}</h4>
                <div class="editor-meta">
                  <span class="meta-tag">{{ book.status === 1 ? '已完结' : '连载中' }}</span>
                  <span class="meta-word">{{ formatWordCount(book.word_count) }}</span>
                </div>
                <p class="editor-comment">{{ book.recommend_comment || '总编力荐佳作，值得一读' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 7. 四大分类快捷栏 ===== -->
      <section class="quick-cat-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>热门分类</h2>
          </div>
          <div class="quick-cat-grid">
            <div v-for="(catName, catKey) in quickCatNames" :key="catKey" class="quick-cat-block">
              <h3 class="quick-cat-title" @click="goToCategory(catKey)">{{ catName }} &gt;</h3>
              <div class="quick-cat-books">
                <div v-for="book in (homeData.quick_categories?.[catKey] || [])" :key="book.id"
                     class="quick-mini-card" @click="goToDetail(book.id)">
                  <img :src="book.cover || defaultCover" class="quick-cover" @error="onImgError" />
                  <div class="quick-info">
                    <h5 class="quick-book-title">{{ book.title }}</h5>
                    <p class="quick-book-author">{{ book.author }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 8. 签约新书 ===== -->
      <section class="signed-new-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>签约新书</h2>
            <router-link to="/novels" class="see-all-link">更多 &gt;</router-link>
          </div>
          <div class="signed-grid">
            <div v-for="book in (homeData.signed_new || []).slice(0, 12)" :key="book.id" class="signed-card" @click="goToDetail(book.id)">
              <img :src="book.cover || defaultCover" class="signed-cover" @error="onImgError" />
              <h4 class="signed-title">{{ book.title }}</h4>
              <p class="signed-author">{{ book.author }}</p>
              <span class="signed-cat">{{ book.category }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 9. 最近更新表格 ===== -->
      <section class="recent-update-section">
        <div class="page-width">
          <div class="section-head">
            <h2 class="section-title"><span class="title-deco"></span>最近更新</h2>
            <router-link to="/novels?ordering=-updated_at" class="see-all-link">更多 &gt;</router-link>
          </div>
          <div class="update-table-wrap">
            <table class="update-table">
              <thead>
                <tr><th width="80">分类</th><th>书名</th><th>最新章节</th><th width="120">作者</th><th width="140">更新时间</th></tr>
              </thead>
              <tbody>
                <tr v-for="book in (homeData.recent_updated || []).slice(0,15)" :key="book.id" @click="goToDetail(book.id)">
                  <td><span class="td-cat">{{ book.category }}</span></td>
                  <td class="td-title">{{ book.title }}</td>
                  <td class="td-chapter">{{ book.latest_chapter || '-' }}</td>
                  <td>{{ book.author }}</td>
                  <td class="td-time">{{ formatTime(book.updated_at) }}</td>
                </tr>
                <tr v-if="!homeData.recent_updated?.length"><td colspan="5" class="empty-row">暂无更新数据</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ===== 10. 完结榜单 ===== -->
      <section class="finished-section">
        <div class="page-width">
          <div class="finish-cols">
            <!-- 女生完结 -->
            <div class="finish-col">
              <div class="finish-header finish-header--pink">
                <span>完结榜 · 女生</span>
              </div>
              <ul class="finish-list">
                <li v-for="(book, i) in (homeData.finished?.female || []).slice(0,10)" :key="book.id"
                    class="finish-item" @click="goToDetail(book.id)">
                  <span class="finish-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="finish-cover" @error="onImgError" />
                  <div class="finish-info">
                    <h5>{{ book.title }}</h5>
                    <p>{{ book.author }}</p>
                  </div>
                </li>
                <li v-if="!homeData.finished?.female?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
            <!-- 男生完结 -->
            <div class="finish-col">
              <div class="finish-header finish-header--blue">
                <span>完结榜 · 男生</span>
              </div>
              <ul class="finish-list">
                <li v-for="(book, i) in (homeData.finished?.male || []).slice(0,10)" :key="book.id"
                    class="finish-item" @click="goToDetail(book.id)">
                  <span class="finish-num" :class="{ top3: i < 3 }">{{ i + 1 }}</span>
                  <img :src="book.cover || defaultCover" class="finish-cover" @error="onImgError" />
                  <div class="finish-info">
                    <h5>{{ book.title }}</h5>
                    <p>{{ book.author }}</p>
                  </div>
                </li>
                <li v-if="!homeData.finished?.male?.length" class="rank-empty">暂无数据</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

    </main>

    <!-- ===== 页脚 ===== -->
    <footer class="site-footer">
      <div class="footer-top">
        <div class="page-width footer-flex">
          <div class="footer-brand">
            <h3>墨香书阁</h3>
            <p>为阅读而生，为故事而活</p>
          </div>
          <div class="footer-links-group">
            <div class="fl-col">
              <h4>关于我们</h4>
              <a href="#">网站简介</a>
              <a href="#">联系我们</a>
              <a href="#">投稿须知</a>
            </div>
            <div class="fl-col">
              <h4>帮助中心</h4>
              <a href="#">用户协议</a>
              <a href="#">隐私政策</a>
              <a href="#">版权声明</a>
            </div>
            <div class="fl-col">
              <h4>友情链接</h4>
              <a href="#">作家专区</a>
              <a href="#">关于我们</a>
              <a href="#">征文活动</a>
            </div>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 墨香书阁 All Rights Reserved</p>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { novelApi } from '../api'
import request from '../utils/request'

const router = useRouter()

// ── 状态 ──
const homeData = reactive<Record<string, any>>({})
const publicAnnouncements = ref<any[]>([])
const isScrolled = ref(false)
const searchKeyword = ref('')
const searchInput = ref<HTMLInputElement>()
const showUserMenu = ref(false)
const userAvatar = ref('')

// ── 轮播 ──
const currentSlide = ref(0)
let carouselTimer: ReturnType<typeof setInterval> | null = null
let carouselPaused = ref(false)

const defaultCover = 'https://via.placeholder.com/140x190/e8dcc8/8B6914?text=Book'

const quickCatNames: Record<string, string> = {
  '穿越': '穿越',
  '玄幻': '玄幻',
  '都市': '都市',
  '武侠': '武侠',
}

const isLoggedIn = computed(() => !!localStorage.getItem('user'))
const displayName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    const name = u.real_name || u.pen_name || u.nickname || u.username || '读者'
    return name && typeof name === 'string' ? name : '读者'
  } catch { return '读者' }
})

// ── 方法 ──
const formatCount = (num?: number | string) => {
  const n = Number(num) || 0
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return String(n)
}

const formatWordCount = (num?: number | string) => {
  const n = Number(num) || 0
  if (n >= 10000) return (n / 10000).toFixed(1) + '万字'
  return n + '字'
}

const formatTime = (time?: string) => {
  if (!time) return '-'
  const d = new Date(time)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const goToDetail = (id?: number | string) => { if (id != null) router.push({ name: 'NovelDetail', params: { id } }) }
const goToCategory = (category: string) => router.push({ name: 'NovelList', query: { category } })

const handleSearch = () => {
  if (searchKeyword.value.trim())
    router.push({ name: 'Search', query: { q: searchKeyword.value.trim() } })
}
const focusSearch = () => searchInput.value?.focus()
const handleLogout = () => {
  localStorage.removeItem('user')
  window.location.reload()
}

const onImgError = (e: Event) => {
  (e.target as HTMLImageElement).src = defaultCover
}

// ── 轮播控制 ──
const startAutoPlay = () => {
  stopAutoPlay()
  carouselTimer = setInterval(() => {
    if (!carouselPaused.value && (homeData.banner?.length || 0) > 1) {
      currentSlide.value = (currentSlide.value + 1) % (homeData.banner?.length || 1)
    }
  }, 4000)
}
const stopAutoPlay = () => { if (carouselTimer) { clearInterval(carouselTimer); carouselTimer = null } }
const nextSlide = () => {
  const len = homeData.banner?.length || 0
  if (len <= 1) return
  currentSlide.value = (currentSlide.value + 1) % len
}
const prevSlide = () => {
  const len = homeData.banner?.length || 0
  if (len <= 1) return
  currentSlide.value = (currentSlide.value - 1 + len) % len
}
const goToSlide = (i: number) => { currentSlide.value = i }
const pauseCarousel = () => { carouselPaused.value = true }
const resumeCarousel = () => { carouselPaused.value = false }

// 横向滚动控制
const femaleTopic = ref<HTMLElement>()
const maleTopic = ref<HTMLElement>()
const adaptedTrack = ref<HTMLElement>()

const scrollLeft = (refName: 'femaleTopic' | 'maleTopic' | 'adaptedTrack') => {
  const el = refName === 'femaleTopic' ? femaleTopic.value : refName === 'maleTopic' ? maleTopic.value : adaptedTrack.value
  if (el) el.scrollBy({ left: -320, behavior: 'smooth' })
}
const scrollRight = (refName: 'femaleTopic' | 'maleTopic' | 'adaptedTrack') => {
  const el = refName === 'femaleTopic' ? femaleTopic.value : refName === 'maleTopic' ? maleTopic.value : adaptedTrack.value
  if (el) el.scrollBy({ left: 320, behavior: 'smooth' })
}

// ── 数据加载 ──
const SAFE_DEFAULTS = {
  banner: [],
  rankings: { hot_female: [], hot_male: [], new_female: [], new_male: [] },
  topics: { female: [], male: [] },
  adapted: [],
  recommended: [],
  quick_categories: {},
  signed_new: [],
  recent_updated: [],
  finished: { female: [], male: [] },
}

const loadHomeData = async () => {
  try {
    const res = await novelApi.homeData()
    const data = res && typeof res === 'object' ? res : {}
    // 合并安全默认值，确保每个字段至少是空数组/对象，不会触发 map 崩溃
    Object.keys(SAFE_DEFAULTS).forEach(key => {
      if (data[key] === null || data[key] === undefined) {
        homeData[key] = SAFE_DEFAULTS[key]
      } else if (typeof SAFE_DEFAULTS[key] === 'object' && !Array.isArray(SAFE_DEFAULTS[key])) {
        homeData[key] = { ...SAFE_DEFAULTS[key], ...data[key] }
      } else {
        homeData[key] = Array.isArray(data[key]) ? data[key] : SAFE_DEFAULTS[key]
      }
    })
  } catch (e) {
    console.error('[Home] 首页数据加载失败:', e)
    // 接口异常时使用全部空数据兜底，页面正常渲染但各板块显示空白
    Object.assign(homeData, SAFE_DEFAULTS)
  }
}

const fetchAnnouncements = async () => {
  try {
    const res = await request.get('/public/announcements/')
    const list: any[] = Array.isArray(res) ? res : res.results || []
    publicAnnouncements.value = list.filter((a: any) => a.is_active).sort((a: any, b: any) => {
      if (a.is_pinned && !b.is_pinned) return -1
      if (!a.is_pinned && b.is_pinned) return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  } catch {}
}

// ── 生命周期 ──
onMounted(async () => {
  await loadHomeData()
  startAutoPlay()
  fetchAnnouncements()
  window.addEventListener('scroll', handleScroll)
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    userAvatar.value = user.avatar || ''
  } catch {}
})

onUnmounted(() => {
  stopAutoPlay()
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => { isScrolled.value = window.scrollY > 40 }
</script>

<style scoped>
/* ═══════════════ 全局变量 ═══════════════ */
:root {
  --primary: #C0392B;
  --primary-light: #E74C3C;
  --pink: #E91E63;
  --blue: #1976D2;
  --orange: #FF9800;
  --green: #4CAF50;
  --bg: #F5F5F5;
  --white: #FFFFFF;
  --text-dark: #212121;
  --text-gray: #757575;
  --text-light: #999;
  --border: #E8E8E8;
  --shadow: 0 2px 12px rgba(0,0,0,.08);
  --radius: 8px;
}

.home-page { min-height: 100vh; background: var(--bg); font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; color: var(--text-dark); }

.page-width { max-width: 1200px; margin: 0 auto; padding: 0 16px; }

/* ═══ 导航 ═══ */
.site-header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: var(--white); border-bottom: 1px solid var(--border);
  transition: box-shadow .25s;
}
.header-scrolled { box-shadow: 0 2px 12px rgba(0,0,0,.08); }
.header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; height: 56px; display: flex; align-items: center; gap: 28px; }

.logo { text-decoration: none; }
.logo-text { font-size: 20px; font-weight: 800; color: var(--primary); letter-spacing: 2px; }

.main-nav { display: flex; gap: 24px; }
.nav-link { font-size: 14px; color: var(--text-gray); text-decoration: none; padding: 4px 0; position: relative; transition: color .2s; white-space: nowrap; }
.nav-link:hover, .nav-link.active { color: var(--primary); font-weight: 600; }
.nav-link.active::after { content:''; position:absolute; bottom:-17px; left:0; right:0; height:2px; background:var(--primary); }

.header-actions { display:flex; align-items:center; gap:12px; margin-left:auto; }
.search-box { position:relative; }
.search-box input { width:200px; height:34px; padding:0 12px 0 34px; border:1px solid var(--border); border-radius:18px; font-size:13px; outline:none; background:#FAFAFA; transition:.2s; }
.search-box input:focus { border-color:var(--primary); background:#fff; }
.search-icon { position:absolute; left:10px; top:50%; transform:translateY(-50%); width:16px; height:16px; color:var(--text-light); pointer-events:none; }

.btn-login { padding:5px 18px; font-size:13px; color:#fff; background:var(--primary); border-radius:18px; text-decoration:none; font-weight:500; }
.btn-login:hover { opacity:.9; }

.user-dropdown { position:relative; display:flex; align-items:center; gap:6px; cursor:pointer; padding:4px 8px; border-radius:20px; }
.user-dropdown:hover { background:#f5f5f5; }
.user-avatar-sm { width:28px; height:28px; border-radius:50%; object-fit:cover; }
.user-avatar-placeholder { width:28px; height:28px; border-radius:50%; background:var(--primary); color:#fff; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:600; }
.user-name { font-size:13px; color:var(--text-dark); max-width:70px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.user-menu-list { position:absolute; top:100%; right:0; min-width:130px; background:#fff; border:1px solid var(--border); border-radius:8px; box-shadow:var(--shadow); z-index:101; padding:4px 0; }
.menu-item { display:block; padding:8px 16px; font-size:13px; color:var(--text-dark); text-decoration:none; }
.menu-item:hover { background:#f5f5f5; }
.dropdown-fade-enter-active, .dropdown-fade-leave-active { transition:opacity .15s; }
.dropdown-fade-enter-from, .dropdown-fade-leave-to { opacity:0; }

.main-content { padding-top: 56px; }

/* ═══ 1. 轮播Banner ═══ */
.banner-section { padding: 16px 0 0; }
.banner-container { max-width:1200px; margin:0 auto; padding:0 16px; position:relative; height:420px; border-radius:12px; overflow:hidden; background:#1a1a2e; }
.banner-track { position:relative; width:100%; height:100%; }
.banner-slide { position:absolute; inset:0; opacity:0; transition:opacity .6s ease; cursor:pointer; }
.banner-slide.active { opacity:1; }
.banner-img { width:100%; height:100%; object-fit:cover; object-position:center top; image-rendering:-webkit-optimize-contrast; image-rendering:crisp-edges; }
.banner-overlay { position:absolute; left:0; bottom:0; right:0; padding:20px 24px 16px; background:linear-gradient(transparent, rgba(0,0,0,.78)); display:flex; flex-direction:column; gap:4px; }
.banner-tag { display:inline-flex; align-self:flex-start; padding:2px 10px; font-size:11px; font-weight:600; color:#fff; background:rgba(192,57,43,.85); border-radius:10px; letter-spacing:1px; }
.banner-title { font-size:18px; font-weight:700; color:#fff; margin:0; line-height:1.3; }
.banner-desc { font-size:12px; color:rgba(255,255,255,.75); margin:0; display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }
.banner-arrow { position:absolute; top:50%; transform:translateY(-50%); width:36px; height:36px; border:none; border-radius:50%; background:rgba(0,0,0,.35); color:#fff; cursor:pointer; font-size:16px; display:flex; align-items:center; justify-content:center; opacity:0; transition:all .25s; z-index:5; backdrop-filter:blur(4px); }
.banner-container:hover .banner-arrow { opacity:1; }
.banner-arrow:hover { background:var(--primary); }
.banner-arrow--prev { left:12px; }
.banner-arrow--next { right:12px; }
.banner-dots { position:absolute; bottom:12px; right:16px; z-index:5; display:flex; gap:6px; }
.dot { width:8px; height:8px; border-radius:50%; border:none; background:rgba(255,255,255,.35); cursor:pointer; padding:0; transition:all .3s; }
.dot.active { background:var(--primary); width:22px; border-radius:4px; }

/* ═══ 2. 信息三栏 ═══ */
.info-bar-section { padding: 16px 0; }
.info-grid { display:grid; grid-template-columns: repeat(2,1fr); gap: 16px; }
.info-card { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); padding:20px; display:flex; flex-direction:column; align-items:center; gap:8px; cursor:pointer; transition:box-shadow .2s; }
.info-card:hover { box-shadow:var(--shadow); }
.info-card-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#fff; }
.info-card--writer .info-card-icon { background:linear-gradient(135deg,#E91E63,#F06292); }
.info-card--policy .info-card-icon { background:linear-gradient(135deg,#1976D2,#64B5F6); }
.info-card--notice .info-card-icon { background:linear-gradient(135deg,#FF9800,#FFB74D); }
.info-card-icon svg { width:22px; height:22px; }
.info-card h4 { font-size:15px; font-weight:600; margin:0; }
.info-card p { font-size:12px; color:var(--text-gray); margin:0; text-align:center; }

/* ═══ Section通用 ═══ */
.section-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; padding-top:24px; }
.section-title { font-size:18px; font-weight:700; margin:0; display:flex; align-items:center; gap:8px; }
.title-deco { width:4px; height:18px; background:var(--primary); border-radius:2px; display:inline-block; }
.see-all-link { font-size:13px; color:var(--text-light); text-decoration:none; }
.see-all-link:hover { color:var(--primary); }

/* ═══ 3. 四大榜单 ═══ */
.rank-section { padding: 0 0 8px; }
.rank-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
.rank-col { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; }
.rank-header { padding:10px 14px; font-size:14px; font-weight:600; color:#fff; display:flex; justify-content:space-between; align-items:center; }
.rank-header--pink { background:linear-gradient(135deg,#E91E63,#F48FB1); }
.rank-header--blue { background:linear-gradient(135deg,#1976D2,#90CAF9); }
.rank-header--orange { background:linear-gradient(135deg,#FF9800,#FFCC80); }
.rank-header--green { background:linear-gradient(135deg,#4CAF50,#A5D6A7); }
.rank-more { font-size:16px; opacity:.7; }
.rank-list { list-style:none; margin:0; padding:0; }
.rank-item { display:flex; align-items:center; gap:8px; padding:8px 12px; border-bottom:1px solid #f5f5f5; cursor:pointer; transition:background .15s; }
.rank-item:last-child { border-bottom:none; }
.rank-item:hover { background:#fafafa; }
.rank-num { width:20px; text-align:center; font-size:14px; font-weight:700; color:var(--text-light); flex-shrink:0; }
.rank-num.top3 { color:var(--primary); }
.rank-cover { width:36px; height:48px; object-fit:cover; border-radius:4px; flex-shrink:0; }
.rank-info { flex:1; min-width:0; }
.rank-book-title { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rank-book-author { font-size:11px; color:var(--text-light); margin:2px 0 0; }
.rank-hot { font-size:11px; color:var(--primary); white-space:nowrap; flex-shrink:0; }
.rank-empty { padding:30px; text-align:center; font-size:13px; color:var(--text-light); }

/* ═══ 4. 专题区 ═══ */
.topic-section { padding: 0 0 8px; }
.topic-block { margin-bottom:16px; }
.topic-subtitle { font-size:14px; font-weight:600; margin:0 0 10px; padding-left:4px; }
.topic-subtitle--pink { color:var(--pink); }
.topic-subtitle--blue { color:var(--blue); }
.scroll-row { position:relative; display:flex; align-items:center; gap:4px; }
.scroll-track { display:flex; gap:12px; overflow-x:auto; scroll-behavior:smooth; padding:4px 0; scrollbar-width:none; }
.scroll-track::-webkit-scrollbar { display:none; }
.scroll-btn { width:32px; height:72px; border:none; border-radius:6px; background:rgba(255,255,255,.9); color:var(--text-dark); cursor:pointer; font-size:16px; flex-shrink:0; box-shadow:0 1px 6px rgba(0,0,0,.1); transition:background .2s; z-index:2; }
.scroll-btn:hover { background:#fff; color:var(--primary); }
.topic-card { flex-shrink:0; width:110px; cursor:pointer; }
.topic-cover { width:110px; height:150px; object-fit:cover; border-radius:6px; margin-bottom:6px; transition:transform .2s; }
.topic-card:hover .topic-cover { transform:scale(1.04); }
.topic-name { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.topic-author { font-size:11px; color:var(--text-light); margin:2px 0 0; }

/* ═══ 5. 影视改编 ═══ */
.adapted-section { padding: 0 0 8px; }
.adapted-card { flex-shrink:0; width:160px; cursor:pointer; }
.adapted-cover { width:160px; height:100px; object-fit:cover; border-radius:6px; margin-bottom:6px; }
.adapted-info { padding:0 2px; }
.adapted-title { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.adapted-author { font-size:11px; color:var(--text-light); margin:2px 0; }
.adapted-tag { display:inline-block; padding:1px 8px; font-size:10px; color:var(--orange); background:#FFF3E0; border-radius:10px; }

/* ═══ 6. 总编推荐 ═══ */
.editor-pick-section { padding: 0 0 8px; }
.editor-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
.editor-card { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; cursor:pointer; transition:box-shadow .2s; display:flex; gap:14px; padding:14px; }
.editor-card:hover { box-shadow:var(--shadow); }
.editor-cover { width:90px; height:120px; object-fit:cover; border-radius:6px; flex-shrink:0; }
.editor-body { flex:1; min-width:0; display:flex; flex-direction:column; justify-content:center; }
.editor-title { font-size:15px; font-weight:600; margin:0 0 6px; }
.editor-meta { display:flex; gap:8px; margin-bottom:8px; }
.meta-tag { font-size:11px; color:#fff; background:var(--green); padding:1px 8px; border-radius:10px; }
.meta-word { font-size:11px; color:var(--text-light); }
.editor-comment { font-size:12px; color:var(--text-gray); line-height:1.6; margin:0; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }

/* ═══ 7. 四大分类快捷栏 ═══ */
.quick-cat-section { padding: 0 0 8px; }
.quick-cat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.quick-cat-block { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; }
.quick-cat-title { font-size:14px; font-weight:600; padding:10px 14px; margin:0; border-bottom:1px solid #f5f5f5; cursor:pointer; color:var(--primary); transition:background .15s; }
.quick-cat-title:hover { background:#fef5f5; }
.quick-cat-books { padding:8px; }
.quick-mini-card { display:flex; gap:8px; padding:6px 0; border-bottom:1px solid #fafafa; cursor:pointer; }
.quick-mini-card:last-child { border-bottom:none; }
.quick-mini-card:hover .quick-book-title { color:var(--primary); }
.quick-cover { width:40px; height:54px; object-fit:cover; border-radius:4px; flex-shrink:0; }
.quick-info { flex:1; min-width:0; }
.quick-book-title { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.quick-book-author { font-size:11px; color:var(--text-light); margin:2px 0 0; }

/* ═══ 8. 签约新书 ═══ */
.signed-new-section { padding: 0 0 8px; }
.signed-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:12px; }
.signed-card { cursor:pointer; }
.signed-cover { width:100%; aspect-ratio:3/4; object-fit:cover; border-radius:6px; margin-bottom:6px; transition:transform .2s; }
.signed-card:hover .signed-cover { transform:scale(1.05); }
.signed-title { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.signed-author { font-size:11px; color:var(--text-light); margin:2px 0; }
.signed-cat { font-size:10px; color:var(--text-light); background:#f5f5f5; padding:1px 8px; border-radius:10px; }

/* ═══ 9. 最近更新表格 ═══ */
.recent-update-section { padding: 0 0 8px; }
.update-table-wrap { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; }
.update-table { width:100%; border-collapse:collapse; }
.update-table th { background:#FAFAFA; padding:10px 14px; font-size:12px; font-weight:600; color:var(--text-gray); text-align:left; border-bottom:1px solid var(--border); }
.update-table td { padding:9px 14px; font-size:13px; border-bottom:1px solid #f9f9f9; }
.update-table tbody tr { cursor:pointer; transition:background .15s; }
.update-table tbody tr:hover { background:#fafafa; }
.td-cat { font-size:11px; }
.td-cat span { padding:2px 8px; background:#FCE4EC; color:var(--pink); border-radius:10px; font-size:11px; }
.td-title { font-weight:500; color:var(--text-dark); }
.td-chapter { color:var(--text-gray); font-size:12px; }
.td-time { color:var(--text-light); font-size:12px; }
.empty-row { text-align:center; color:var(--text-light); padding:30px !important; }

/* ═══ 10. 完结榜单 ═══ */
.finished-section { padding: 0 0 24px; }
.finish-cols { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.finish-col { background:var(--white); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden; }
.finish-header { padding:10px 14px; font-size:14px; font-weight:600; color:#fff; }
.finish-header--pink { background:linear-gradient(135deg,#E91E63,#F48FB1); }
.finish-header--blue { background:linear-gradient(135deg,#1976D2,#90CAF9); }
.finish-list { list-style:none; margin:0; padding:0; }
.finish-item { display:flex; align-items:center; gap:10px; padding:8px 12px; border-bottom:1px solid #f5f5f5; cursor:pointer; transition:background .15s; }
.finish-item:last-child { border-bottom:none; }
.finish-item:hover { background:#fafafa; }
.finish-num { width:20px; text-align:center; font-size:14px; font-weight:700; color:var(--text-light); flex-shrink:0; }
.finish-num.top3 { color:var(--primary); }
.finish-cover { width:38px; height:50px; object-fit:cover; border-radius:4px; flex-shrink:0; }
.finish-info { flex:1; min-width:0; }
.finish-info h5 { font-size:13px; font-weight:500; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.finish-info p { font-size:11px; color:var(--text-light); margin:2px 0 0; }

/* ═══ 页脚 ═══ */
.site-footer { background:#1A1A1A; color:#aaa; margin-top:0; }
.footer-top { padding:32px 0 24px; }
.footer-flex { display:flex; justify-content:space-between; gap:40px; }
.footer-brand h3 { font-size:20px; color:#eee; margin:0 0 8px; }
.footer-brand p { font-size:13px; color:#777; margin:0; }
.footer-links-group { display:flex; gap:48px; }
.fl-col h4 { font-size:13px; color:#ddd; margin:0 0 12px; font-weight:600; }
.fl-col a { display:block; font-size:12px; color:#888; text-decoration:none; margin-bottom:8px; }
.fl-col a:hover { color:#fff; }
.footer-bottom { border-top:1px solid #2a2a2a; padding:14px 0; text-align:center; }
.footer-bottom p { font-size:12px; color:#666; margin:0; }

/* ═══ 响应式 ═══ */
@media (max-width:1024px) {
  .rank-grid { grid-template-columns:1fr 1fr; }
  .finish-cols { grid-template-columns:1fr; }
  .signed-grid { grid-template-columns:repeat(4,1fr); }
  .quick-cat-grid { grid-template-columns:1fr 1fr; }
  .editor-grid { grid-template-columns:1fr; }
  .main-nav { gap:14px; }
  .nav-link { font-size:13px; }
}
@media (max-width:768px) {
  .main-nav { display:none; }
  .info-grid { grid-template-columns:1fr; }
  .rank-grid { grid-template-columns:1fr; }
  .signed-grid { grid-template-columns:repeat(3,1fr); }
  .quick-cat-grid { grid-template-columns:1fr; }
  .footer-flex { flex-direction:column; gap:24px; }
  .footer-links-group { flex-wrap:wrap; gap:24px; }
  .search-box input { width:140px; }
  .banner-container { height:240px; }
  .user-name { display:none; }
}
@media (max-width:480px) {
  .signed-grid { grid-template-columns:repeat(2,1fr); }
  .banner-container { height:180px; }
  .banner-title { font-size:15px; }
}
</style>
