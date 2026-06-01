<template>
  <div class="uc-root">
    <header class="uc-header">
      <div class="uc-header__inner">
        <h1 class="uc-logo" @click="goHome">墨香书阁</h1>
        <nav class="uc-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/user" class="active">个人中心</router-link>
        </nav>
        <div class="uc-header__actions">
          <span class="uc-header__user">{{ userInfo.username }}</span>
          <button class="uc-header__logout" @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <main class="uc-main">
      <section class="uc-hero">
        <div class="uc-hero__inner">
          <div class="uc-hero__avatar-wrap">
            <div class="uc-hero__avatar-ring">
              <div class="uc-hero__avatar">
                <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.username" />
                <span v-else class="uc-hero__avatar-letter">{{ userInfo.username?.charAt(0).toUpperCase() }}</span>
              </div>
            </div>
            <div class="uc-hero__vip" :class="{ 'is-vip': userInfo.is_vip }">
              <svg v-if="userInfo.is_vip" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>
              {{ userInfo.is_vip ? 'VIP' : '普通会员' }}
            </div>
          </div>
          <div class="uc-hero__info">
            <h2 class="uc-hero__name">{{ userInfo.username }}</h2>
            <p class="uc-hero__motto">「 读书破万卷，下笔如有神 」</p>
            <div class="uc-hero__stats">
              <div class="uc-stat">
                <span class="uc-stat__num">{{ favorites.length }}</span>
                <span class="uc-stat__lbl">收藏</span>
              </div>
              <div class="uc-stat__sep"></div>
              <div class="uc-stat">
                <span class="uc-stat__num">{{ readingHistory.length }}</span>
                <span class="uc-stat__lbl">阅读</span>
              </div>
              <div class="uc-stat__sep"></div>
              <div class="uc-stat">
                <span class="uc-stat__num">{{ formatDays(userInfo.created_at) }}</span>
                <span class="uc-stat__lbl">注册天</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div class="uc-layout">
        <aside class="uc-sidenav">
          <button
            v-for="tab in tabList"
            :key="tab.name"
            class="uc-sidenav__item"
            :class="{ active: activeTab === tab.name }"
            @click="activeTab = tab.name"
          >
            <span class="uc-sidenav__icon" v-html="tab.svg"></span>
            <span class="uc-sidenav__label">{{ tab.label }}</span>
          </button>
        </aside>

        <div class="uc-content">
          <div v-show="activeTab === 'profile'" class="uc-pane">
            <div class="uc-pane__header">
              <span class="uc-pane__title">个人信息</span>
              <div class="uc-pane__actions">
                <button class="uc-btn-edit" @click="showEditDialog">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  编辑资料
                </button>
                <button class="uc-btn-edit" @click="pwdDialogVisible = true">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                  修改密码
                </button>
              </div>
            </div>
            <div class="uc-info-list">
              <div class="uc-info-row">
                <span class="uc-info__label">用户名</span>
                <span class="uc-info__value">{{ userInfo.username || '—' }}</span>
              </div>
              <div class="uc-info-row">
                <span class="uc-info__label">邮　箱</span>
                <span class="uc-info__value" :class="{ 'is-empty': !userInfo.email }">{{ userInfo.email || '未设置' }}</span>
              </div>
              <div class="uc-info-row">
                <span class="uc-info__label">注册时间</span>
                <span class="uc-info__value">{{ formatDate(userInfo.created_at) || '—' }}</span>
              </div>
              <div class="uc-info-row">
                <span class="uc-info__label">会员等级</span>
                <span class="uc-info__value">
                  <span class="uc-membership" :class="{ 'is-vip': userInfo.is_vip }">
                    {{ userInfo.is_vip ? 'VIP 会员' : '普通会员' }}
                  </span>
                </span>
              </div>
            </div>
          </div>

          <div v-show="activeTab === 'favorites'" class="uc-pane">
            <div class="uc-pane__header">
              <span class="uc-pane__title">我的书架</span>
              <div class="uc-pane__actions" v-if="favorites.length > 0">
                <span class="uc-count">{{ favorites.length }} 本</span>
                <select class="uc-select" v-model="favoriteOrder" @change="handleFavoriteSort">
                  <option value="created_at">按收藏时间</option>
                  <option value="updated_at">按更新时间</option>
                  <option value="title">按书名</option>
                </select>
              </div>
            </div>
            <div v-if="favorites.length > 0" class="uc-shelf">
              <div
                v-for="fav in favorites"
                :key="fav.id"
                class="uc-book"
                @click="goToDetail(fav.novel)"
              >
                <div class="uc-book__cover-wrap">
                  <div class="uc-book__spine"></div>
                  <img
                    v-lazy="fav.novel_cover"
                    :alt="fav.novel_title"
                    class="uc-book__cover"
                    @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'"
                  />
                  <div class="uc-book__mask">
                    <span class="uc-book__mask-text">阅读</span>
                  </div>
                  <button class="uc-book__remove" @click.stop="cancelFavorite(fav.id)" title="取消收藏">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
                <div class="uc-book__meta">
                  <p class="uc-book__title">{{ fav.novel_title }}</p>
                  <p class="uc-book__author">{{ fav.novel_author }}</p>
                </div>
              </div>
            </div>
            <div v-else class="uc-empty">
              <svg class="uc-empty__icon" width="64" height="64" viewBox="0 0 64 64" fill="none">
                <rect x="8" y="16" width="20" height="32" rx="2" fill="#E8D5B0" stroke="#CA8A04" stroke-width="1"/>
                <rect x="22" y="12" width="20" height="32" rx="2" fill="#A07850" stroke="#8B6914" stroke-width="1"/>
                <rect x="36" y="18" width="20" height="32" rx="2" fill="#3D5A4A" stroke="#2A4035" stroke-width="1"/>
                <ellipse cx="32" cy="54" rx="24" ry="3" fill="#E0E0E0"/>
              </svg>
              <p class="uc-empty__title">书架还是空的</p>
              <p class="uc-empty__hint">去书库找几本喜欢的小说吧</p>
              <button class="uc-btn-gold" @click="goToNovels">浏览书库</button>
            </div>
          </div>

          <div v-show="activeTab === 'history'" class="uc-pane">
            <div class="uc-pane__header">
              <span class="uc-pane__title">阅读记录</span>
              <div class="uc-pane__actions" v-if="readingHistory.length > 0">
                <span class="uc-count">{{ readingHistory.length }} 条</span>
                <select class="uc-select" v-model="historyOrder" @change="handleHistorySort">
                  <option value="updated_at">按阅读时间</option>
                  <option value="novel">按小说名</option>
                </select>
              </div>
            </div>
            <div v-if="readingHistory.length > 0" class="uc-timeline">
              <div
                v-for="(item, index) in readingHistory"
                :key="item.id"
                class="uc-timeline__item"
              >
                <div class="uc-timeline__rail">
                  <div class="uc-timeline__dot"></div>
                  <div v-if="index < readingHistory.length - 1" class="uc-timeline__line"></div>
                </div>
                <div class="uc-timeline__card" @click="continueReading(item)">
                  <div class="uc-tl__cover">
                    <img
                      v-lazy="item.novel_cover || 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'"
                      :alt="item.novel_title"
                      @error="($event.target as HTMLImageElement).src = 'https://placehold.co/300x400/8B4513/FFFFFF?text=%E5%B0%81%E9%9D%A2'"
                    />
                  </div>
                  <div class="uc-tl__body">
                    <h4 class="uc-tl__title">{{ item.novel_title }}</h4>
                    <p class="uc-tl__chapter">读至 &nbsp;{{ item.chapter_title || '序章' }}</p>
                    <div class="uc-tl__progress">
                      <div class="uc-tl__bar">
                        <div class="uc-tl__fill" :style="{ width: calculateProgress(item) + '%' }"></div>
                      </div>
                      <span class="uc-tl__pct">{{ calculateProgress(item) }}%</span>
                    </div>
                    <p class="uc-tl__time">{{ formatDate(item.updated_at) }}</p>
                  </div>
                  <div class="uc-tl__actions">
                    <button class="uc-btn-sm uc-btn-sm--gold" @click.stop="continueReading(item)">继续读</button>
                    <button class="uc-btn-sm uc-btn-sm--ghost" @click.stop="deleteHistory(item.id)">删除</button>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="uc-empty">
              <svg class="uc-empty__icon" width="64" height="64" viewBox="0 0 64 64" fill="none">
                <rect x="12" y="8" width="28" height="40" rx="2" fill="#F5F1EA" stroke="#E0E0E0" stroke-width="1.5"/>
                <line x1="18" y1="16" x2="34" y2="16" stroke="#E0E0E0" stroke-width="1.5"/>
                <line x1="18" y1="22" x2="34" y2="22" stroke="#E0E0E0" stroke-width="1.5"/>
                <line x1="18" y1="28" x2="28" y2="28" stroke="#E0E0E0" stroke-width="1.5"/>
                <rect x="24" y="16" width="28" height="40" rx="2" fill="#FFFFFF" stroke="#CA8A04" stroke-width="1.5"/>
                <line x1="30" y1="24" x2="46" y2="24" stroke="#CA8A04" stroke-width="1"/>
                <line x1="30" y1="30" x2="46" y2="30" stroke="#E0E0E0" stroke-width="1"/>
                <line x1="30" y1="36" x2="40" y2="36" stroke="#E0E0E0" stroke-width="1"/>
              </svg>
              <p class="uc-empty__title">暂无阅读记录</p>
              <p class="uc-empty__hint">开始你的第一本小说之旅</p>
              <button class="uc-btn-gold" @click="goToNovels">开始阅读</button>
            </div>
          </div>

          <div v-show="activeTab === 'bookmarks'" class="uc-pane">
            <div class="uc-pane__header">
              <span class="uc-pane__title">我的书签</span>
              <span class="uc-count" v-if="bookmarks.length > 0">{{ bookmarks.length }} 个</span>
            </div>
            <div v-if="bookmarks.length > 0" class="uc-bookmark-list">
              <div
                v-for="bookmark in bookmarks"
                :key="bookmark.id"
                class="uc-bookmark"
                @click="goToBookmark(bookmark)"
              >
                <div class="uc-bookmark__icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>
                </div>
                <div class="uc-bookmark__body">
                  <h4 class="uc-bookmark__novel">{{ bookmark.novel_title }}</h4>
                  <p class="uc-bookmark__chapter">{{ bookmark.chapter_title }}</p>
                  <p class="uc-bookmark__note" v-if="bookmark.note">{{ bookmark.note }}</p>
                  <p class="uc-bookmark__time">{{ formatDate(bookmark.created_at) }}</p>
                </div>
                <div class="uc-bookmark__actions">
                  <button class="uc-btn-sm uc-btn-sm--gold" @click.stop="goToBookmark(bookmark)">跳转</button>
                  <button class="uc-btn-sm uc-btn-sm--ghost" @click.stop="deleteBookmark(bookmark.id)">删除</button>
                </div>
              </div>
            </div>
            <div v-else class="uc-empty">
              <svg class="uc-empty__icon" width="64" height="64" viewBox="0 0 64 64" fill="none">
                <path d="M48 56L32 44 16 56V12a4 4 0 014-4h24a4 4 0 014 4v44z" fill="#F5F1EA" stroke="#CA8A04" stroke-width="1.5"/>
                <line x1="24" y1="18" x2="40" y2="18" stroke="#E0E0E0" stroke-width="1.5"/>
                <line x1="24" y1="26" x2="40" y2="26" stroke="#E0E0E0" stroke-width="1.5"/>
              </svg>
              <p class="uc-empty__title">暂无书签</p>
              <p class="uc-empty__hint">在阅读页点击书签按钮添加</p>
              <button class="uc-btn-gold" @click="goToNovels">开始阅读</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="uc-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>

    <el-dialog v-model="editDialogVisible" title="编辑个人资料" width="480px" class="uc-dialog">
      <el-form :model="editForm" label-width="70px" class="uc-dialog__form">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" placeholder="输入用户名" />
        </el-form-item>
        <el-form-item label="头像">
          <el-input v-model="editForm.avatar" placeholder="输入头像 URL" />
        </el-form-item>
        <el-form-item label="邮　箱">
          <el-input v-model="editForm.email" placeholder="输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="输入手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="uc-dialog__footer">
          <button class="uc-btn-cancel" @click="editDialogVisible = false">取消</button>
          <button class="uc-btn-save" @click="handleUpdateProfile">保存</button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="pwdDialogVisible" title="修改密码" width="420px" class="uc-dialog">
      <el-form :model="pwdForm" label-width="80px" class="uc-dialog__form">
        <el-form-item label="旧密码">
          <el-input v-model="pwdForm.old_password" type="password" placeholder="输入当前密码" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="pwdForm.confirm_password" type="password" placeholder="再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="uc-dialog__footer">
          <button class="uc-btn-cancel" @click="pwdDialogVisible = false">取消</button>
          <button class="uc-btn-save" @click="handleChangePassword">确认修改</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authApi } from '../api'
