<template>
  <div class="reader" :class="themeClass">
    <header class="reader-header" :class="{ 'header-hidden': !showFooter }">
      <div class="header-left">
        <button class="icon-btn" @click="goBack" title="返回">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
        </button>
        <nav class="breadcrumb">
          <router-link to="/" class="breadcrumb-link">首页</router-link>
          <span class="breadcrumb-sep">/</span>
          <router-link :to="{ path: '/novels', query: { category: novel?.category } }" class="breadcrumb-link">{{ novel?.category || '小说' }}</router-link>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-current">{{ chapter?.title || '章节' }}</span>
        </nav>
      </div>
      <div class="header-right">
        <div class="dropdown-wrap">
          <button class="icon-btn" title="主题" @click.stop="toggleThemeMenu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          </button>
          <div v-if="showThemeMenu" class="dropdown-menu">
            <button class="dropdown-item" :class="{ active: theme === 'light' }" @click="handleThemeChange('light')">明亮</button>
            <button class="dropdown-item" :class="{ active: theme === 'sepia' }" @click="handleThemeChange('sepia')">护眼</button>
            <button class="dropdown-item" :class="{ active: theme === 'dark' }" @click="handleThemeChange('dark')">夜间</button>
          </div>
        </div>
        <div class="dropdown-wrap">
          <button class="icon-btn" title="字号" @click.stop="toggleFontMenu">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 7 4 4 20 4 20 7"/><line x1="9" y1="20" x2="15" y2="20"/><line x1="12" y1="4" x2="12" y2="20"/></svg>
          </button>
          <div v-if="showFontMenu" class="dropdown-menu">
            <button class="dropdown-item" :class="{ active: fontSize === 'small' }" @click="handleFontSizeChange('small')">小</button>
            <button class="dropdown-item" :class="{ active: fontSize === 'medium' }" @click="handleFontSizeChange('medium')">中</button>
            <button class="dropdown-item" :class="{ active: fontSize === 'large' }" @click="handleFontSizeChange('large')">大</button>
          </div>
        </div>
        <button class="icon-btn" title="目录" @click="showDrawer = true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        </button>
        <button class="icon-btn" :class="{ 'icon-btn-active': isBookmarked }" title="书签" @click="toggleBookmark">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
        </button>
      </div>
    </header>

    <div class="progress-bar" :class="{ 'bar-hidden': !showFooter }">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: readingProgress + '%' }"></div>
      </div>
      <span class="progress-text">{{ readingProgress }}%</span>
    </div>

    <main class="reader-content" @click="toggleHeader">
      <div v-if="chapterLoading" class="skeleton-wrap">
        <div class="skeleton-line" style="width:60%;height:28px;margin-bottom:2rem"></div>
        <div class="skeleton-line" style="width:100%"></div>
        <div class="skeleton-line" style="width:100%"></div>
        <div class="skeleton-line" style="width:95%"></div>
        <div class="skeleton-line" style="width:100%"></div>
        <div class="skeleton-line" style="width:88%"></div>
        <div class="skeleton-line" style="width:100%"></div>
        <div class="skeleton-line" style="width:92%"></div>
        <div class="skeleton-line" style="width:100%"></div>
        <div class="skeleton-line" style="width:78%"></div>
      </div>
      <article v-else class="chapter-body" :class="fontSizeClass">
        <h1 class="chapter-title">{{ chapter?.title }}</h1>
        <p v-for="(paragraph, index) in paragraphs" :key="index" class="paragraph">
          {{ paragraph }}
        </p>
      </article>
    </main>

    <footer class="reader-footer" :class="{ 'bar-hidden': !showFooter }">
      <div class="nav-buttons">
        <button
          class="nav-btn nav-prev"
          :disabled="!hasPrev"
          @click="goToPrev"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
          上一章
        </button>
        <button
          class="nav-btn nav-next"
          :disabled="!hasNext"
          @click="goToNext"
        >
          下一章
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
        </button>
      </div>
    </footer>

    <Teleport to="body">
      <div v-if="showDrawer" class="drawer-overlay" @click="showDrawer = false"></div>
      <aside class="drawer" :class="{ 'drawer-open': showDrawer }">
        <div class="drawer-header">
          <h3 class="drawer-title">目录</h3>
          <button class="icon-btn" @click="showDrawer = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="drawer-novel" v-if="novel">
          <h4>{{ novel.title }}</h4>
          <p>{{ novel.author }}</p>
        </div>
        <div class="drawer-progress" v-if="chapterProgress !== null">
          <div class="drawer-progress-bar">
            <div class="drawer-progress-fill" :style="{ width: chapterProgress + '%' }"></div>
          </div>
          <span class="drawer-progress-text">已阅读 {{ chapterProgress }}%</span>
        </div>
        <ul class="chapter-list">
          <li
            v-for="ch in chapters"
            :key="ch.id"
            :class="{ active: ch.id === currentChapterId }"
            @click="goToChapter(ch.id)"
          >
            {{ ch.title }}
          </li>
        </ul>
      </aside>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { novelApi, chapterApi, progressApi, bookmarkApi } from '../api'

