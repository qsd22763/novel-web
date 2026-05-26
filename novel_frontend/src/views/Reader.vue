<template>
  <div class="reader" :class="themeClass">
    <header class="reader-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <h2 class="chapter-title">{{ chapter?.title || '加载中...' }}</h2>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click" @command="handleThemeChange">
          <el-button :icon="Brush" circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="light">明亮</el-dropdown-item>
              <el-dropdown-item command="sepia">护眼</el-dropdown-item>
              <el-dropdown-item command="dark">夜间</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-dropdown trigger="click" @command="handleFontSizeChange">
          <el-button :icon="Plus" circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="small">小</el-dropdown-item>
              <el-dropdown-item command="medium">中</el-dropdown-item>
              <el-dropdown-item command="large">大</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button :icon="List" circle @click="showDrawer = true" />
      </div>
    </header>

    <div class="progress-bar" v-show="showFooter">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: readingProgress + '%' }"></div>
      </div>
      <span class="progress-text">{{ readingProgress }}%</span>
    </div>

    <main class="reader-content" @click="toggleHeader">
      <article class="chapter-body" :class="fontSizeClass">
        <p v-for="(paragraph, index) in paragraphs" :key="index" class="paragraph">
          {{ paragraph }}
        </p>
      </article>
    </main>

    <footer class="reader-footer" v-show="showFooter">
      <div class="nav-buttons">
        <el-button
          :disabled="!hasPrev"
          @click="goToPrev"
          size="large"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一章
        </el-button>
        <el-button
          :disabled="!hasNext"
          @click="goToNext"
          size="large"
        >
          下一章
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </footer>

    <el-drawer v-model="showDrawer" direction="rtl" size="300px" :with-header="false">
      <div class="chapter-list">
        <h3 class="list-title">目录</h3>
        <div class="novel-info" v-if="novel">
          <h4>{{ novel.title }}</h4>
          <p>{{ novel.author }}</p>
        </div>
        <div class="chapter-progress" v-if="chapterProgress !== null">
          <el-progress :percentage="chapterProgress" :show-text="false" />
          <span class="progress-label">已阅读 {{ chapterProgress }}%</span>
        </div>
        <ul class="chapter-items">
          <li
            v-for="ch in chapters"
            :key="ch.id"
            :class="{ active: ch.id === currentChapterId }"
            @click="goToChapter(ch.id)"
          >
            {{ ch.title }}
          </li>
        </ul>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, List, Brush, Plus } from '@element-plus/icons-vue'
import request from '../utils/request'

interface Chapter {
  id: number
  title: string
  content: string
  novel_id: number
}

interface Novel {
  id: number
  title: string
  author: string
}

const route = useRoute()
const router = useRouter()

const chapter = ref<Chapter | null>(null)
const novel = ref<Novel | null>(null)
const chapters = ref<{ id: number; title: string }[]>([])
const currentChapterId = computed(() => Number(route.params.id))
const showDrawer = ref(false)
const showFooter = ref(true)
const readingProgress = ref(0)
const chapterProgress = ref<number | null>(null)

const theme = ref('light')
const fontSize = ref('medium')

const themeClass = computed(() => `theme-${theme.value}`)
const fontSizeClass = computed(() => `font-${fontSize.value}`)

const paragraphs = computed(() => {
  if (!chapter.value?.content) return []
  return chapter.value.content.split('\n').filter((p) => p.trim())
})

const hasPrev = computed(() => {
  if (!chapters.value.length) return false
  const currentIndex = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  return currentIndex > 0
})

const hasNext = computed(() => {
  if (!chapters.value.length) return false
  const currentIndex = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  return currentIndex < chapters.value.length - 1
})

const currentChapterIndex = computed(() => {
  if (!chapters.value.length) return 0
  return chapters.value.findIndex((c) => c.id === currentChapterId.value)
})

const loadChapter = async () => {
  try {
    const res = await request.get(`/chapters/${currentChapterId.value}/`)
    chapter.value = res

    if (res.novel_id && !novel.value) {
      const novelRes = await request.get(`/novels/${res.novel_id}/`)
      novel.value = novelRes
      loadChapters(res.novel_id)
    }
  } catch (error) {
    ElMessage.error('加载章节失败')
  }
}

const loadChapters = async (novelId: number) => {
  try {
    const res = await request.get(`/novels/${novelId}/chapters/`)
    chapters.value = res.results || res || []
    updateChapterProgress()
  } catch (error) {
    console.error('加载目录失败:', error)
  }
}