import request from '../utils/request'

const router = useRouter()
const activeTab = ref('profile')
const userInfo = ref<any>({})
const favorites = ref<any[]>([])
const readingHistory = ref<any[]>([])
const bookmarks = ref<any[]>([])
const favoriteOrder = ref('created_at')
const historyOrder = ref('updated_at')
const editDialogVisible = ref(false)
const editForm = ref({
  username: '',
  avatar: '',
  email: '',
  phone: ''
})
const pwdDialogVisible = ref(false)
const pwdForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const tabList = [
  { name: 'profile', label: '个人信息', svg: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  { name: 'favorites', label: '我的书架', svg: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>' },
  { name: 'history', label: '阅读记录', svg: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>' },
  { name: 'bookmarks', label: '我的书签', svg: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z"/></svg>' },
]

const showEditDialog = () => {
  editForm.value = {
    username: userInfo.value.username || '',
    avatar: userInfo.value.avatar || '',
    email: userInfo.value.email || '',
    phone: userInfo.value.phone || ''
  }
  editDialogVisible.value = true
}

const handleUpdateProfile = async () => {
  try {
    await request.put('/auth/update_profile/', editForm.value)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadUserInfo()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleChangePassword = async () => {
  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  if (pwdForm.value.new_password.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
    ElMessage.warning('两次密码不一致')
    return
  }
  try {
    await authApi.changePassword({
      old_password: pwdForm.value.old_password,
      new_password: pwdForm.value.new_password,
    })
    ElMessage.success('密码修改成功，下次登录生效')
    pwdDialogVisible.value = false
    pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (err: any) {
    const data = err?.response?.data
    if (data) {
      const msg = Object.values(data).flat().join('; ')
      ElMessage.error(msg)
    } else {
      ElMessage.error('修改失败')
    }
  }
}

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
    const res: any = await request.get('/auth/me/')
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const loadFavorites = async () => {
  try {
    const res: any = await request.get('/favorites/', { params: { ordering: favoriteOrder.value } })
    favorites.value = res.results || []
  } catch (error) {
    console.error('获取收藏失败:', error)
  }
}

const handleFavoriteSort = () => {
  loadFavorites()
}

const loadReadingHistory = async () => {
  try {
    const res: any = await request.get('/reading-progress/', { params: { ordering: historyOrder.value } })
    readingHistory.value = res.results || []
  } catch (error) {
    console.error('获取阅读记录失败:', error)
  }
}

const handleHistorySort = () => {
  loadReadingHistory()
}

const deleteHistory = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此阅读记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.delete(`/reading-progress/${id}/`)
    ElMessage.success('已删除阅读记录')
    loadReadingHistory()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除阅读记录失败')
    }
  }
}

const loadBookmarks = async () => {
  try {
    const res: any = await request.get('/bookmarks/')
    bookmarks.value = res.results || []
  } catch (error) {
    console.error('获取书签失败:', error)
  }
}

const deleteBookmark = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此书签吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.delete(`/bookmarks/${id}/`)
    ElMessage.success('已删除书签')
    loadBookmarks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除书签失败')
    }
  }
}

const goToBookmark = (bookmark: any) => {
  if (bookmark.chapter) {
    router.push({ name: 'Reader', params: { id: bookmark.chapter } })
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
  const id = typeof novel === 'number' ? novel : novel?.id
  if (id) {
    router.push({ name: 'NovelDetail', params: { id } })
  }
}

const continueReading = (item: any) => {
  const chapterId = typeof item.chapter === 'number' ? item.chapter : item.chapter?.id
  const novelId = typeof item.novel === 'number' ? item.novel : item.novel?.id
  if (chapterId) {
    router.push({ name: 'Reader', params: { id: chapterId } })
  } else if (novelId) {
    router.push({ name: 'NovelDetail', params: { id: novelId } })
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
    await authApi.logout()
  } catch (error) {
    console.log('登出请求失败')
  }
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  ElMessage.success('已退出登录')
  router.push({ name: 'Home' })
}

onMounted(() => {
  if (!localStorage.getItem('user')) {
    router.push({ name: 'Login' })
    return
  }
  loadUserInfo()
  loadFavorites()
  loadReadingHistory()
  loadBookmarks()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.uc-root {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-dark: #A67C00;
  --border: #E0E0E0;
  --card-bg: #FFFFFF;

  min-height: 100vh;
  background: var(--paper-bg);
  color: var(--ink);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
}

.uc-header {
  background: var(--ink);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid var(--accent);
}

.uc-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.uc-logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  cursor: pointer;
  letter-spacing: 3px;
  user-select: none;
  flex-shrink: 0;
  margin: 0;
}

.uc-nav {
  display: flex;
  gap: 0.25rem;
  flex: 1;
}

.uc-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
  letter-spacing: 0.5px;
  cursor: pointer;
}

.uc-nav a:hover,
.uc-nav a.active {
  color: var(--accent);
  background: rgba(202, 138, 4, 0.1);
}

.uc-header__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.uc-header__user {
  color: #D1D5DB;
  font-size: 0.88rem;
}

.uc-header__logout {
  background: transparent;
  border: 1px solid #4B5563;
  color: #9CA3AF;
  font-size: 0.83rem;
  padding: 5px 14px;
  border-radius: 2px;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  transition: border-color 0.2s, color 0.2s;
}

.uc-header__logout:hover {
  border-color: #EF4444;
  color: #EF4444;
}

.uc-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 3rem;
}

.uc-hero {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-top: none;
  border-bottom: 2px solid var(--accent);
  margin-bottom: 2rem;
}

.uc-hero__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 0;
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.uc-hero__avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.uc-hero__avatar-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, var(--accent) 0%, #92600A 100%);
}