interface ChapterData {
  id: number
  title: string
  content: string
  novel_id: number
}

interface NovelData {
  id: number
  title: string
  author: string
  category?: string
}

const route = useRoute()
const router = useRouter()

const chapter = ref<ChapterData | null>(null)
const novel = ref<NovelData | null>(null)
const chapters = ref<{ id: number; title: string }[]>([])
const showDrawer = ref(false)
const showFooter = ref(true)
const readingProgress = ref(0)
const chapterProgress = ref<number | null>(null)
const chapterLoading = ref(false)

const theme = ref('light')
const fontSize = ref('medium')
const isBookmarked = ref(false)
const currentBookmarkId = ref<number | null>(null)

const showThemeMenu = ref(false)
const showFontMenu = ref(false)

const themeClass = computed(() => `theme-${theme.value}`)
const fontSizeClass = computed(() => `font-${fontSize.value}`)

const paragraphs = computed(() => {
  if (!chapter.value?.content) return []
  return chapter.value.content.split('\n').filter((p) => p.trim())
})

const hasPrev = computed(() => {
  if (!chapters.value.length) return false
  const idx = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  return idx > 0
})

const hasNext = computed(() => {
  if (!chapters.value.length) return false
  const idx = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  return idx < chapters.value.length - 1
})

const currentChapterId = computed(() => Number(route.params.id))

const currentChapterIndex = computed(() => {
  if (!chapters.value.length) return 0
  return chapters.value.findIndex((c) => c.id === currentChapterId.value)
})

const loadChapter = async () => {
  chapterLoading.value = true
  try {
    const res: any = await chapterApi.detail(currentChapterId.value)
    chapter.value = res

    if (res.novel_id && !novel.value) {
      const novelRes: any = await novelApi.detail(res.novel_id)
      novel.value = novelRes
      loadChapters(res.novel_id)
    }
  } catch (error) {
    ElMessage.error('加载章节失败')
  } finally {
    chapterLoading.value = false
  }
}

const loadChapters = async (novelId: number) => {
  try {
    const res: any = await novelApi.chapters(novelId)
    chapters.value = res.results || res.chapters || res || []
    updateChapterProgress()
  } catch (error) {
    console.error('加载目录失败:', error)
  }
}

const updateChapterProgress = () => {
  if (!chapters.value.length || currentChapterIndex.value < 0) return
  chapterProgress.value = Math.round(((currentChapterIndex.value + 1) / chapters.value.length) * 100)
}

const updateReadingProgress = () => {
  const scrollTop = window.scrollY
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight
  if (scrollHeight > 0) {
    readingProgress.value = Math.round((scrollTop / scrollHeight) * 100)
  }
}

const saveReadingProgress = async () => {
  if (!chapter.value?.novel_id) return
  try {
    await progressApi.update({
      novel_id: chapter.value.novel_id,
      chapter_id: chapter.value.id,
      position: readingProgress.value,
    })
  } catch (error) {
    console.error('保存阅读进度失败:', error)
  }
}

const checkBookmark = async () => {
  if (!chapter.value) return
  try {
    const res: any = await bookmarkApi.byChapter(chapter.value.id)
    isBookmarked.value = true
    currentBookmarkId.value = res.id
  } catch (error) {
    isBookmarked.value = false
    currentBookmarkId.value = null
  }
}

const toggleBookmark = async () => {
  if (!chapter.value) return

  if (isBookmarked.value && currentBookmarkId.value) {
    try {
      await bookmarkApi.remove(currentBookmarkId.value)
      isBookmarked.value = false
      currentBookmarkId.value = null
      ElMessage.success('已取消书签')
    } catch (error) {
      ElMessage.error('取消书签失败')
    }
  } else {
    try {
      const res: any = await bookmarkApi.add({
        novel_id: chapter.value.novel_id,
        chapter_id: chapter.value.id,
        position: readingProgress.value,
        note: chapter.value.title,
      })
      isBookmarked.value = true
      currentBookmarkId.value = res.id
      ElMessage.success('已添加书签')
    } catch (error) {
      ElMessage.error('添加书签失败')
    }
  }
}

const goBack = () => {
  if (novel.value) {
    router.push({ name: 'NovelDetail', params: { id: novel.value.id } })
  } else {
    router.push({ name: 'Home' })
  }
}

