<template>
  <div class="novel-detail">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1 class="logo" @click="goHome">免费小说阅读平台</h1>
          <div class="header-actions">
            <el-button v-if="!isLoggedIn" type="primary" @click="goLogin">登录</el-button>
            <el-button v-else @click="goUserCenter">用户中心</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <div class="content-wrapper" v-if="novel">
          <div class="novel-header">
            <img v-lazy="novel.cover" :alt="novel.title" class="novel-cover" @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'" />
            <div class="novel-info">
              <h2>{{ novel.title }}</h2>
              <p class="author">作者：{{ novel.author }}</p>
              <p class="category">分类：{{ novel.category }}</p>
              <p class="status">状态：{{ novel.status === 1 ? '已完结' : '连载中' }}</p>
              <p class="stats">
                <span>字数：{{ novel.word_count }}</span>
                <span>阅读：{{ novel.view_count }}</span>
                <span>章节：{{ novel.chapter_count }}</span>
              </p>
              <div class="action-buttons">
                <el-button type="primary" size="large" @click="startReading">开始阅读</el-button>
                <el-button v-if="isLoggedIn" :type="isFavorited ? 'info' : 'warning'" @click="toggleFavorite">
                  {{ isFavorited ? '已收藏' : '收藏' }}
                </el-button>
              </div>
            </div>
          </div>
          <div class="novel-description">
            <h3>简介</h3>
            <p>{{ novel.description || '暂无简介' }}</p>
          </div>
          <div class="chapter-list">
            <h3>章节列表</h3>
            <ul>
              <li v-for="chapter in chapters" :key="chapter.id" @click="goToRead(chapter.id)">
                {{ chapter.title }}
              </li>
            </ul>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { novelApi, type Novel, type Chapter } from '../api'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const novel = ref<Novel | null>(null)
const chapters = ref<Chapter[]>([])
const isFavorited = ref(false)

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('user')
})

const loadNovelDetail = async () => {
  try {
    const id = Number(route.params.id)
    const [novelRes, chaptersRes] = await Promise.all([
      novelApi.detail(id),
      novelApi.chapters(id),
    ])
    novel.value = novelRes
    chapters.value = chaptersRes.chapters
    if (isLoggedIn.value) {
      checkFavorite(id)
    }
  } catch (error) {
    console.error('加载小说详情失败:', error)
  }
}

const checkFavorite = async (novelId: number) => {
  try {
    const res: any = await request.get('/favorites/check/', { params: { novel_id: novelId } })
    isFavorited.value = res.is_favorited
  } catch (error) {
    console.error('检查收藏状态失败:', error)
  }
}

const toggleFavorite = async () => {
  if (!novel.value) return
  try {
    if (isFavorited.value) {
      await request.delete(`/favorites/${novel.value.id}/`)
      isFavorited.value = false
      ElMessage.success('已取消收藏')
    } else {
      await request.post('/favorites/', { novel: novel.value.id })
      isFavorited.value = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const startReading = () => {
  if (chapters.value.length > 0) {
    goToRead(chapters.value[0].id)
  }
}

const goToRead = (chapterId: number) => {
  router.push({ name: 'Reader', params: { id: chapterId } })
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const goLogin = () => {
  router.push({ name: 'Login' })
}

const goUserCenter = () => {
  router.push({ name: 'UserCenter' })
}

onMounted(() => {
  loadNovelDetail()
})
</script>

<style scoped>
.novel-detail {
  min-height: 100vh;
  background: #f5f5f5;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo {
  margin: 0;
  color: #409eff;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 30px;
}

.novel-header {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.novel-cover {
  width: 200px;
  height: 280px;
  object-fit: cover;
  background: #ddd;
  border-radius: 4px;
}

.novel-info {
  flex: 1;
}

.novel-info h2 {
  margin: 0 0 15px;
}

.novel-info p {
  margin: 8px 0;
  color: #666;
}

.novel-info .stats {
  display: flex;
  gap: 20px;
  color: #999;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.novel-description {
  margin-bottom: 30px;
}

.novel-description h3 {
  margin: 0 0 10px;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.novel-description p {
  color: #666;
  line-height: 1.8;
}

.chapter-list h3 {
  margin: 0 0 15px;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}

.chapter-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.chapter-list li {
  padding: 10px 15px;
  background: #f9f9f9;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-list li:hover {
  background: #409eff;
  color: white;
}
</style>