.uc-hero__avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #F3F0EC;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.uc-hero__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.uc-hero__avatar-letter {
  font-size: 2.2rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Noto Serif SC', serif;
}

.uc-hero__vip {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  background: #6B7280;
  color: #fff;
  font-size: 0.68rem;
  padding: 2px 10px;
  border-radius: 20px;
  white-space: nowrap;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.uc-hero__vip.is-vip {
  background: linear-gradient(90deg, var(--accent) 0%, #92600A 100%);
}

.uc-hero__info {
  flex: 1;
}

.uc-hero__name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 2px;
  margin: 0 0 0.3rem;
}

.uc-hero__motto {
  color: var(--muted);
  font-size: 0.88rem;
  font-style: italic;
  font-family: 'Noto Serif SC', serif;
  margin: 0 0 1.25rem;
  letter-spacing: 0.5px;
}

.uc-hero__stats {
  display: flex;
  align-items: center;
}

.uc-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 2rem 0 0;
}

.uc-stat__num {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Noto Serif SC', serif;
}

.uc-stat__lbl {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 2px;
}

.uc-stat__sep {
  width: 1px;
  height: 32px;
  background: var(--border);
  margin: 0 2rem 0 0;
}

.uc-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.uc-sidenav {
  width: 160px;
  flex-shrink: 0;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 3px;
  overflow: hidden;
  position: sticky;
  top: 80px;
}