const goToPrev = () => {
  if (!hasPrev.value) return
  const idx = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  const prevChapter = chapters.value[idx - 1]
  router.push({ name: 'Reader', params: { id: prevChapter.id } })
}

const goToNext = () => {
  if (!hasNext.value) return
  const idx = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  const nextChapter = chapters.value[idx + 1]
  router.push({ name: 'Reader', params: { id: nextChapter.id } })
}

const goToChapter = (id: number) => {
  router.push({ name: 'Reader', params: { id } })
  showDrawer.value = false
}

const toggleHeader = () => {
  showFooter.value = !showFooter.value
}

const handleThemeChange = (command: string) => {
  theme.value = command
  localStorage.setItem('readerTheme', command)
  showThemeMenu.value = false
}

const handleFontSizeChange = (command: string) => {
  fontSize.value = command
  localStorage.setItem('readerFontSize', command)
  showFontMenu.value = false
}

const toggleThemeMenu = () => {
  showThemeMenu.value = !showThemeMenu.value
  showFontMenu.value = false
}

const toggleFontMenu = () => {
  showFontMenu.value = !showFontMenu.value
  showThemeMenu.value = false
}

const closeMenus = () => {
  showThemeMenu.value = false
  showFontMenu.value = false
}

const beforeUnloadHandler = (_e: BeforeUnloadEvent) => {
  saveReadingProgress()
}

let scrollHandler: () => void
let autoSaveTimer: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  const savedTheme = localStorage.getItem('readerTheme')
  const savedFontSize = localStorage.getItem('readerFontSize')
  if (savedTheme) theme.value = savedTheme
  if (savedFontSize) fontSize.value = savedFontSize

  await loadChapter()
  checkBookmark()

  scrollHandler = updateReadingProgress
  window.addEventListener('scroll', scrollHandler)
  window.addEventListener('beforeunload', beforeUnloadHandler)
  document.addEventListener('click', closeMenus)

  autoSaveTimer = setInterval(() => {
    saveReadingProgress()
  }, 30000)
})

onBeforeUnmount(() => {
  saveReadingProgress()
})

onUnmounted(() => {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler)
  }
  window.removeEventListener('beforeunload', beforeUnloadHandler)
  document.removeEventListener('click', closeMenus)
  if (autoSaveTimer) {
    clearInterval(autoSaveTimer)
  }
})

watch(() => route.params.id, async (newId) => {
  if (!newId) return
  await saveReadingProgress()
  await loadChapter()
  checkBookmark()
  window.scrollTo(0, 0)
  readingProgress.value = 0
  updateChapterProgress()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500&display=swap');

.reader {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-hover: #B07800;
  --border: #E0E0E0;
  min-height: 100vh;
  background: var(--paper-bg);
  color: var(--ink);
  transition: background-color 0.3s, color 0.3s;
}

.reader.theme-light {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --border: #E0E0E0;
  --header-bg: rgba(253, 251, 247, 0.88);
  --header-border: rgba(0, 0, 0, 0.06);
}

.reader.theme-sepia {
  --paper-bg: #F4ECD8;
  --ink: #3D3225;
  --muted: #8B7E6A;
  --border: #D6CCAF;
  --header-bg: rgba(244, 236, 216, 0.88);
  --header-border: rgba(0, 0, 0, 0.06);
}

.reader.theme-dark {
  --paper-bg: #1A1A1A;
  --ink: #D4D4D4;
  --muted: #8A8A8A;
  --border: #333333;
  --header-bg: rgba(26, 26, 26, 0.88);
  --header-border: rgba(255, 255, 255, 0.08);
}

.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1.5rem;
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--header-border);
  transition: transform 0.2s ease;
}

