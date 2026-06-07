<template>
  <div class="my-follows-page">
    <header class="mf-header">
      <div class="mf-header__inner">
        <h1 class="mf-logo" @click="goHome">墨香书阁</h1>
        <nav class="mf-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/user" class="active">个人中心</router-link>
        </nav>
        <div class="mf-header__actions">
          <span class="mf-user">{{ userInfo.username }}</span>
          <button class="mf-btn-back" @click="goBack">返回中心</button>
        </div>
      </div>
    </header>

    <main class="mf-main">
      <div class="mf-title-bar">
        <h2 class="mf-title">我的关注</h2>
        <span class="mf-count" v-if="totalCount > 0">共 {{ totalCount }} 位作者</span>
      </div>

      <div v-if="loading" class="mf-loading">
        <div v-for="i in 6" :key="i" class="mf-skeleton-item"></div>
      </div>

      <div v-else-if="list.length > 0" class="mf-list">
        <div
          v-for="item in list"
          :key="item.id"
          class="mf-card"
        >
          <div class="mf-avatar">
            {{ (item.author_name || '').charAt(0) }}
          </div>
          <div class="mf-body">
            <h4 class="mf-author-name" @click="goToAuthor(item.author_name)">{{ item.author_name }}</h4>
            <p class="mf-time">关注于 {{ item.created_at }}</p>
          </div>
          <div class="mf-actions">
            <button class="mf-btn-unfollow" :disabled="item._loading" @click="handleUnfollow(item)">
              {{ item._loading ? '处理中...' : '取消关注' }}
            </button>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="mf-pagination">
          <button
            class="mf-pg-btn"
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
          >上一页</button>
          <span class="mf-pg-info">{{ currentPage }} / {{ totalPages }}</span>
          <button
            class="mf-pg-btn"
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
          >下一页</button>
        </div>
      </div>

      <div v-else class="mf-empty">
        <svg width="72" height="72" viewBox="0 0 64 64" fill="none">
          <path d="M48 56L32 44 16 56V12a4 4 0 014-4h24a4 4 0 014 4v44z" fill="#F5F1EA" stroke="#CA8A04" stroke-width="1.5"/>
          <line x1="24" y1="18" x2="40" y2="18" stroke="#E0E0E0" stroke-width="1.5"/>
          <line x1="24" y1="26" x2="36" y2="26" stroke="#E0E0E0" stroke-width="1.5"/>
        </svg>
        <p class="mf-empty__title">还没有关注任何作者</p>
        <p class="mf-empty__hint">去小说详情页发现喜欢的作者吧</p>
        <button class="mf-btn-gold" @click="goToNovels">浏览书库</button>
      </div>
    </main>

    <footer class="mf-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { followApi } from '../api'

const router = useRouter()
const route = useRoute()

const userInfo = reactive(JSON.parse(localStorage.getItem('user') || '{}'))
const list = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = 20
const totalPages = ref(1)
const loading = ref(true)

const loadList = async (page = 1) => {
  loading.value = true
  try {
    const res: any = await followApi.myFollows({ page, page_size: pageSize })
    list.value = (res.results || []).map((item: any) => ({ ...item, _loading: false }))
    totalCount.value = res.count || 0
    totalPages.value = Math.ceil(totalCount.value / pageSize) || 1
    currentPage.value = page
  } catch (err) {
    console.error('获取关注列表失败:', err)
    ElMessage.error('获取关注列表失败')
  } finally {
    loading.value = false
  }
}