.uc-sidenav__item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 14px 18px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--muted);
  font-family: 'Noto Sans SC', sans-serif;
  text-align: left;
  border-left: 3px solid transparent;
  transition: color 0.2s, background-color 0.2s, border-color 0.2s;
  letter-spacing: 0.5px;
}

.uc-sidenav__item:not(:last-child) {
  border-bottom: 1px solid var(--border);
}

.uc-sidenav__item:hover {
  color: var(--ink);
  background: #F9F7F3;
}

.uc-sidenav__item.active {
  color: var(--accent);
  background: #FFFBF0;
  border-left-color: var(--accent);
  font-weight: 500;
}

.uc-sidenav__icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.uc-sidenav__label {
  white-space: nowrap;
}

.uc-content {
  flex: 1;
  min-width: 0;
}

.uc-pane {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 2rem;
}

.uc-pane__header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.75rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.uc-pane__actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.uc-pane__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 2px;
  position: relative;
  padding-left: 12px;
  margin: 0;
}

.uc-pane__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: var(--accent);
  border-radius: 2px;
}

.uc-pane__actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.uc-btn-edit {
  margin-left: auto;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.83rem;
  padding: 5px 14px;
  border-radius: 2px;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: border-color 0.2s, color 0.2s;
}

.uc-btn-edit:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.uc-count {
  font-size: 0.8rem;
  color: var(--muted);
  background: #F3F0EC;
  padding: 3px 10px;
  border-radius: 20px;
  border: 1px solid var(--border);
}

