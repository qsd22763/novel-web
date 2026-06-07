<template>
  <div class="author-profile">
    <header class="ap-header">
      <div class="ap-header__inner">
        <h1 class="ap-logo" @click="goHome">墨香书阁</h1>
        <nav class="ap-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
        </nav>
        <div class="ap-header__actions">
          <button v-if="!isLoggedIn" class="ap-btn-login" @click="goLogin">
            登录
          </button>
          <button v-else class="ap-btn-user" @click="goUserCenter">
            用户中心
          </button>
        </div>
      </div>
    </header>

    <main class="ap-main" v-if="!loading">
      <!-- 作者信息区 -->
      <section class="ap-hero">
        <div class="ap-hero__bg"></div>
        <div class="ap-hero__content">
          <div class="ap-avatar-wrap">
            <div class="ap-avatar">
              {{ authorName.charAt(0) }}
            </div>
          </div>
          <div class="ap-info">
            <h2 class="ap-name">{{ authorName }}</h2>
            <p class="ap-bio">墨香书阁签约作者</p>
            <div class="ap-stats">
              <div class="ap-stat">
                <span class="ap-stat__num">{{ authorInfo.novel_count || 0 }}</span>
                <span class="ap-stat__lbl">作品数</span>
              </div>
              <div class="ap-stat__sep"></div>
              <div class="ap-stat">
                <span class="ap-stat__num">{{ authorInfo.follower_count || 0 }}</span>
                <span class="ap-stat__lbl">粉丝数</span>
              </div>
            </div>
          </div>
          <div class="ap-action">
            <button
              class="ap-btn-follow"
              :class="{ followed: isFollowed }"
              :disabled="followLoading"
              @click="toggleFollow"
            >
              <Transition name="follow-icon" mode="out-in">
                <span v-if="isFollowed" key="followed">已关注</span>
                <span v-else key="unfollowed">+ 关注作者</span>
              </Transition>
            </button>
          </div>
        </div>
      </section>

      <!-- 作品列表 -->
      <section class="ap-novels">
        <div class="ap-section-header">
          <span class="ap-section-title">{{ authorName }}的全部作品</span>
          <span class="ap-section-count">共 {{ novels.length }} 部</span>
          <div class="ap-section-line"></div>
        </div>

        <div v-if="novels.length > 0" class="ap-novel-grid">
          <div
            v-for="novel in novels"
            :key="novel.id"
            class="ap-novel-card"
            @click="goToNovel(novel.id)"
          >
            <div class="ap-cover-wrap">
              <img :src="novel.cover || defaultCover" :alt="novel.title" class="ap-cover" @error="onCoverError" />
              <div class="ap-status-tag" :class="novel.status === 1 ? 'complete' : 'ongoing'">
                {{ novel.status === 1 ? '已完结' : '连载中' }}
              </div>
            </div>
            <div class="ap-novel-meta">
              <h4 class="ap-novel-title">{{ novel.title }}</h4>
              <p class="ap-novel-cat">{{ novel.category }}</p>
              <p class="ap-novel-words">{{ formatCount(novel.word_count || 0) }}字</p>
            </div>
          </div>
        </div>

        <div v-else class="ap-empty">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#D8D2C4" stroke-width="1"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
          <p>该作者暂无已发布作品</p>
        </div>
      </section>
    </main>

    <div v-if="loading" class="ap-loading">
      <div class="ap-skeleton-hero"></div>
      <div class="ap-skeleton-grid">
        <div v-for="i in 4" :key="i" class="ap-skeleton-card"></div>
      </div>
    </div>

    <footer class="ap-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { followApi } from '../api'
import { DEFAULT_COVER } from '../utils/image'

const defaultCover = DEFAULT_COVER
const onCoverError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== defaultCover) img.src = defaultCover
}

const route = useRoute()
const router = useRouter()

const authorName = ref('')
const authorInfo = ref<any>({})
const novels = ref<any[]>([])
const isFollowed = ref(false)
const followLoading = ref(false)
const loading = ref(true)

const isLoggedIn = () => !!localStorage.getItem('user')

const formatCount = (num: number): string => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return String(num)
}