const handleUnfollow = async (item: any) => {
  try {
    await ElMessageBox.confirm(`确定取消关注「${item.author_name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    item._loading = true
    await followApi.unfollow(item.author_name)
    list.value = list.value.filter((f: any) => f.id !== item.id)
    totalCount.value = Math.max(0, totalCount.value - 1)
    ElMessage.success('已取消关注')
  } catch (err: any) {
    if (err !== 'cancel') ElMessage.error('操作失败')
  } finally {
    item._loading = false
  }
}

const changePage = (page: number) => {
  loadList(page)
}

const goToAuthor = (name: string) => {
  router.push({ name: 'AuthorProfile', params: { name: encodeURIComponent(name) } })
}

const goHome = () => router.push('/')
const goToNovels = () => router.push('/novels')
const goBack = () => router.push('/user')

onMounted(() => {
  const page = Number(route.query.page) || 1
  loadList(page)
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

.my-follows-page {
  min-height: 100vh;
  background: #FDFBF7;
  color: #1A1A1A;
  font-family: 'Noto Sans SC', sans-serif;
}

.mf-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #1A1A1A;
  border-bottom: 2px solid #CA8A04;
}
.mf-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 58px;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.mf-logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #CA8A04;
  cursor: pointer;
  letter-spacing: 3px;
  flex-shrink: 0;
  margin: 0;
}
.mf-nav { display: flex; gap: 0.25rem; flex: 1; }
.mf-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
}
.mf-nav a:hover,
.mf-nav a.active { color: #CA8A04; background: rgba(202,138,4,0.1); }

.mf-header__actions { display: flex; align-items: center; gap: 1rem; flex-shrink: 0; }
.mf-user { color: #D1D5DB; font-size: 0.88rem; }
.mf-btn-back {
  background: transparent;
  border: 1px solid #4B5563;
  color: #9CA3AF;
  font-size: 0.82rem;
  padding: 5px 14px;
  border-radius: 2px;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s;
  font-family: 'Noto Sans SC', sans-serif;
}
.mf-btn-back:hover { border-color: #EF4444; color: #EF4444; }

.mf-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 74px 2rem 2rem;
  min-height: calc(100vh - 80px);
}

.mf-title-bar {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 2rem;
}
.mf-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #1A1A1A;
  letter-spacing: 3px;
  margin: 0;
}
.mf-count { font-size: 0.82rem; color: #6B7280; }

/* List */
.mf-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mf-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 3px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.mf-card:hover {
  border-color: #CA8A04;
  box-shadow: 0 2px 12px rgba(202,138,4,0.08);
}

.mf-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #CA8A04 0%, #92600A 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Serif SC', serif;
  font-size: 1.3rem;
  font-weight: 700;
  flex-shrink: 0;
}

.mf-body { flex: 1; min-width: 0; }
.mf-author-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1A1A;
  cursor: pointer;
  margin: 0 0 0.2rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
}
.mf-author-name:hover { color: #CA8A04; }
.mf-time { font-size: 0.78rem; color: #9CA3AF; margin: 0; }

.mf-actions { flex-shrink: 0; }
.mf-btn-unfollow {
  background: transparent;
  border: 1px solid #E0E0E0;
  color: #6B7280;
  font-size: 0.82rem;
  padding: 7px 18px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 0.5px;
}
.mf-btn-unfollow:hover:not(:disabled) {
  border-color: #EF4444;
  color: #EF4444;
  background: rgba(239,76,60,0.04);
}
.mf-btn-unfollow:disabled { opacity: 0.5; cursor: not-allowed; }

/* Pagination */
.mf-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #E0E0E0;
}
.mf-pg-btn {
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  color: #1A1A1A;
  font-size: 0.84rem;
  padding: 7px 20px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Noto Sans SC', sans-serif;
}
.mf-pg-btn:hover:not(:disabled) { border-color: #CA8A04; color: #CA8A04; }
.mf-pg-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.mf-pg-info { font-size: 0.84rem; color: #6B7280; }

/* Loading */
.mf-loading { display: flex; flex-direction: column; gap: 0.75rem; }
.mf-skeleton-item {
  height: 80px;
  border-radius: 3px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5df 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: mfShimmer 1.5s infinite;
}
@keyframes mfShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Empty */
.mf-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5rem 0;
  gap: 0.75rem;
}
.mf-empty__title { font-size: 1.05rem; color: #1A1A1A; font-family: 'Noto Serif SC', serif; margin: 0; }
.mf-empty__hint { font-size: 0.85rem; color: #6B7280; margin: 0; }

.mf-btn-gold {
  background: #CA8A04;
  color: #fff;
  border: none;
  padding: 9px 28px;
  border-radius: 2px;
  font-size: 0.88rem;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 1px;
  margin-top: 0.5rem;
  transition: background 0.2s;
  box-shadow: 0 2px 8px rgba(202,138,4,0.25);
}
.mf-btn-gold:hover { background: #A67C00; }

.mf-footer {
  text-align: center;
  padding: 2rem;
  color: #6B7280;
  font-size: 0.82rem;
  letter-spacing: 2px;
  border-top: 1px solid #E0E0E0;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .mf-header__inner { padding: 0 1.25rem; }
  .mf-main { padding: 66px 1.25rem 1.5rem; }
  .mf-nav { display: none; }
  .mf-card { padding: 1rem; gap: 1rem; }
  .mf-avatar { width: 42px; height: 42px; font-size: 1.1rem; }
}
</style>