.uc-select {
  font-size: 0.82rem;
  color: var(--muted);
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 2px;
  padding: 4px 8px;
  font-family: 'Noto Sans SC', sans-serif;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}

.uc-select:focus {
  border-color: var(--accent);
}

.uc-info-list {
  display: flex;
  flex-direction: column;
}

.uc-info-row {
  display: flex;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #F3F0EC;
  gap: 2rem;
}

.uc-info-row:last-child {
  border-bottom: none;
}

.uc-info__label {
  min-width: 70px;
  font-size: 0.88rem;
  color: var(--muted);
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 2px;
}

.uc-info__value {
  font-size: 0.92rem;
  color: var(--ink);
}

.uc-info__value.is-empty {
  color: #C9CDD4;
  font-style: italic;
}

.uc-membership {
  font-size: 0.8rem;
  padding: 3px 12px;
  border-radius: 2px;
  background: #F3F0EC;
  color: var(--muted);
  border: 1px solid var(--border);
}

.uc-membership.is-vip {
  background: #FFFBF0;
  color: var(--accent);
  border-color: rgba(202, 138, 4, 0.4);
}

.uc-shelf {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.uc-book {
  cursor: pointer;
}

.uc-book__cover-wrap {
  position: relative;
  height: 220px;
  border-radius: 2px 4px 4px 2px;
  overflow: hidden;
  box-shadow: 4px 4px 14px rgba(0, 0, 0, 0.18);
  transition: box-shadow 0.25s, transform 0.25s;
}

.uc-book:hover .uc-book__cover-wrap {
  box-shadow: 6px 8px 24px rgba(0, 0, 0, 0.28);
  transform: translateY(-3px);
}

.uc-book__spine {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 6px;
  background: linear-gradient(180deg, var(--accent) 0%, #92600A 100%);
  z-index: 2;
}

.uc-book__cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.uc-book__mask {
  position: absolute;
  inset: 0;
  background: rgba(26, 26, 26, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s;
}

.uc-book:hover .uc-book__mask {
  opacity: 1;
}

.uc-book__mask-text {
  color: #fff;
  font-size: 0.88rem;
  border: 1px solid rgba(255, 255, 255, 0.7);
  padding: 6px 20px;
  border-radius: 2px;
  letter-spacing: 2px;
  font-family: 'Noto Sans SC', sans-serif;
}

.uc-book__remove {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 26px;
  height: 26px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s, background-color 0.2s;
  z-index: 3;
}

.uc-book:hover .uc-book__remove {
  opacity: 1;
}

.uc-book__remove:hover {
  background: #EF4444;
}

.uc-book__meta {
  padding: 0.6rem 0.25rem 0;
}

.uc-book__title {
  font-size: 0.88rem;
  color: var(--ink);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0 0 0.2rem;
}

.uc-book__author {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0;
}

.uc-timeline {
  display: flex;
  flex-direction: column;
}

.uc-timeline__item {
  display: flex;
  gap: 1rem;
}

.uc-timeline__rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20px;
  flex-shrink: 0;
}

.uc-timeline__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid #FFFBF0;
  box-shadow: 0 0 0 2px var(--accent);
  flex-shrink: 0;
}

.uc-timeline__line {
  width: 1px;
  flex: 1;
  background: var(--border);
  margin-top: 6px;
  min-height: 20px;
}

.uc-timeline__card {
  flex: 1;
  display: flex;
  gap: 1.25rem;
  background: #F9F7F3;
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
}

.uc-timeline__card:hover {
  background: var(--card-bg);
  border-color: var(--accent);
}

.uc-tl__cover {
  width: 64px;
  height: 88px;
  flex-shrink: 0;
  border-radius: 2px 3px 3px 2px;
  overflow: hidden;
  box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.15);
}