const loadAuthorDetail = async () => {
  const name = decodeURIComponent(route.params.name as string)
  authorName.value = name
  loading.value = true
  try {
    const res: any = await followApi.authorDetail(name)
    authorInfo.value = res
    novels.value = res.novels || []
    isFollowed.value = res.is_followed || false
  } catch (err: any) {
    console.error('加载作者信息失败:', err)
    ElMessage.error('作者信息加载失败')
  } finally {
    loading.value = false
  }
}

const toggleFollow = async () => {
  if (!isLoggedIn()) {
    ElMessage.warning('请先登录后再关注作者')
    router.push('/login')
    return
  }
  followLoading.value = true
  try {
    if (isFollowed.value) {
      await followApi.unfollow(authorName.value)
      isFollowed.value = false
      authorInfo.value.follower_count = Math.max(0, (authorInfo.value.follower_count || 1) - 1)
      ElMessage.success('已取消关注')
    } else {
      await followApi.follow(authorName.value)
      isFollowed.value = true
      authorInfo.value.follower_count = (authorInfo.value.follower_count || 0) + 1
      ElMessage.success('关注成功')
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.message || '操作失败')
  } finally {
    followLoading.value = false
  }
}

const goToNovel = (id: number) => {
  router.push({ name: 'NovelDetail', params: { id } })
}

const goHome = () => router.push('/')
const goLogin = () => router.push('/login')
const goUserCenter = () => router.push('/user')

onMounted(() => {
  loadAuthorDetail()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

.author-profile {
  min-height: 100vh;
  background: #FDFBF7;
  color: #1A1A1A;
  font-family: 'Noto Sans SC', sans-serif;
}

.ap-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(253,251,247,0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid #E0E0E0;
}
.ap-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.ap-logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #1A1A1A;
  cursor: pointer;
  letter-spacing: 4px;
  flex-shrink: 0;
}
.ap-logo:hover { opacity: 0.7; }
.ap-nav {
  display: flex;
  gap: 0.25rem;
  flex: 1;
}
.ap-nav a {
  color: #6B7280;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
}
.ap-nav a:hover,
.ap-nav a.router-link-active { color: #CA8A04; background: rgba(202,138,4,0.08); }

.ap-header__actions { display: flex; gap: 0.75rem; flex-shrink: 0; }
.ap-btn-login,
.ap-btn-user {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: transparent;
  border: 1px solid #E0E0E0;
  color: #1A1A1A;
  font-size: 0.82rem;
  padding: 7px 18px;
  border-radius: 2px;
  cursor: pointer;
  transition: border-color 200ms, color 200ms, background 200ms;
}
.ap-btn-login:hover,
.ap-btn-user:hover {
  border-color: #1A1A1A;
  background: #1A1A1A;
  color: #FDFBF7;
}

.ap-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 76px 2rem 2rem;
  min-height: calc(100vh - 80px);
}

/* Hero */
.ap-hero {
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 2.5rem;
  background: linear-gradient(135deg, #1A1A1A 0%, #2d2a26 50%, #1A1A1A 100%);
}
.ap-hero__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(202,138,4,0.12) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(202,138,4,0.08) 0%, transparent 50%);
}
.ap-hero__content {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 2.5rem;
  padding: 3rem 3rem;
}

.ap-avatar-wrap {
  flex-shrink: 0;
}
.ap-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #CA8A04 0%, #92600A 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Serif SC', serif;
  font-size: 2.4rem;
  font-weight: 700;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35), 0 0 0 3px rgba(202,138,4,0.3);
}

.ap-info { flex: 1; }
.ap-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 3px;
  margin: 0 0 0.3rem;
}
.ap-bio {
  color: rgba(255,255,255,0.55);
  font-size: 0.88rem;
  margin: 0 0 1.25rem;
  letter-spacing: 1px;
}
.ap-stats {
  display: flex;
  align-items: center;
  gap: 0;
}
.ap-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-right: 2rem;
}
.ap-stat__num {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #FFD066;
}
.ap-stat__lbl {
  font-size: 0.72rem;
  color: rgba(255,255,255,0.45);
  margin-top: 2px;
  letter-spacing: 1px;
}
.ap-stat__sep {
  width: 1px;
  height: 32px;
  background: rgba(255,255,255,0.12);
  margin-right: 2rem;
}