const updateChapterProgress = () => {
  if (!chapters.value.length || currentChapterIndex.value < 0) return
  const progress = Math.round(((currentChapterIndex.value + 1) / chapters.value.length) * 100)
  chapterProgress.value = progress
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
    await request.post('/reading-progress/update_progress/', {
      novel_id: chapter.value.novel_id,
      chapter_id: chapter.value.id,
      position: readingProgress.value,
    })
  } catch (error) {
    console.error('保存阅读进度失败:', error)
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
  const currentIndex = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  const prevChapter = chapters.value[currentIndex - 1]
  router.push({ name: 'Reader', params: { id: prevChapter.id } })
}

const goToNext = () => {
  if (!hasNext.value) return
  const currentIndex = chapters.value.findIndex((c) => c.id === currentChapterId.value)
  const nextChapter = chapters.value[currentIndex + 1]
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
}

const handleFontSizeChange = (command: string) => {
  fontSize.value = command
  localStorage.setItem('readerFontSize', command)
}

let scrollHandler: () => void

onMounted(() => {
  const savedTheme = localStorage.getItem('readerTheme')
  const savedFontSize = localStorage.getItem('readerFontSize')
  if (savedTheme) theme.value = savedTheme
  if (savedFontSize) fontSize.value = savedFontSize

  loadChapter()
  saveReadingProgress()

  scrollHandler = updateReadingProgress
  window.addEventListener('scroll', scrollHandler)
})

onUnmounted(() => {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler)
  }
})

watch(() => route.params.id, () => {
  loadChapter()
  saveReadingProgress()
  window.scrollTo(0, 0)
  readingProgress.value = 0
  updateChapterProgress()
})
</script>

<style scoped>
.reader {
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
}

.reader.theme-light {
  background: #faf8f5;
  color: #2d2d2d;
}

.reader.theme-sepia {
  background: #f4ecd8;
  color: #5b4636;
}

.reader.theme-dark {
  background: #1a1a1a;
  color: #d4d4d4;
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
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.theme-dark .reader-header {
  background: rgba(26, 26, 26, 0.95);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chapter-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
  color: inherit;
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

.progress-bar {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  z-index: 99;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.theme-dark .progress-bar {
  background: rgba(26, 26, 26, 0.95);
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.progress-track {
  flex: 1;
  height: 4px;
  background: #e5e5e5;
  border-radius: 2px;
  overflow: hidden;
}

.theme-dark .progress-track {
  background: rgba(255, 255, 255, 0.1);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #888;
  min-width: 36px;
  text-align: right;
}

.reader-content {
  max-width: 700px;
  margin: 0 auto;
  padding: 5rem 1.5rem 8rem;
  cursor: pointer;
}

.chapter-body {
  line-height: 1.8;
  transition: font-size 0.3s;
}

.chapter-body.font-small {
  font-size: 0.9rem;
}

.chapter-body.font-medium {
  font-size: 1.1rem;
}

.chapter-body.font-large {
  font-size: 1.3rem;
}

.paragraph {
  margin: 0 0 1.5em;
  text-indent: 2em;
}

.theme-sepia .paragraph {
  color: #5b4636;
}

.theme-dark .paragraph {
  color: #b0b0b0;
}

.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.theme-dark .reader-footer {
  background: rgba(26, 26, 26, 0.95);
  border-top-color: rgba(255, 255, 255, 0.1);
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  max-width: 700px;
  margin: 0 auto;
}

.nav-buttons .el-button {
  flex: 1;
  height: 44px;
  font-size: 0.95rem;
}

.chapter-list {
  padding: 1rem;
}

.list-title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.25rem;
  margin: 0 0 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
}

.novel-info {
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.novel-info h4 {
  font-size: 1rem;
  margin: 0 0 0.25rem;
}

.novel-info p {
  font-size: 0.85rem;
  color: #888;
  margin: 0;
}

.chapter-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.chapter-progress :deep(.el-progress-bar__outer) {
  background: #e5e5e5;
}

.progress-label {
  font-size: 0.75rem;
  color: #888;
  white-space: nowrap;
}

.chapter-items {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.chapter-items li {
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-items li:hover {
  background: #f5f5f5;
}

.chapter-items li.active {
  background: #1a1a1a;
  color: #fff;
}

.theme-dark .chapter-items li:hover {
  background: rgba(255, 255, 255, 0.1);
}

@media (max-width: 768px) {
  .reader-header {
    padding: 0.5rem 1rem;
  }

  .chapter-title {
    font-size: 0.95rem;
    max-width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .reader-content {
    padding: 4rem 1rem 6rem;
  }

  .nav-buttons .el-button {
    font-size: 0.85rem;
  }
}
</style>
