<template>
  <div class="novel-detail">
    <!-- ===== 顶部导航 ===== -->
    <header class="site-header">
      <div class="header-inner">
        <div class="header-left">
          <h1 class="logo" @click="goHome">墨香书阁</h1>
          <nav v-if="novel" class="breadcrumb" aria-label="breadcrumb">
            <span class="bc-item bc-link" @click="goHome">首页</span>
            <span class="bc-sep">/</span>
            <span class="bc-item bc-link" @click="goToCategory">{{ novel.category }}</span>
            <span class="bc-sep">/</span>
            <span class="bc-current">{{ novel.title }}</span>
          </nav>
        </div>
        <div class="header-actions">
          <button v-if="!isLoggedIn" class="btn-login" @click="goLogin">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            登录
          </button>
          <button v-else class="btn-user" @click="goUserCenter">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            用户中心
          </button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <!-- 骨架屏 -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton-hero"><div class="sk-block"></div></div>
        <div class="skeleton-info">
          <div class="sk-cover"></div>
          <div class="sk-meta">
            <div class="sk-line" style="width:60%;height:22px"></div>
            <div class="sk-line" style="width:35%;height:14px;margin-top:6px"></div>
            <div class="sk-line" style="width:75%;height:36px;margin-top:10px"></div>
          </div>
        </div>
      </div>

      <!-- 主内容 -->
      <template v-else-if="novel">

        <!-- Hero 横幅区 -->
        <section class="hero-section">
          <div class="hero-bg">
            <img :src="novel.cover || defaultCover" :alt="novel.title" class="hero-bg-img" @error="onCoverError" />
          </div>
          <div class="hero-overlay"></div>
          <div class="hero-content">
            <div class="hero-cover-frame">
              <img :src="novel.cover || defaultCover" :alt="novel.title" class="hero-cover-img" @error="onCoverError" />
            </div>
            <div class="hero-meta">
              <h1 class="hero-title">{{ novel.title }}</h1>
              <p class="hero-author-row">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <span class="hero-author-name" @click="goToAuthor">{{ novel.author }}</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="hero-arrow"><polyline points="9 18 15 12 9 6"/></svg>
              </p>
              <div class="hero-tags">
                <span class="tag tag-category">{{ novel.category }}</span>
                <span v-for="tag in parsedTags" :key="tag" class="tag tag-custom">{{ tag }}</span>
                <span class="tag" :class="novel.status === 1 ? 'tag-complete' : 'tag-ongoing'">{{ novel.status === 1 ? '已完结' : '连载中' }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 内容卡片容器 -->
        <div class="content-wrapper">

          <!-- 信息操作区：封面 + 数据 + 按钮 + 作者内联 -->
          <section class="info-section">
            <div class="info-layout">
              <div class="info-left">
                <div class="cover-card" @click="goToAuthor">
                  <img :src="novel.cover || defaultCover" :alt="novel.title" class="side-cover" @error="onCoverError" />
                  <div class="cover-spine"></div>
                </div>
              </div>
              <div class="info-right">
                <div class="stats-row">
                  <div class="stat-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#CA8A04" stroke-width="1.8"><path d="M4 7V4h16v3"/><path d="M9 20h6"/><path d="M12 4v16"/></svg>
                    <b>{{ formatCount(novel.word_count || 0) }}</b><em>字数</em>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.8"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    <b>{{ formatCount(novel.view_count || 0) }}</b><em>阅读</em>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
                    <b>{{ novel.chapter_count || chapters.length }}</b><em>章节</em>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item stat-item--author" @click="goToAuthor">
                    <span class="author-dot">{{ (novel.author || '').charAt(0) }}</span>
                    <b>{{ novel.author }}</b><em>作者 &rarr;</em>
                  </div>
                </div>
                <div class="action-bar">
                  <button class="btn btn--primary" @click="startReading">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    开始阅读
                  </button>
                  <button v-if="isLoggedIn" class="btn btn--secondary" :class="{ active: isFavorited }" @click="toggleFavorite">
                    <Transition name="icon-pop" mode="out-in">
                      <svg v-if="isFavorited" key="f" width="15" height="15" viewBox="0 0 24 24" fill="#CA8A04" stroke="#CA8A04" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                      <svg v-else key="o" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
                    </Transition>
                    {{ isFavorited ? '已收藏' : '收藏' }}
                  </button>
                  <button v-if="isLoggedIn" class="btn btn--secondary" :class="{ followed: isFollowed }" :disabled="followLoading" @click="toggleFollow">
                    <Transition name="icon-pop" mode="out-in">
                      <svg v-if="isFollowed" key="f" width="15" height="15" viewBox="0 0 24 24" fill="#22C55E" stroke="#22C55E" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
                      <svg v-else key="u" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
                    </Transition>
                    {{ isFollowed ? '已关注' : '关注' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 评分展示区 -->
            <div class="rating-display" @click="openRatingDialog">
              <div class="rd-score">
                <span class="rd-num">{{ ratingAvg > 0 ? ratingAvg.toFixed(1) : '--' }}</span>
              </div>
              <div class="rd-info">
                <div class="rd-stars-static">
                  <span v-for="i in 5" :key="'rs'+i" class="rss-star" :class="{ on: i <= Math.round(ratingAvg) }">★</span>
                </div>
                <span class="rd-count">{{ ratingTotal > 0 ? `${ratingTotal}人评分` : '暂无评分' }}</span>
                <span class="rd-hint">{{ isLoggedIn ? (myRatingScore > 0 ? `你评了 ${myRatingScore} 星` : '点击评分') : '登录后可评分' }} &rarr;</span>
              </div>
            </div>
          </section>

          <!-- 内容简介 -->
          <section class="sec-card desc-card">
            <div class="sec-head">
              <svg class="sec-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/><line x1="9" y1="7" x2="16" y2="7"/></svg>
              <span class="sec-title">内容简介</span>
            </div>
            <div class="desc-body" :class="{ collapsed: !descExpanded }">
              <p class="desc-text">{{ novel.description || '暂无简介' }}</p>
            </div>
            <button v-if="novel.description && novel.description.length > 120" class="expand-btn" @click="descExpanded = !descExpanded">
              {{ descExpanded ? '收起' : '展开全文' }}
              <svg :width="12" :height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline :points="!descExpanded ? '6 9 12 15 18 9' : '18 15 12 9 6 15'"/></svg>
            </button>
          </section>

          <!-- 章节目录（横向按钮流式布局） -->
          <section class="sec-card chapter-card">
            <div class="sec-head">
              <svg class="sec-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/></svg>
              <span class="sec-title">章节目录</span>
              <span class="sec-badge">{{ chapters.length }} 章</span>
            </div>
            <div v-if="chapters.length > 0" class="chapter-grid">
              <button v-for="(chapter, idx) in chapters" :key="chapter.id"
                class="ch-btn" :class="{ read: isChapterRead(chapter.id) }"
                :title="`第${idx + 1}章 · ${chapter.title}`"
                @click="goToRead(chapter.id)">
                <strong>{{ idx + 1 }}</strong>
                <span>{{ chapter.title }}</span>
              </button>
            </div>
            <div v-else class="empty-state">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#D0CCC2" stroke-width="1.2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>
              <p>暂无章节</p>
            </div>
          </section>

          <!-- 书评 -->
          <section class="sec-card comment-card">
            <div class="sec-head">
              <svg class="sec-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              <span class="sec-title">书评</span>
              <span class="sec-badge">{{ commentStats.comment_count }} 条</span>
            </div>
            <div class="comment-form">
              <textarea v-model="newContent" class="comment-input" placeholder="留下你的评论…（最多 500 字）" maxlength="500" rows="2"></textarea>
              <div class="comment-actions">
                <span class="counter">{{ newContent.length }} / 500</span>
                <button class="comment-submit" :disabled="submitting || !newContent.trim()" @click="onSubmitComment">
                  {{ submitting ? '发表中…' : '发表评论' }}
                </button>
              </div>
            </div>
            <ul v-if="comments.length" class="comment-list">
              <li v-for="c in comments" :key="c.id" class="comment-item">
                <div class="avatar">{{ (c.username || 'U').slice(0, 1) }}</div>
                <div class="comment-body">
                  <div class="comment-head">
                    <span class="comment-user">{{ c.username }}</span>
                    <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                    <button v-if="isOwnComment(c)" class="comment-del" @click="onDeleteComment(c.id)" title="删除">&times;</button>
                  </div>
                  <p class="comment-text">{{ c.content }}</p>
                </div>
              </li>
            </ul>
            <div v-else class="empty-state empty-state--cmt">
              <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                <rect x="14" y="10" width="26" height="38" rx="2" fill="#F5F1EA" stroke="#E0D6CC" stroke-width="1.2"/>
                <circle cx="27" cy="22" r="3.5" fill="#E8DDD0"/>
                <line x1="19" y1="29" x2="35" y2="29" stroke="#E0D6CC" stroke-width="1.2"/>
                <line x1="19" y1="34" x2="30" y2="34" stroke="#E0D6CC" stroke-width="1.2"/>
              </svg>
              <p class="empty-title">还没有评论，来抢第一条吧</p>
              <p class="empty-hint">分享你对这本书的看法</p>
            </div>
          </section>

        </div>
      </template>

      <!-- 错误状态 -->
      <div v-else class="error-state">
        <svg class="error-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <p class="error-text">小说不存在或加载失败</p>
        <button class="btn-retry" @click="loadNovelDetail">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg>
          重新加载
        </button>
      </div>
    </main>

    <!-- 评分弹窗 -->
    <el-dialog
      v-model="showRatingDialog"
      :title="myRatingScore > 0 ? '修改评分' : '为本书评分'"
      width="380px"
      :close-on-click-modal="true"
      class="rating-dialog"
      align-center>
      <div class="rdlg-body">
        <p class="rdlg-book">{{ novel?.title }}</p>
        <div class="rdlg-stars">
          <span v-for="i in 5" :key="'ds'+i"
            class="rdlg-star"
            :class="{ on: i <= dialogRating, hover: i <= ratingHover }"
            @mouseenter="ratingHover = i"
            @mouseleave="ratingHover = 0"
            @click="dialogRating = i">★</span>
        </div>
        <p class="rdlg-label">
          <template v-if="dialogRating > 0">
            {{ ['','很差','较差','一般','很好','非常好'][dialogRating] }}
          </template>
          <template v-else>点击星星打分</template>
        </p>
        <p v-if="myRatingScore > 0 && dialogRating !== myRatingScore" class="rdlg-old">
          原评分：{{ myRatingScore }} 星
        </p>
      </div>
      <template #footer>
        <button class="btn btn--secondary" @click="showRatingDialog = false">取消</button>
        <button class="btn btn--primary" :disabled="!dialogRating || ratingSubmitting" @click="submitRating">
          {{ ratingSubmitting ? '提交中...' : (myRatingScore > 0 ? '更新评分' : '提交评分') }}
        </button>
      </template>
    </el-dialog>

    <footer class="site-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { novelApi, favoriteApi, progressApi, commentApi, followApi, ratingApi, type Novel, type Chapter, type NovelComment } from '../api'
import { DEFAULT_COVER } from '../utils/image'

const defaultCover = DEFAULT_COVER
const onCoverError = (e: Event) => {
  const img = e.target as HTMLImageElement
  if (img.src !== defaultCover) img.src = defaultCover
}

const route = useRoute()
const router = useRouter()
const novel = ref<Novel | null>(null)
const chapters = ref<Chapter[]>([])
const isFavorited = ref(false)
const isFollowed = ref(false)
const followLoading = ref(false)
const readChapterIds = ref<Set<number>>(new Set())
const loading = ref(false)
const descExpanded = ref(false)

const comments = ref<NovelComment[]>([])
const commentStats = ref({ comment_count: 0, rating_count: 0, avg_rating: 0 })
const newContent = ref('')
const submitting = ref(false)

// ── 评分相关状态 ──
const ratingAvg = ref(0)
const ratingTotal = ref(0)
const myRatingScore = ref(0)
const showRatingDialog = ref(false)
const dialogRating = ref(0)
const ratingHover = ref(0)
const ratingSubmitting = ref(false)

const formatTime = (s: string) => {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const loadComments = async (novelId: number) => {
  try {
    const [listRes, statsRes]: any = await Promise.all([commentApi.list(novelId), commentApi.stats(novelId)])
    comments.value = listRes.results || listRes
    commentStats.value = statsRes
  } catch (e) { console.error('加载评论失败', e) }
}

const onSubmitComment = async () => {
  if (!novel.value) return
  if (!localStorage.getItem('user')) { ElMessage.warning('请先登录后再发表评论'); router.push('/login'); return }
  if (!newContent.value.trim()) return
  submitting.value = true
  try {
    await commentApi.add({ novel: novel.value.id, content: newContent.value.trim() })
    newContent.value = ''
    await loadComments(novel.value.id)
    ElMessage.success('评论已发表')
  } catch (err: any) { ElMessage.error(err?.response?.data?.detail || '评论失败') }
  finally { submitting.value = false }
}

const currentUserId = computed(() => { try { return JSON.parse(localStorage.getItem('user') || '{}').id } catch { return null } })
const isOwnComment = (c: any) => currentUserId.value && c.user === currentUserId.value

const onDeleteComment = async (commentId: number) => {
  try {
    await ElMessageBox.confirm('确定删除这条评论吗？', '提示', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' })
    await commentApi.remove(commentId)
    comments.value = comments.value.filter((c: any) => c.id !== commentId)
    ElMessage.success('已删除')
  } catch (err: any) { if (err !== 'cancel') ElMessage.error('删除失败') }
}

const isLoggedIn = computed(() => !!localStorage.getItem('user'))
const parsedTags = computed(() => { if (!novel.value?.tags) return []; return novel.value.tags.split(',').map((t: string) => t.trim()).filter(Boolean) })

const formatCount = (num: number): string => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return String(num)
}

const isChapterRead = (chapterId: number) => readChapterIds.value.has(chapterId)

// ── 评分功能 ──
const loadRating = async (novelId: number) => {
  try {
    const [statRes, myRes]: any = await Promise.all([
      ratingApi.stat(novelId),
      isLoggedIn.value ? ratingApi.myRating(novelId).catch(() => ({ score: null })) : Promise.resolve({ score: null }),
    ])
    ratingAvg.value = statRes.avg_score || 0
    ratingTotal.value = statRes.total_count || 0
    if (myRes && myRes.score !== null) {
      myRatingScore.value = myRes.score
    }
  } catch (e) { console.error('加载评分失败:', e) }
}

const openRatingDialog = () => {
  if (!isLoggedIn.value) { ElMessage.warning('请先登录后再评分'); router.push('/login'); return }
  dialogRating.value = myRatingScore.value || 0
  showRatingDialog.value = true
}

const submitRating = async () => {
  if (!novel.value || !dialogRating.value) return
  ratingSubmitting.value = true
  try {
    await ratingApi.submit(novel.value.id, dialogRating.value)
    myRatingScore.value = dialogRating.value
    // 刷新统计
    const statRes: any = await ratingApi.stat(novel.value.id)
    ratingAvg.value = statRes.avg_score || 0
    ratingTotal.value = statRes.total_count || 0
    ElMessage.success(dialogRating.value > 3 ? '感谢你的好评！' : '评分已提交，感谢反馈！')
    showRatingDialog.value = false
  } catch (err: any) {
    if (err?.response?.status === 400) {
      ElMessage.warning(err?.response?.data?.message || '评分参数有误')
    } else {
      ElMessage.error('评分提交失败，请重试')
    }
  } finally { ratingSubmitting.value = false }
}

const loadReadChapters = async (novelId: number) => {
  try {
    const res: any = await progressApi.list()
    const ids = new Set<number>()
    ;(res.results || []).forEach((p: any) => { if (p.novel === novelId && p.chapter) ids.add(p.chapter) })
    readChapterIds.value = ids
  } catch (e) { console.error('获取阅读记录失败:', e) }
}

const loadNovelDetail = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const [novelRes, chaptersRes] = await Promise.all([novelApi.detail(id), novelApi.chapters(id)])
    novel.value = novelRes
    chapters.value = (chaptersRes as any).chapters || (chaptersRes as any).results || []
    loadComments(id)
    loadRating(id)
    if (isLoggedIn.value) { checkFavorite(id); checkFollow(); loadReadChapters(id) }
  } catch (error: any) {
    console.error('加载小说详情失败:', error); novel.value = null
    const isTimeout = error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')
    ElMessage.error({ message: isTimeout ? '请求超时，网络较慢，请稍后重试' : '小说详情加载失败，请重试', duration: 4000 })
  } finally { loading.value = false }
}

const checkFavorite = async (nid: number) => { try { const r: any = await favoriteApi.check(nid); isFavorited.value = r.is_favorited } catch {} }
const checkFollow = async () => { if (!novel.value?.author || !isLoggedIn.value) return; try { const r: any = await followApi.check(novel.value.author); isFollowed.value = r.followed } catch {} }

const toggleFollow = async () => {
  if (!novel.value) return
  if (!isLoggedIn.value) { ElMessage.warning('请先登录后再关注作者'); router.push('/login'); return }
  followLoading.value = true
  try {
    if (isFollowed.value) { await followApi.unfollow(novel.value.author); isFollowed.value = false; ElMessage.success('已取消关注') }
    else { await followApi.follow(novel.value.author); isFollowed.value = true; ElMessage.success('关注成功') }
  } catch (err: any) { ElMessage.error(err?.response?.data?.message || '操作失败') }
  finally { followLoading.value = false }
}

const toggleFavorite = async () => {
  if (!novel.value) return
  try {
    if (isFavorited.value) { await favoriteApi.remove(novel.value.id); isFavorited.value = false; ElMessage.success('已取消收藏') }
    else { await favoriteApi.add(novel.value.id); isFavorited.value = true; ElMessage.success('收藏成功') }
  } catch (error: any) {
    const detail = error?.response?.data
    if (typeof detail === 'object' && detail !== null) { const msgs: string[] = []; Object.keys(detail).forEach(k => { const v = detail[k]; if (Array.isArray(v)) msgs.push(v.join(' ')); else if (typeof v === 'string') msgs.push(v) }); if (msgs.length) { ElMessage.error(msgs.join('; ')); return } }
    ElMessage.error(error?.response?.data?.detail || error?.response?.data?.message || '操作失败')
  }
}

const startReading = async () => {
  if (!novel.value || chapters.value.length === 0) return
  if (isLoggedIn.value) { try { const r: any = await progressApi.get(novel.value.id); if (r.chapter_id) { goToRead(r.chapter_id); return } } catch {} }
  goToRead(chapters.value[0].id)
}
const goToRead = (cid: number) => router.push({ name: 'Reader', params: { id: cid } })
const goToCategory = () => { if (novel.value) router.push({ name: 'NovelList', query: { category: novel.value.category } }) }
const goHome = () => router.push('/')
const goLogin = () => router.push('/login')
const goUserCenter = () => router.push('/user')
const goToAuthor = () => { if (novel.value?.author) router.push({ name: 'AuthorProfile', params: { name: encodeURIComponent(novel.value.author) } }) }

onMounted(() => { loadNovelDetail() })
</script>

<style scoped>
/* ============================================================
   小说详情页 — 紧凑高密度布局（修复版）
   ============================================================
   【P1修复】
   - 移除外部字体@import，改用系统安全字体栈
   - 移除所有 backdrop-filter（导致文字模糊）
   - 所有字号 ≥ 12px（最小 0.75rem = 12px）
   - 减少过度 letter-spacing（中文不适用大间距）
   - 仅在 Hero 暗色背景上保留 text-shadow（确保可读性）
   - transform:scale 仅用于交互反馈（按钮点击），不影响静态文字
   - z-index 层级：header=100 > content > hero-overlay

   【P2优化】
   - Hero 高度 200px，紧凑信息密度
   - 数据行单行内联，作者合并到末尾
   - 章节目录横向流式按钮布局
   - 三大模块独立浅底色卡片容器
   - 响应式适配桌面/平板/手机三档
   ============================================================ */

/* ── 字体系统：纯系统安全栈，零外部依赖 ── */
/* 设计目的：移除 Google Fonts @import，
   使用操作系统原生中文字体，渲染最快、最清晰、无加载等待。
   PingFang SC = macOS/iOS，Microsoft YaHei = Windows，
   system-ui 作为最终兜底。 */
:root {
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-light: rgba(202,138,4,0.07);
  --border: #E5DED4;
  --border-light: #EEE9E1;
  --card: #FFFEFA;
  --card-alt: #FCFBF7;
  /* 安全字体栈：不再依赖外部CDN */
  --ff-base: system-ui, -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
  --ff-serif: Georgia, "SimSun", "STSong", serif;
  --r-xs: 4px; --r-sm: 6px; --r-md: 8px;
  --t: all 180ms ease;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.05);
  --shadow-md: 0 3px 12px rgba(0,0,0,.06);
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }

.novel-detail {
  min-height: 100vh;
  /* 纯色渐变背景，无滤镜 */
  background: linear-gradient(175deg, #FAF8F5 0%, #FDFBF7 40%, #F6F2EC 100%);
  color: var(--ink);
  font-family: var(--ff-base);
  /* 确保根元素文字渲染清晰 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ==================== 导航栏 ====================
   修复：移除 backdrop-filter，改用实心半透明背景。
   原因：backdrop-filter blur 在部分浏览器上会导致下方
   渲染区域文字发虚、GPU 内存占用过高。 */
.site-header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  /* 实心背景替代毛玻璃 */
  background: rgba(253,251,247,.92);
  border-bottom: 1px solid var(--border-light);
}
.header-inner {
  max-width: 1100px; margin: 0 auto;
  padding: 0 1.5rem; height: 54px;
  display: flex; align-items: center; justify-content: space-between;
}
.header-left { display: flex; align-items: center; gap: 1.5rem; }
.logo {
  font-family: var(--ff-base); font-size: 1.15rem; font-weight: 700;
  color: var(--ink); cursor: pointer;
  letter-spacing: 2px; user-select: none;
}
.logo:hover { opacity: .75; }
.breadcrumb { display: flex; align-items: center; gap: .4rem; font-size: .8rem; }
.bc-item { color: var(--muted); }
.bc-link { cursor: pointer; transition: color .15s; }
.bc-link:hover { color: var(--accent); }
.bc-sep { color: var(--border); font-size: .72rem; }
.bc-current { color: var(--ink); font-weight: 500; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.btn-login, .btn-user {
  display: inline-flex; align-items: center; gap: .35rem;
  background: transparent; border: 1px solid var(--border);
  color: var(--ink); font-size: .8rem; padding: 6px 14px;
  border-radius: var(--r-sm); cursor: pointer; transition: var(--t);
}
.btn-login:hover, .btn-user:hover { border-color: var(--ink); background: var(--ink); color: #FDFBF7; }

/* ==================== 主容器 ====================
   修复：padding-top = 54px(header高度) + 6px间距 = 60px，
   确保固定导航栏不会遮挡首屏内容。 */
.main-content {
  max-width: 1100px; margin: 0 auto;
  padding: 60px 1.5rem 0;
  min-height: calc(100vh - 70px);
  position: relative; z-index: 1;
}

/* ==================== Hero 区 ====================
   背景 filter 仅作用于图片本身（非文字层），安全。 */
.hero-section {
  position: relative; width: 100%; height: 228px;
  border-radius: var(--r-md); overflow: hidden;
  margin-bottom: 1.25rem; margin-top: .4rem;
  box-shadow: var(--shadow-md);
}
.hero-bg { position: absolute; inset: -20px; }
.hero-bg-img {
  width: 100%; height: 100%; object-fit: cover;
  /* filter 只在背景图上使用，不影响任何文字 */
  filter: blur(24px) brightness(.42) saturate(.65);
  transform: scale(1.18);
}
.hero-overlay {
  position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(180deg,
    rgba(26,26,26,.12) 0%,
    rgba(26,26,26,.42) 50%,
    rgba(26,26,26,.72) 100%
  );
}
.hero-content {
  position: relative; z-index: 2; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: .55rem; padding: 1.5rem; text-align: center;
}
.hero-cover-frame {
  width: 90px; height: 126px; border-radius: var(--r-sm); overflow: hidden;
  box-shadow: 0 12px 32px rgba(0,0,0,.42), 0 0 0 1px rgba(255,255,255,.08);
  flex-shrink: 0;
}
.hero-cover-img { width: 100%; height: 100%; object-fit: cover; }

.hero-meta { display: flex; flex-direction: column; align-items: center; gap: .3rem; }
.hero-title {
  font-family: var(--ff-base); font-size: clamp(1.3rem, 2.8vw, 2rem);
  font-weight: 700; color: #fff;
  letter-spacing: 2px;
  /* Hero 暗色背景上必须用 text-shadow 保证可读性，这是唯一保留的 */
  text-shadow: 0 1px 8px rgba(0,0,0,.45);
  line-height: 1.25;
}
.hero-author-row {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: .82rem; color: rgba(255,255,255,.58);
  letter-spacing: .3px; cursor: pointer; transition: color .15s;
}
.hero-author-row:hover { color: #FFD066; }
.hero-author-row:hover .hero-arrow { transform: translateX(2px); }
.hero-arrow { transition: transform .15s; }
.hero-author-name { border-bottom: 1px dashed rgba(255,255,255,.22); }

.hero-tags { display: flex; gap: .4rem; margin-top: .15rem; flex-wrap: wrap; justify-content: center; }
.tag {
  font-size: .75rem; padding: 2px 9px; border-radius: 20px;
  letter-spacing: .3px;
  /* 修复：移除 backdrop-filter:blur，改用半透明实心背景 */
  background: rgba(255,255,255,.1);
  color: rgba(255,255,255,.7);
  border: 1px solid rgba(255,255,255,.15);
}
.tag-category { background: rgba(202,138,4,.22); color: #FFD066; border-color: rgba(202,138,4,.32); }
.tag-complete { background: rgba(107,114,128,.22); color: #D1D5DB; border-color: rgba(107,114,128,.28); }
.tag-ongoing { background: rgba(34,197,94,.16); color: #86EFAC; border-color: rgba(34,197,94,.28); }
.tag-custom { background: rgba(255,255,255,.08); color: rgba(255,255,255,.56); border-color: rgba(255,255,255,.1); }

/* ==================== 内容卡片容器 ====================
   修复：移除 backdrop-filter，改用实心背景。 */
.content-wrapper {
  background: var(--card);
  border: 1px solid var(--border-light);
  border-radius: var(--r-md);
  padding: 1.5rem; box-shadow: var(--shadow-md);
}

/* ==================== 信息操作区 ====================
   紧凑布局：左封面140px + 右数据+按钮+作者内联 */
.info-section { margin-bottom: 1.25rem; padding-bottom: 1.25rem; border-bottom: 1px solid var(--border-light); }
.info-layout { display: flex; gap: 1.5rem; align-items: stretch; }
.info-left { flex-shrink: 0; }

.cover-card {
  position: relative; width: 140px; cursor: pointer;
  transition: transform .25s ease;
}
.cover-card:hover { transform: translateY(-4px); }
.side-cover {
  width: 140px; height: 195px; object-fit: cover;
  border-radius: 2px 5px 5px 2px;
  box-shadow: 6px 8px 20px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.06);
  display: block;
}
.cover-spine {
  position: absolute; left: 0; top: 0; bottom: 0; width: 5px;
  background: linear-gradient(180deg, #CA8A04 0%, #92600A 100%);
  border-radius: 2px 0 0 2px;
}

.info-right { flex: 1; display: flex; flex-direction: column; gap: .85rem; justify-content: center;

}

/* ---- 数据行 ---- */
.stats-row {
  display: inline-flex; align-items: center; gap: 0;
  background: linear-gradient(135deg, #FBF9F5 0%, #F7F4EE 100%);
  border: 1px solid var(--border-light); border-radius: var(--r-sm);
  padding: 0 1rem; height: 36px;
}
.stat-item {
  display: inline-flex; align-items: center; gap: .35rem;
  padding: 0 .6rem; white-space: nowrap;
}
.stat-item svg { flex-shrink: 0; opacity: .75; }
.stat-item b {
  font-family: var(--ff-base); font-size: .88rem; font-weight: 700;
  color: var(--ink); min-width: 2em; text-align: center;
}
.stat-item em {
  font-style: normal; font-size: .75rem; color: var(--muted);
  letter-spacing: .2px;
}
.stat-divider {
  width: 1px; height: 16px; background: var(--border-light); flex-shrink: 0;
}
.stat-item--author { cursor: pointer; transition: background .15s; border-radius: 4px; padding: 0 .6rem; margin: 0 -.3rem; }
.stat-item--author:hover { background: var(--accent-light); }
.author-dot {
  width: 20px; height: 20px; border-radius: 50%;
  background: linear-gradient(135deg, #CA8A04, #92600A);
  color: #fff; font-family: var(--ff-base); font-size: .75rem;
  font-weight: 700; display: inline-flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-item--author em { color: var(--accent); }

/* ---- 操作按钮：三个按钮完全统一的尺寸体系，仅颜色区分 ---- */
.action-bar { display: flex; gap: .75rem; align-items: center; flex-wrap: wrap; }
.btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: .35rem;
  font-family: var(--ff-base); font-size: .82rem; font-weight: 600;
  cursor: pointer; letter-spacing: .2px;
  /* 统一尺寸：圆角、高度、内边距 */
  border-radius: var(--r-sm);
  height: 38px;
  padding: 0 22px;
  transition: all 180ms ease;
  user-select: none; white-space: nowrap;
  /* 统一阴影基准线 */
  box-shadow: 0 1px 3px rgba(0,0,0,.08);
}
.btn:active { transform: scale(.96); }

/* 主按钮：金色渐变实心 — 开始阅读 */
.btn--primary {
  background: linear-gradient(135deg, #CA8A04, #B07802);
  color: #fff;
  border: none;
  box-shadow: 0 2px 8px rgba(202,138,4,.28);
}
.btn--primary:hover {
  filter: brightness(1.06);
  box-shadow: 0 4px 14px rgba(202,138,4,.38);
}

/* 次级按钮：浅色描边 — 收藏 / 关注（未激活态） */
.btn--secondary {
  background: #FAF8F6;
  color: #555;
  border: 1px solid var(--border-light);
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.btn--secondary:hover {
  background: #F5F2EE;
  border-color: #D5CFC4;
  color: var(--ink);
  box-shadow: 0 2px 6px rgba(0,0,0,.09);
}

/* 收藏激活态：金色描边 + 浅金底 */
.btn--secondary.active {
  border-color: var(--accent);
  color: var(--accent);
  background: rgba(202,138,4,.06);
  box-shadow: 0 1px 4px rgba(202,138,4,.12);
}
.btn--secondary.active:hover {
  background: rgba(202,138,4,.10);
}

/* 关注激活态：绿色描边 + 浅绿底 */
.btn--secondary.followed {
  border-color: #22C55E;
  color: #22C55E;
  background: rgba(34,197,94,.05);
  box-shadow: 0 1px 4px rgba(34,197,94,.10);
}
.btn--secondary.followed:hover {
  background: rgba(34,197,94,.10);
}

.btn:disabled { opacity: .45; cursor: not-allowed; box-shadow: none; }

.icon-pop-enter-active { transition: all .25s ease; }
.icon-pop-leave-active { transition: all .12s ease-in; }
.icon-pop-enter-from { opacity: 0; transform: scale(.2); }
.icon-pop-leave-to { opacity: 0; transform: scale(1.3); }

/* ==================== 统一区块标题 ====================
   修复：字号统一 ≥ 12px，letter-spacing 收紧至合理范围。 */
.sec-head { display: flex; align-items: center; gap: .5rem; margin-bottom: .85rem; }
.sec-icon { color: var(--accent); opacity: .78; flex-shrink: 0; }
.sec-title {
  font-family: var(--ff-base); font-size: .9rem; font-weight: 600;
  color: var(--ink); letter-spacing: 1px; white-space: nowrap;
}
.sec-badge {
  font-size: .75rem; color: var(--muted); background: var(--border-light);
  padding: 1px 8px; border-radius: 20px; letter-spacing: .2px;
}

/* ==================== 通用卡片容器 ====================
   三大模块共用样式，浅底色+细边框+圆角 */
.sec-card {
  background: var(--card-alt); border: 1px solid var(--border-light);
  border-radius: var(--r-sm); padding: 1.15rem 1.25rem;
  margin-bottom: 1.25rem;
}

/* ==================== 内容简介 ==================== */
.desc-text {
  color: #555; line-height: 1.78; font-size: .85rem;
  font-family: var(--ff-base); letter-spacing: .2px;
}
.desc-body { overflow: hidden; transition: max-height .28s ease; max-height: 9999px; }
.desc-body.collapsed { max-height: 4.5em; position: relative; }
.desc-body.collapsed::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2.2em;
  background: linear-gradient(to bottom, transparent, var(--card-alt));
}
.expand-btn {
  display: inline-flex; align-items: center; gap: .25rem;
  margin-top: .5rem; background: none; border: none;
  color: var(--accent); font-size: .78rem; cursor: pointer;
  font-family: var(--ff-base); letter-spacing: .2px; padding: 0; transition: opacity .15s;
}
.expand-btn:hover { opacity: .65; }

/* ==================== 章节目录（横向按钮流式布局）====================
   设计目的：放弃垂直列表，改为类似标签云/小说APP目录的横向紧凑按钮布局。
   每章一个固定宽高的圆角按钮，flex-wrap 自动换行。
   长标题用 text-overflow:ellipsis 截断，hover 时通过 title 属性显示完整名。 */
.chapter-grid { display: flex; flex-wrap: wrap; gap: 8px; }

.ch-btn {
  display: inline-flex; align-items: center; gap: 4px;
  width: 80px; height: 34px; padding: 0 7px;
  background: #FAF8F6; border: 1px solid var(--border-light);
  border-radius: var(--r-sm); cursor: pointer;
  font-family: var(--ff-base); font-size: .76rem; color: var(--ink);
  transition: all 180ms ease; overflow: hidden;
  white-space: nowrap; text-overflow: ellipsis;
}
.ch-btn:hover {
  background: var(--accent-light); border-color: rgba(202,138,4,.3);
  color: var(--accent); box-shadow: 0 1px 6px rgba(202,138,4,.1);
  transform: translateY(-1px);
}
.ch-btn:active { transform: scale(.96); }
/* 修复：strong 最小字号 .75rem = 12px */
.ch-btn strong { font-size: .75rem; font-weight: 700; color: var(--muted); opacity: .65; flex-shrink: 0; }
.ch-btn:hover strong { color: var(--accent); }
.ch-btn span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; max-width: 46px; font-weight: 500; }
.ch-btn.read { background: #F4F2EE; border-color: #EBE7DE; color: #AAA5A0; }
.ch-btn.read strong { color: #C4C0BA; }
.ch-btn.read:hover { background: var(--accent-light); border-color: rgba(202,138,4,.3); color: var(--accent); }

.comment-form {
  background: #FEFCFA; border: 1px solid var(--border-light);
  border-radius: var(--r-sm); padding: 1rem 1.25rem; margin-bottom: 1rem;
}

.comment-input {
  width: 100%; border: 1px solid var(--border); background: #FFFDFB;
  padding: 10px 12px; font-family: var(--ff-base); font-size: .85rem;
  line-height: 1.65; border-radius: var(--r-sm); outline: none;
  resize: vertical; box-sizing: border-box; transition: border-color .15s;
}
.comment-input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(202,138,4,.06); }
.comment-actions { display: flex; align-items: center; justify-content: flex-end; gap: 10px; margin-top: 8px; }
.counter { font-size: .75rem; color: #BBB; }
.comment-submit {
  background: linear-gradient(135deg, #B8860B, #9A7209); color: #fff;
  border: none; padding: 7px 20px; font-size: .82rem; font-weight: 600;
  border-radius: var(--r-sm); cursor: pointer; font-family: var(--ff-base);
  letter-spacing: .3px; box-shadow: 0 2px 6px rgba(184,134,11,.24);
  transition: box-shadow .18s;
}
.comment-submit:hover { box-shadow: 0 3px 10px rgba(184,134,11,.36); }
.comment-submit:disabled { opacity: .38; cursor: not-allowed; box-shadow: none; }

.comment-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.comment-item {
  background: #FEFCFA; border: 1px solid var(--border-light);
  border-radius: var(--r-sm); padding: 1rem 1.15rem;
  display: flex; gap: 10px; transition: box-shadow .15s;
}
.comment-item:hover { box-shadow: var(--shadow-sm); }
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #CA8A04, #A87403);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: .82rem; flex-shrink: 0;
}
.comment-body { flex: 1; min-width: 0; }
.comment-head { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; font-size: .82rem; flex-wrap: wrap; }
.comment-user { font-weight: 600; color: var(--ink); }
.comment-del {
  background: none; border: none; color: #CCC; font-size: 1rem;
  cursor: pointer; padding: 1px 5px; border-radius: 3px;
  line-height: 1; transition: color .15s; margin-left: 4px; font-family: system-ui;
}
.comment-del:hover { color: #E74C3C; background: rgba(231,76,60,.05); }
.comment-text { margin: 0; color: #333; font-size: .85rem; line-height: 1.72; font-family: var(--ff-base); white-space: pre-wrap; word-break: break-word; }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 2rem 0; gap: .4rem; color: #BBB5AC; font-size: .85rem;
}
.empty-state p { margin: 0; }
.empty-state--cmt { padding: 2.5rem 0; }
.empty-title { font-size: .88rem; color: #888; font-weight: 500; margin: 0; }
.empty-hint { font-size: .78rem; color: #AAA; margin: 0; }

/* ==================== 加载态骨架 ==================== */
.loading-state { padding: 1.5rem 0; }
.skeleton-hero { width: 100%; height: 228px; border-radius: var(--r-md); margin-bottom: 1.25rem; overflow: hidden; }
.sk-block { width: 100%; height: 100%; background: linear-gradient(90deg,#f0ede8 25%,#e8e5df 50%,#f0ede8 75%); background-size: 200% 100%; animation: sk-shimmer 1.4s infinite; border-radius: var(--r-md); }
@keyframes sk-shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
.skeleton-info { display: flex; gap: 1.5rem; }
.sk-cover { width: 140px; height: 195px; border-radius: var(--r-sm); background: linear-gradient(90deg,#f0ede8 25%,#e8e5df 50%,#f0ede8 75%); background-size: 200% 100%; animation: sk-shimmer 1.4s infinite; flex-shrink: 0; }
.sk-meta { flex: 1; display: flex; flex-direction: column; gap: .7rem; padding-top: .3rem; }
.sk-line { border-radius: 4px; background: linear-gradient(90deg,#f0ede8 25%,#e8e5df 50%,#f0ede8 75%); background-size: 200% 100%; animation: sk-shimmer 1.4s infinite; }

/* ==================== 错误态 ==================== */
.error-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 70px 0; gap: .75rem; }
.error-icon { color: var(--border); }
.error-text { font-size: .88rem; color: var(--muted); letter-spacing: .2px; }
.btn-retry {
  display: inline-flex; align-items: center; gap: .35rem;
  background: transparent; border: 1px solid var(--border);
  color: var(--ink); font-size: .82rem; padding: 7px 20px;
  border-radius: var(--r-sm); cursor: pointer; letter-spacing: .2px; transition: var(--t);
}
.btn-retry:hover { border-color: var(--ink); background: var(--ink); color: #FDFBF7; }

.site-footer {
  text-align: center; padding: 1.5rem;
  color: #AAA; font-family: var(--ff-base);
  font-size: .78rem; letter-spacing: .5px;
  border-top: 1px solid var(--border-light); margin-top: 1.5rem;
}

/* ==================== 评分展示区 ==================== */
.rating-display {
  display: flex; align-items: center; gap: 14px;
  margin-top: .6rem;
  padding: 10px 14px;
  background: linear-gradient(135deg, #FFFBF0, #FFF8E8);
  border: 1px solid rgba(202,138,4,.15);
  border-radius: var(--r-sm);
  cursor: pointer;
  transition: all 180ms ease;
}
.rating-display:hover {
  border-color: rgba(202,138,4,.35);
  box-shadow: 0 2px 8px rgba(202,138,4,.08);
}
.rd-score { flex-shrink: 0; }
.rd-num {
  font-family: 'Georgia', serif; font-size: 1.6rem; font-weight: 700;
  color: var(--accent); line-height: 1;
}
.rd-info { display: flex; flex-direction: column; gap: 2px; }
.rd-stars-static { display: flex; gap: 2px; }
.rss-star {
  font-size: .82rem; color: #DDD3C4; line-height: 1; transition: color .12s;
}
.rss-star.on { color: var(--accent); }
.rd-count { font-size: .72rem; color: #AAA; letter-spacing: .2px; }
.rd-hint {
  font-size: .7rem; color: var(--accent); opacity: .65;
  transition: opacity .15s;
}
.rating-display:hover .rd-hint { opacity: 1; }

/* ==================== 评分弹窗 ==================== */
.rating-dialog :deep(.el-dialog) {
  border-radius: 10px !important;
  overflow: hidden;
}
.rating-dialog :deep(.el-dialog__header) {
  padding: 18px 22px 12px;
  border-bottom: 1px solid #EEE9E1;
}
.rating-dialog :deep(.el-dialog__title) {
  font-family: var(--ff-base); font-size: .95rem; font-weight: 600;
  color: var(--ink); letter-spacing: .5px;
}
.rating-dialog :deep(.el-dialog__body) { padding: 24px 22px 16px; }
.rating-dialog :deep(.el-dialog__footer) { padding: 12px 22px 20px; }

.rdlg-body { text-align: center; }
.rdlg-book {
  font-family: var(--ff-serif); font-size: 1.05rem; font-weight: 600;
  color: var(--ink); margin-bottom: 16px; letter-spacing: .5px;
}
.rdlg-stars { display: flex; justify-content: center; gap: 8px; margin-bottom: 10px; }
.rdlg-star {
  font-size: 32px; color: #D8D2C4; cursor: pointer;
  transition: color .12s, transform .15s; user-select: none;
  line-height: 1;
}
.rdlg-star:hover { transform: scale(1.15); }
.rdg-star.hover,
.rdlg-star.on { color: var(--accent); }
.rdlg-label {
  font-size: .85rem; color: var(--muted); margin-bottom: 4px;
}
.rdlg-old { font-size: .75rem; color: #AAA; margin-top: 4px; }

/* ==================== 响应式 ==================== */

@media (max-width: 1024px) {
  .content-wrapper { padding: 1.25rem; }
}

@media (max-width: 768px) {
  .header-inner { padding: 0 1.15rem; height: 50px; }
  .header-left { gap: .8rem; }
  .breadcrumb { display: none; }
  .main-content { padding: 56px 1.15rem 0; }

  .hero-section { height: 200px; margin-top: .35rem; margin-bottom: 1rem; border-radius: var(--r-sm); }
  .hero-cover-frame { width: 76px; height: 106px; }
  .hero-title { letter-spacing: 1.5px; }
  .tag { font-size: .72rem; padding: 2px 7px; }

  .content-wrapper { padding: 1rem; border-radius: var(--r-sm); }
  .info-layout { flex-direction: column; gap: 1rem; align-items: center; }
  .cover-card { width: 120px; }
  .side-cover { width: 120px; height: 168px; }
  .info-right { align-items: stretch; width: 100%; gap: .7rem; }
  .stats-row {
    flex-wrap: wrap; justify-content: center; gap: 4px;
    height: auto; padding: .6rem .75rem;
  }
  .stat-item { padding: .3rem .5rem; }
  .stat-divider { display: none; }
  .action-bar { justify-content: center; }
  .btn { padding: 7px 14px; font-size: .8rem; }

  .sec-card { padding: 1rem; margin-bottom: 1rem; }
  .sec-head { margin-bottom: .7rem; }
  .sec-title { font-size: .85rem; letter-spacing: .8px; }

  .chapter-grid { gap: 7px; }
  .ch-btn { width: calc((100% - 14px) / 4); height: 36px; font-size: .74rem; }
}

@media (max-width: 420px) {
  .header-inner { padding: 0 .9rem; }
  .logo { font-size: 1.05rem; letter-spacing: 1.5px; }
  .main-content { padding: 54px .9rem 0; }
  .hero-section { height: 180px; }
  .hero-cover-frame { width: 66px; height: 92px; }
  .content-wrapper { padding: .85rem; }

  .stats-row { gap: 3px; padding: .5rem .6rem; }
  .action-bar { gap: .45rem; }
  .btn { padding: 6px 11px; font-size: .78rem; }

  .chapter-grid { gap: 6px; }
  .ch-btn { width: calc((100% - 12px) / 3); height: 34px; font-size: .73rem; padding: 0 5px; }
  .ch-btn span { max-width: 34px; }
}
</style>