.ap-action { flex-shrink: 0; }
.ap-btn-follow {
  padding: 11px 32px;
  border-radius: 2px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 250ms;
  letter-spacing: 2px;
  border: 1px solid #CA8A04;
  background: transparent;
  color: #CA8A04;
  font-family: 'Noto Sans SC', sans-serif;
}
.ap-btn-follow:hover:not(:disabled) {
  background: #CA8A04;
  color: #fff;
}
.ap-btn-follow.followed {
  border-color: #22C55E;
  background: rgba(34,197,94,0.1);
  color: #22C55E;
}
.ap-btn-follow.followed:hover:not(:disabled) {
  background: #22C55E;
  color: #fff;
}
.ap-btn-follow:disabled { opacity: 0.55; cursor: not-allowed; }

/* Follow icon animation */
.follow-icon-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.follow-icon-leave-active { transition: all 0.2s ease-in; }
.follow-icon-enter-from { opacity: 0; transform: scale(0.5); }
.follow-icon-leave-to { opacity: 0; transform: scale(1.3); }

/* Novels */
.ap-novels {
  background: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 4px;
  padding: 2.5rem;
}
.ap-section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid #E0E0E0;
}
.ap-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: #1A1A1A;
  letter-spacing: 2px;
  white-space: nowrap;
  position: relative;
  padding-left: 14px;
}
.ap-section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: #CA8A04;
  border-radius: 2px;
}
.ap-section-count {
  font-size: 0.78rem;
  color: #6B7280;
  white-space: nowrap;
}
.ap-section-line { flex: 1; height: 1px; background: #E0E0E0; }

.ap-novel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
}

.ap-novel-card {
  cursor: pointer;
  transition: transform 250ms;
}
.ap-novel-card:hover {
  transform: translateY(-4px);
}
.ap-cover-wrap {
  position: relative;
  height: 280px;
  border-radius: 2px 4px 4px 2px;
  overflow: hidden;
  box-shadow: 4px 4px 16px rgba(0,0,0,0.15);
}
.ap-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.ap-status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.68rem;
  padding: 2px 10px;
  border-radius: 20px;
  letter-spacing: 1px;
  font-family: 'Noto Sans SC', sans-serif;
}
.ap-status-tag.complete {
  background: rgba(107,114,128,0.85);
  color: #D1D5DB;
}
.ap-status-tag.ongoing {
  background: rgba(34,197,94,0.85);
  color: #86EFAC;
}

.ap-novel-meta {
  padding: 0.65rem 0.25rem 0;
}
.ap-novel-title {
  font-size: 0.92rem;
  font-weight: 600;
  color: #1A1A1A;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0 0 0.2rem;
}
.ap-novel-cat {
  font-size: 0.75rem;
  color: #6B7280;
  margin: 0;
}
.ap-novel-words {
  font-size: 0.72rem;
  color: #9CA3AF;
  margin: 0.15rem 0 0;
}

.ap-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 0;
  gap: 0.75rem;
  color: #9CA3AF;
  font-size: 0.92rem;
}

/* Loading skeleton */
.ap-loading { max-width: 1200px; margin: 76px auto 0; padding: 0 2rem; }
.ap-skeleton-hero {
  height: 240px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5df 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: apShimmer 1.5s infinite;
  margin-bottom: 2rem;
}
.ap-skeleton-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}
.ap-skeleton-card {
  height: 360px;
  border-radius: 3px;
  background: linear-gradient(90deg, #f0ede8 25%, #e8e5df 50%, #f0ede8 75%);
  background-size: 200% 100%;
  animation: apShimmer 1.5s infinite;
}
@keyframes apShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.ap-footer {
  text-align: center;
  padding: 2rem;
  color: #6B7280;
  font-size: 0.82rem;
  letter-spacing: 2px;
  border-top: 1px solid #E0E0E0;
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .ap-header__inner { padding: 0 1.25rem; }
  .ap-main { padding: 66px 1.25rem 1.5rem; }
  .ap-hero__content { flex-direction: column; text-align: center; padding: 2rem 1.5rem; gap: 1.25rem; }
  .ap-stats { justify-content: center; }
  .ap-novel-grid { grid-template-columns: repeat(2, 1fr); }
  .ap-novels { padding: 1.5rem; }
  .ap-skeleton-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
