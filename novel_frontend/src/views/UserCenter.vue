<template>
  <div class="user-center">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1 class="logo" @click="goHome">免费小说阅读平台</h1>
          <el-button @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      <el-main>
        <div class="content-wrapper">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="个人信息" name="profile">
              <el-card>
                <el-descriptions title="用户信息" :column="1" border>
                  <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
                  <el-descriptions-item label="邮箱">{{ userInfo.email || '未设置' }}</el-descriptions-item>
                  <el-descriptions-item label="注册时间">{{ formatDate(userInfo.created_at) }}</el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-tab-pane>
            <el-tab-pane label="我的收藏" name="favorites">
              <div class="novel-grid" v-if="favorites.length > 0">
                <div v-for="fav in favorites" :key="fav.id" class="novel-card" @click="goToDetail(fav.novel)">
                  <img v-lazy:src="fav.novel_cover || '/placeholder.png'" :alt="fav.novel_title" class="novel-cover" />
                  <div class="novel-info">
                    <h3>{{ fav.novel_title }}</h3>
                    <p class="author">{{ fav.novel_author }}</p>
                    <el-button type="danger" size="small" @click.stop="cancelFavorite(fav.id)">取消收藏</el-button>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无收藏" />
            </el-tab-pane>
            <el-tab-pane label="阅读记录" name="history">
              <div class="history-list" v-if="readingHistory.length > 0">
                <div v-for="item in readingHistory" :key="item.id" class="history-item" @click="continueReading(item)">
                  <div class="history-info">
                    <h4>{{ item.novel_title }}</h4>
                    <p>阅读至：{{ item.chapter_title }}</p>
                    <p class="time">更新时间：{{ formatDate(item.updated_at) }}</p>
                  </div>
                  <el-button type="primary" size="small">继续阅读</el-button>
                </div>
              </div>
              <el-empty v-else description="暂无阅读记录" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-main>
    </el-container>
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

const goToDetail = (novelId: number) => {
  router.push({ name: 'NovelDetail', params: { id: novelId } })
}

const continueReading = (item: any) => {
  router.push({ name: 'Reader', params: { id: item.chapter } })
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const handleLogout = async () => {
  try {
    await request.post('/auth/logout/')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push({ name: 'Home' })
  } catch (error) {
    localStorage.removeItem('user')
    router.push({ name: 'Home' })
  }
}

onMounted(() => {
  loadUserInfo()
  loadFavorites()
  loadReadingHistory()
})
</script>

<style scoped>
.user-center {
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

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
}

.novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.novel-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s;
}

.novel-card:hover {
  transform: translateY(-5px);
}

.novel-cover {
  width: 100%;
  height: 220px;
  object-fit: cover;
  background: #ddd;
}

.novel-info {
  padding: 12px;
}

.novel-info h3 {
  margin: 0 0 8px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author {
  color: #666;
  font-size: 12px;
  margin: 0 0 10px;
}

.history-list {
  background: white;
  border-radius: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.history-item:hover {
  background: #f9f9f9;
}

.history-item:last-child {
  border-bottom: none;
}

.history-info h4 {
  margin: 0 0 5px;
}

.history-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.history-info .time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
</style>