.reader-header.header-hidden {
  transform: translateY(-100%);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  flex: 1;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.82rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

.breadcrumb-link {
  color: var(--muted);
  text-decoration: none;
  cursor: pointer;
  transition: color 0.15s;
  flex-shrink: 0;
}

.breadcrumb-link:hover {
  color: var(--accent);
}

.breadcrumb-sep {
  color: var(--border);
  flex-shrink: 0;
}

.breadcrumb-current {
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--ink);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.icon-btn:hover {
  background: rgba(0, 0, 0, 0.06);
}

.icon-btn-active {
  color: var(--accent);
}

.icon-btn-active:hover {
  background: rgba(202, 138, 4, 0.1);
}

.theme-dark .icon-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dropdown-wrap {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 200;
  min-width: 100px;
  background: var(--paper-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  padding: 4px 0;
  overflow: hidden;
}

.theme-dark .dropdown-menu {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--ink);
  font-size: 0.85rem;
  font-family: 'Noto Sans SC', sans-serif;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.theme-dark .dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.dropdown-item.active {
  color: var(--accent);
  font-weight: 500;
}

.progress-bar {
  position: fixed;
  top: 49px;
  left: 0;
  right: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.4rem 1.5rem;
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--header-border);
  transition: transform 0.2s ease;
}

.progress-bar.bar-hidden {
  transform: translateY(calc(-100% - 49px));
}

.progress-track {
  flex: 1;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #CA8A04, #EAB308);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.72rem;
  color: var(--muted);
  min-width: 32px;
  text-align: right;
}

.reader-content {
  max-width: 700px;
  margin: 0 auto;
  padding: 5.5rem 1.5rem 7rem;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
}

.skeleton-wrap {
  padding: 2rem 0;
}

.skeleton-line {
  height: 18px;
  margin-bottom: 1.2em;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--border) 25%, rgba(0, 0, 0, 0.04) 50%, var(--border) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

.theme-dark .skeleton-line {
  background: linear-gradient(90deg, #2a2a2a 25%, #333 50%, #2a2a2a 75%);
  background-size: 200% 100%;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.chapter-body {
  line-height: 1.9;
  font-family: 'Libre Baskerville', 'Noto Serif SC', serif;
  transition: font-size 0.2s ease;
}

.chapter-body.font-small {
  font-size: 0.95rem;
}

.chapter-body.font-medium {
  font-size: 1.1rem;
}

.chapter-body.font-large {
  font-size: 1.3rem;
}

.chapter-title {
  font-family: 'Cormorant Garamond', 'Noto Serif SC', serif;
  font-size: 1.75em;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 2rem;
  text-align: center;
  letter-spacing: 0.02em;
}

.paragraph {
  margin: 0 0 1.5em;
  text-indent: 2em;
}

.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 0.75rem 1.5rem;
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--header-border);
  transition: transform 0.2s ease;
}

.reader-footer.bar-hidden {
  transform: translateY(100%);
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  max-width: 700px;
  margin: 0 auto;
}

.nav-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  flex: 1;
  height: 42px;
  border: 1.5px solid var(--accent);
  border-radius: 8px;
  background: transparent;
  color: var(--accent);
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: var(--accent);
  color: #fff;
}

.nav-btn:disabled {
  border-color: var(--border);
  color: var(--muted);
  cursor: not-allowed;
  opacity: 0.5;
}

.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(0, 0, 0, 0.3);
  transition: opacity 0.2s;
}

.theme-dark .drawer-overlay {
  background: rgba(0, 0, 0, 0.5);
}

.drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 501;
  width: 300px;
  max-width: 85vw;
  background: var(--paper-bg);
  border-left: 1px solid var(--border);
  transform: translateX(100%);
  transition: transform 0.25s ease;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.drawer-open {
  transform: translateX(0);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.drawer-title {
  font-family: 'Cormorant Garamond', 'Noto Serif SC', serif;
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
}

.drawer-novel {
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.drawer-novel h4 {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0 0 0.2rem;
}

.drawer-novel p {
  font-size: 0.8rem;
  color: var(--muted);
  margin: 0;
}

.drawer-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.drawer-progress-bar {
  flex: 1;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.drawer-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #CA8A04, #EAB308);
  border-radius: 2px;
  transition: width 0.3s;
}

.drawer-progress-text {
  font-size: 0.72rem;
  color: var(--muted);
  white-space: nowrap;
}

.chapter-list {
  list-style: none;
  padding: 0.5rem 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.chapter-list li {
  padding: 0.65rem 1.25rem;
  font-size: 0.88rem;
  font-family: 'Noto Sans SC', sans-serif;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  border-left: 3px solid transparent;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-list li:hover {
  background: rgba(0, 0, 0, 0.03);
}

.theme-dark .chapter-list li:hover {
  background: rgba(255, 255, 255, 0.04);
}

.chapter-list li.active {
  border-left-color: var(--accent);
  background: rgba(202, 138, 4, 0.06);
  color: var(--accent);
  font-weight: 500;
}

.theme-dark .chapter-list li.active {
  background: rgba(202, 138, 4, 0.1);
}

@media (max-width: 768px) {
  .reader-header {
    padding: 0.5rem 1rem;
  }

  .breadcrumb {
    font-size: 0.75rem;
  }

  .progress-bar {
    padding: 0.35rem 1rem;
  }

  .reader-content {
    padding: 4.5rem 1rem 6rem;
  }

  .chapter-title {
    font-size: 1.4em;
  }

  .nav-btn {
    font-size: 0.82rem;
    height: 38px;
  }
}
</style>