.uc-tl__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.uc-tl__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.uc-tl__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 1px;
  margin: 0;
}

.uc-tl__chapter {
  font-size: 0.83rem;
  color: var(--muted);
  margin: 0;
}

.uc-tl__progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.uc-tl__bar {
  flex: 1;
  height: 4px;
  background: #E0D6CC;
  border-radius: 2px;
  overflow: hidden;
}

.uc-tl__fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent) 0%, #92600A 100%);
  border-radius: 2px;
  transition: width 0.3s;
}

.uc-tl__pct {
  font-size: 0.75rem;
  color: var(--muted);
  flex-shrink: 0;
  min-width: 32px;
  text-align: right;
}

.uc-tl__time {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin: 0;
}

.uc-tl__actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  justify-content: center;
  flex-shrink: 0;
}

.uc-btn-sm {
  padding: 6px 14px;
  border-radius: 2px;
  font-size: 0.8rem;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 0.5px;
  white-space: nowrap;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
  border: 1px solid transparent;
}

.uc-btn-sm--gold {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.uc-btn-sm--gold:hover {
  background: var(--accent-dark);
  border-color: var(--accent-dark);
}

.uc-btn-sm--ghost {
  background: transparent;
  color: #9CA3AF;
  border-color: var(--border);
}

.uc-btn-sm--ghost:hover {
  border-color: #EF4444;
  color: #EF4444;
}

.uc-bookmark-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.uc-bookmark {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: #F9F7F3;
  border: 1px solid var(--border);
  border-left: 3px solid var(--border);
  border-radius: 0 3px 3px 0;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.uc-bookmark:hover {
  border-left-color: var(--accent);
  background: var(--card-bg);
}

.uc-bookmark__icon {
  color: var(--accent);
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.uc-bookmark__body {
  flex: 1;
  min-width: 0;
}

.uc-bookmark__novel {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
  margin: 0 0 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.uc-bookmark__chapter {
  font-size: 0.83rem;
  color: var(--muted);
  margin: 0 0 0.2rem;
}

.uc-bookmark__note {
  font-size: 0.8rem;
  color: #9CA3AF;
  font-style: italic;
  margin: 0 0 0.2rem;
}

.uc-bookmark__time {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin: 0;
}

.uc-bookmark__actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.uc-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 0;
  gap: 0.6rem;
}

.uc-empty__icon {
  margin-bottom: 0.5rem;
  opacity: 0.7;
}

.uc-empty__title {
  font-size: 1rem;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
  margin: 0;
}

.uc-empty__hint {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0 0 1rem;
}

.uc-btn-gold {
  background: var(--accent);
  color: #fff;
  border: none;
  padding: 9px 28px;
  border-radius: 2px;
  font-size: 0.88rem;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 1px;
  transition: background-color 0.2s;
  box-shadow: 0 2px 8px rgba(202, 138, 4, 0.25);
}

.uc-btn-gold:hover {
  background: var(--accent-dark);
}

.uc-footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.83rem;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}

.uc-footer p {
  margin: 0;
}

.uc-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
  font-family: 'Noto Serif SC', serif;
}

.uc-dialog :deep(.el-dialog__title) {
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  color: var(--ink);
}

.uc-dialog__form :deep(.el-form-item__label) {
  font-family: 'Noto Serif SC', serif;
  color: var(--muted);
  letter-spacing: 1px;
}

.uc-dialog__form :deep(.el-input__wrapper) {
  border-radius: 2px;
  box-shadow: none;
  border: 1px solid var(--border);
  background: #F9F7F3;
  transition: border-color 0.2s;
}

.uc-dialog__form :deep(.el-input__wrapper:focus-within) {
  border-color: var(--accent);
}

.uc-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.uc-btn-cancel {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 8px 22px;
  border-radius: 2px;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.88rem;
  transition: border-color 0.2s, color 0.2s;
}

.uc-btn-cancel:hover {
  border-color: var(--ink);
  color: var(--ink);
}

.uc-btn-save {
  background: var(--accent);
  border: none;
  color: #fff;
  padding: 8px 22px;
  border-radius: 2px;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.88rem;
  transition: background-color 0.2s;
  box-shadow: 0 2px 6px rgba(202, 138, 4, 0.3);
}

.uc-btn-save:hover {
  background: var(--accent-dark);
}

@media (max-width: 1024px) {
  .uc-shelf {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .uc-layout {
    flex-direction: column;
  }

  .uc-sidenav {
    width: 100%;
    display: flex;
    position: static;
    overflow-x: auto;
  }

  .uc-sidenav__item {
    flex-direction: column;
    gap: 0.25rem;
    padding: 10px 18px;
    border-left: none;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
  }

  .uc-sidenav__item:not(:last-child) {
    border-bottom: 3px solid transparent;
    border-right: 1px solid var(--border);
  }

  .uc-sidenav__item.active {
    border-left-color: transparent;
    border-bottom-color: var(--accent);
  }

  .uc-hero__inner {
    gap: 1.5rem;
  }

  .uc-shelf {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 375px) {
  .uc-main {
    padding: 0 1rem 2rem;
  }

  .uc-header__inner {
    padding: 0 1rem;
  }

  .uc-nav {
    display: none;
  }

  .uc-hero__inner {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem 1rem;
  }

  .uc-hero__stats {
    justify-content: center;
  }

  .uc-shelf {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .uc-timeline__card {
    flex-direction: column;
  }

  .uc-tl__actions {
    flex-direction: row;
  }

  .uc-pane {
    padding: 1.25rem;
  }
}
</style>
