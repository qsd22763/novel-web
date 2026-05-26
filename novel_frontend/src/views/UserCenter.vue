<template>
  <div class="user-center">
    <header class="site-header">
      <div class="header-inner">
        <h1 class="logo" @click="goHome">墨香书阁</h1>
        <nav class="main-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/user" class="active">个人中心</router-link>
        </nav>
        <div class="user-actions">
          <span class="username">{{ userInfo.username }}</span>
          <el-button type="primary" plain @click="handleLogout">退出</el-button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="profile-hero">
        <div class="hero-bg"></div>
        <div class="profile-card">
          <div class="avatar-wrapper">
            <div class="avatar">
              <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.username" />
              <span v-else class="avatar-placeholder">{{ userInfo.username?.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="status-badge">VIP</div>
          </div>
          <div class="profile-info">
            <h2 class="username">{{ userInfo.username }}</h2>
            <p class="bio">「 读书破万卷，下笔如有神 」</p>
            <div class="stats-row">
              <div class="stat-item">
                <span class="stat-value">{{ favorites.length }}</span>
                <span class="stat-label">收藏</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ readingHistory.length }}</span>
                <span class="stat-label">阅读</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formatDays(userInfo.created_at) }}</span>
                <span class="stat-label">注册天数</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="content-section">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="个人信息" name="profile">
            <template #label>
              <span class="tab-label">
                <span class="tab-icon">👤</span>
                <span>个人信息</span>
              </span>
            </template>
            <div class="info-card">
              <div class="card-header">
                <h3>基本信息</h3>
              </div>
              <el-descriptions :column="2" border class="info-descriptions">
                <el-descriptions-item label="用户名">
                  <el-tag type="info">{{ userInfo.username }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="邮箱">
                  <span v-if="userInfo.email">{{ userInfo.email }}</span>
                  <span v-else class="placeholder">未设置</span>
                </el-descriptions-item>
                <el-descriptions-item label="注册时间">
                  {{ formatDate(userInfo.created_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="会员状态">
                  <el-tag type="warning">VIP会员</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-tab-pane>

          <el-tab-pane label="我的收藏" name="favorites">
            <template #label>
              <span class="tab-label">
                <span class="tab-icon">❤️</span>
                <span>我的收藏</span>
              </span>
            </template>
            <div class="novel-grid" v-if="favorites.length > 0">
              <div
                v-for="fav in favorites"
                :key="fav.id"
                class="novel-card"
                @click="goToDetail(fav.novel)"
              >
                <div class="card-glow"></div>
                <div class="cover-wrapper">
                  <img
                    v-lazy="fav.novel?.cover || '/placeholder.png'"
                    :alt="fav.novel?.title"
                    class="novel-cover"
                  />
                  <div class="cover-overlay">
                    <el-button type="primary" size="small" circle>
                      <span>阅读</span>
                    </el-button>
                  </div>
                </div>
                <div class="novel-info">
                  <h3 class="title">{{ fav.novel?.title }}</h3>
                  <p class="author">{{ fav.novel?.author }}</p>
                  <div class="meta">
                    <span class="category">{{ fav.novel?.category }}</span>
                    <span class="status" :class="{ completed: fav.novel?.status === 1 }">
                      {{ fav.novel?.status === 1 ? '已完结' : '连载中' }}
                    </span>
                  </div>
                </div>
                <button class="remove-btn" @click.stop="cancelFavorite(fav.id)">
                  <span>×</span>
                </button>
              </div>
            </div>
            <el-empty v-else class="empty-state">
              <template #image>
                <div class="empty-illustration">📚</div>
              </template>
              <template #description>
                <p class="empty-text">暂无收藏小说</p>
                <p class="empty-hint">快去书库发现喜欢的小说吧</p>
              </template>
              <el-button type="primary" @click="goToNovels">浏览书库</el-button>
            </el-empty>
          </el-tab-pane>

          <el-tab-pane label="阅读记录" name="history">
            <template #label>
              <span class="tab-label">
                <span class="tab-icon">📖</span>
                <span>阅读记录</span>
              </span>
            </template>
            <div class="history-list" v-if="readingHistory.length > 0">
              <div
                v-for="item in readingHistory"
                :key="item.id"
                class="history-item"
                @click="continueReading(item)"
              >
                <div class="item-glow"></div>
                <div class="history-cover">
                  <img
                    v-lazy="item.novel?.cover || '/placeholder.png'"
                    :alt="item.novel?.title"
                  />
                </div>
                <div class="history-info">
                  <h4>{{ item.novel?.title }}</h4>
                  <p class="chapter">阅读至：{{ item.chapter?.title || '序章' }}</p>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: calculateProgress(item) + '%' }"></div>
                  </div>
                  <p class="time">{{ formatDate(item.updated_at) }}</p>
                </div>
                <div class="history-action">
                  <el-button type="primary" circle>
                    <span>继续</span>
                  </el-button>
                </div>
              </div>
            </div>
            <el-empty v-else class="empty-state">
              <template #image>
                <div class="empty-illustration">📖</div>
              </template>
              <template #description>
                <p class="empty-text">暂无阅读记录</p>
                <p class="empty-hint">开始阅读你的第一本小说吧</p>
              </template>
              <el-button type="primary" @click="goToNovels">开始阅读</el-button>
            </el-empty>
          </el-tab-pane>
        </el-tabs>
      </div>
    </main>

    <footer class="site-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const activeTab = ref('profile')
const userInfo = ref<any>({})
const favorites = ref<any[]>([])
const readingHistory = ref<any[]>([])

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDays = (dateStr: string) => {
  if (!dateStr) return 0
  const created = new Date(dateStr)
  const now = new Date()
  return Math.floor((now.getTime() - created.getTime()) / (1000 * 60 * 60 * 24))
}

const calculateProgress = (item: any) => {
  if (!item.novel?.chapter_count) return 0
  const chapterIndex = item.chapter?.chapter_order || 1
  return Math.min(Math.round((chapterIndex / item.novel.chapter_count) * 100), 100)
}

const loadUserInfo = async () => {
  try {
    const res = await request.get('/auth/me/')
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const loadFavorites = async () => {
  try {
    const res = await request.get('/favorites/')
    favorites.value = res.results || []
  } catch (error) {
    console.error('获取收藏失败:', error)
  }
}

const loadReadingHistory = async () => {
  try {
    const res = await request.get('/reading-progress/')
    readingHistory.value = res.results || []
  } catch (error) {
    console.error('获取阅读记录失败:', error)
  }
}

const cancelFavorite = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.delete(`/favorites/${id}/`)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('取消收藏失败')
    }
  }
}

const goToDetail = (novel: any) => {
  if (novel?.id) {
    router.push({ name: 'NovelDetail', params: { id: novel.id } })
  }
}

const continueReading = (item: any) => {
  if (item.chapter?.id) {
    router.push({ name: 'Reader', params: { id: item.chapter.id } })
  } else if (item.novel?.id) {
    router.push({ name: 'NovelDetail', params: { id: item.novel.id } })
  }
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const goToNovels = () => {
  router.push({ name: 'NovelList' })
}

const handleLogout = async () => {
  try {
    await request.post('/auth/logout/')
  } catch (error) {
    console.log('登出请求失败')
  }
  localStorage.removeItem('user')
  ElMessage.success('已退出登录')
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadUserInfo()
  loadFavorites()
  loadReadingHistory()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Ma+Shan+Zheng&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.user-center {
  min-height: 100vh;
  background: #faf8f5;
  color: #2c2c2c;
  font-family: 'Noto Serif SC', serif;
}

.site-header {
  background: linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%);
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 20px rgba(0,0,0,0.15);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
}

.logo {
  font-family: 'Ma Shan Zheng', cursive;
  font-size: 1.8rem;
  color: #d4a574;
  cursor: pointer;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.main-nav {
  display: flex;
  gap: 2rem;
}

.main-nav a {
  color: #c9c9c9;
  text-decoration: none;
  font-size: 0.95rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
  position: relative;
}

.main-nav a:hover,
.main-nav a.active {
  color: #d4a574;
  background: rgba(212, 165, 116, 0.1);
}

.main-nav a.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: #d4a574;
  border-radius: 2px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #d4a574;
  font-size: 0.9rem;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-hero {
  position: relative;
  margin-bottom: 3rem;
}

.hero-bg {
  position: absolute;
  top: -2rem;
  left: -2rem;
  right: -2rem;
  height: 280px;
  background: linear-gradient(135deg, #2c2c2c 0%, #3d3d3d 50%, #d4a574 100%);
  border-radius: 20px;
  z-index: 0;
}

.profile-card {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 2.5rem;
  padding: 2.5rem;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #d4a574 0%, #c4956a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 4px solid #fff;
  box-shadow: 0 8px 25px rgba(212,165,116,0.3);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 3rem;
  color: #fff;
  font-weight: 600;
}

.status-badge {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: linear-gradient(135deg, #ffd700 0%, #ffb347 100%);
  color: #2c2c2c;
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(255,215,0,0.4);
}

.profile-info {
  flex: 1;
}

.profile-info .username {
  font-size: 2rem;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.bio {
  color: #888;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  font-style: italic;
}

.stats-row {
  display: flex;
  gap: 3rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #d4a574;
}

.stat-label {
  font-size: 0.85rem;
  color: #999;
  margin-top: 0.25rem;
}

.content-section {
  background: #fff;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 2rem;
  border-bottom: 2px solid #f0ebe4;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.custom-tabs :deep(.el-tabs__item) {
  font-size: 1rem;
  color: #999;
  padding: 0 1.5rem;
  height: 50px;
  line-height: 50px;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #d4a574;
  font-weight: 600;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background-color: #d4a574;
  height: 3px;
  border-radius: 3px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-icon {
  font-size: 1.2rem;
}

.info-card {
  background: #faf8f5;
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid #f0ebe4;
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.2rem;
  color: #2c2c2c;
  font-weight: 600;
}

.info-descriptions :deep(.el-descriptions__label) {
  background: #f5f0ea;
  color: #666;
  font-weight: 600;
}

.info-descriptions :deep(.el-descriptions__content) {
  color: #2c2c2c;
}

.placeholder {
  color: #bbb;
  font-style: italic;
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.novel-card {
  position: relative;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f0ebe4;
}

.novel-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.12);
}

.novel-card:hover .card-glow {
  opacity: 1;
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(135deg, rgba(212,165,116,0.2) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.cover-wrapper {
  position: relative;
  height: 260px;
  overflow: hidden;
}

.novel-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.novel-card:hover .novel-cover {
  transform: scale(1.05);
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.novel-card:hover .cover-overlay {
  opacity: 1;
}

.novel-info {
  padding: 1rem;
}

.title {
  font-size: 1rem;
  font-weight: 600;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 0.75rem;
}

.meta {
  display: flex;
  gap: 0.5rem;
}

.category {
  background: #f0ebe4;
  color: #8b7355;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.status {
  background: #e8f5e9;
  color: #4caf50;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.status.completed {
  background: #fff3e0;
  color: #ff9800;
}

.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.novel-card:hover .remove-btn {
  opacity: 1;
}

.remove-btn:hover {
  background: #ff5252;
  transform: scale(1.1);
}

.empty-state {
  padding: 3rem;
}

.empty-illustration {
  font-size: 4rem;
  opacity: 0.8;
}

.empty-text {
  font-size: 1.1rem;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
}

.empty-hint {
  color: #999;
  font-size: 0.9rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #faf8f5;
  border-radius: 16px;
  border: 1px solid #f0ebe4;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.history-item:hover {
  background: #fff;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  transform: translateX(5px);
}

.history-item:hover .item-glow {
  opacity: 1;
}

.item-glow {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #d4a574 0%, #c4956a 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.history-cover {
  width: 70px;
  height: 95px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.history-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-info h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.75rem;
}

.progress-bar {
  height: 4px;
  background: #e0d6cc;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #d4a574 0%, #c4956a 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.time {
  font-size: 0.8rem;
  color: #999;
}

.history-action {
  flex-shrink: 0;
}

.site-footer {
  text-align: center;
  padding: 2rem;
  color: #999;
  font-size: 0.9rem;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .header-inner {
    flex-wrap: wrap;
    height: auto;
    padding: 1rem 0;
    gap: 1rem;
  }

  .main-nav {
    order: 3;
    width: 100%;
    justify-content: center;
    gap: 1rem;
  }

  .main-content {
    padding: 1rem;
  }

  .hero-bg {
    height: 200px;
  }

  .profile-card {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }

  .stats-row {
    justify-content: center;
  }

  .novel-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }

  .cover-wrapper {
    height: 200px;
  }

  .history-item {
    flex-direction: column;
    text-align: center;
  }

  .history-action {
    width: 100%;
  }

  .history-action .el-button {
    width: 100%;
  }
}
</style>