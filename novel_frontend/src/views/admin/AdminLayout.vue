<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isCollapse = ref(false)
const activeMenu = computed(() => route.path)

const menuItems = [
  { index: '/admin', title: '仪表盘', icon: 'Odometer' },
  { index: '/admin/advertisements', title: '广告管理', icon: 'Promotion' },
  { index: '/admin/announcements', title: '公告管理', icon: 'Bell' },
  { index: '/admin/books', title: '书籍管理', icon: 'Notebook' },
  { index: '/admin/review', title: '新书审核', icon: 'Select' },
  { index: '/admin/categories', title: '分类管理', icon: 'FolderOpened' },
]

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const userInfo = computed(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
})

const username = computed(() => {
  const u = userInfo.value
  return u?.real_name || u?.pen_name || u?.nickname || u?.username || '管理员'
})

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && (item.meta as any).title)
  return matched.map(item => ({
    title: ((item.meta as any).title as string) || '未知',
    path: item.path,
  }))
})

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/admin')
      break
    case 'logout':
      localStorage.removeItem('user')
      router.push('/login')
      break
  }
}
</script>

<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: isCollapse }">
      <div class="sidebar-logo">
        <div class="logo-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" class="logo-svg">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" stroke="currentColor" stroke-width="1.8"/>
            <line x1="9" y1="7" x2="16" y2="7" stroke="currentColor" stroke-width="1.3" opacity="0.6"/>
            <line x1="9" y1="11" x2="14" y2="11" stroke="currentColor" stroke-width="1.3" opacity="0.6"/>
          </svg>
        </div>
        <transition name="logo-text-fade">
          <span v-show="!isCollapse" class="logo-text">墨香书阁</span>
        </transition>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :router="false"
        @select="handleMenuSelect"
        class="sidebar-menu"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
          class="menu-item-custom"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <router-link to="/" class="back-to-site">
          <el-icon><Monitor /></el-icon>
          <transition name="logo-text-fade">
            <span v-show="!isCollapse">返回前台</span>
          </transition>
        </router-link>
      </div>
    </aside>

    <!-- Main Area -->
    <div class="main-area">
      <!-- Header -->
      <header class="top-header">
        <div class="header-left">
          <button class="collapse-btn" @click="toggleCollapse">
            <el-icon :size="18"><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </button>
          <el-breadcrumb separator="/" class="breadcrumb-nav">
            <el-breadcrumb-item :to="{ path: '/admin' }">控制台</el-breadcrumb-item>
            <el-breadcrumb-item v-for="(crumb, idx) in breadcrumbs" :key="idx">
              {{ crumb.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-dropdown-trigger">
              <div class="user-avatar">
                <el-icon :size="18"><UserFilled /></el-icon>
              </div>
              <span class="user-name">{{ username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="admin-dropdown-menu">
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Content -->
      <main class="content-area">
        <router-view v-slot="{ Component, route: r }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="r.path" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

.admin-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #020617;
  color: #F8FAFC;
  font-family: 'Fira Sans', system-ui, -apple-system, sans-serif;
  overflow: hidden;
}

/* ===== SIDEBAR ===== */
.sidebar {
  width: 250px;
  min-width: 250px;
  height: 100vh;
  background: #0F172A;
  border-right: 1px solid rgba(30, 41, 59, 0.8);
  display: flex;
  flex-direction: column;
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(34, 197, 94, 0.15),
    transparent
  );
  pointer-events: none;
}

/* Logo Area */
.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(30, 41, 59, 0.6);
  flex-shrink: 0;
  position: relative;
}

.logo-icon-wrap {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(34, 197, 94, 0.35);
}

.logo-svg {
  width: 18px;
  height: 18px;
  color: #fff;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.5px;
  white-space: nowrap;
  text-shadow: 0 0 20px rgba(34, 197, 94, 0.25);
  background: linear-gradient(135deg, #F8FAFC 0%, #94A3B8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Menu */
.sidebar-menu {
  flex: 1;
  border-right: none !important;
  background: transparent !important;
  padding: 12px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar-menu::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.2);
  border-radius: 4px;
}

.sidebar-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.35);
}

:deep(.el-menu) {
  background: transparent !important;
  border-right: none !important;
}

:deep(.menu-item-custom) {
  height: 44px !important;
  margin: 3px 0 !important;
  border-radius: 10px !important;
  color: #94A3B8 !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative;
  overflow: hidden;
}

:deep(.menu-item-custom .el-icon) {
  font-size: 17px !important;
  transition: all 0.2s ease !important;
}

:deep(.menu-item-custom:hover) {
  background: rgba(30, 41, 59, 0.65) !important;
  color: #F8FAFC !important;
}

:deep(.menu-item-custom.is-active) {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.06) 100%) !important;
  color: #22C55E !important;
  font-weight: 600;
  box-shadow: inset 0 0 0 1px rgba(34, 197, 94, 0.2), 0 2px 8px rgba(34, 197, 94, 0.08);
}

:deep(.menu-item-custom.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 22px;
  background: #22C55E;
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

:deep(.menu-item-custom.is-active .el-icon) {
  color: #22C55E !important;
  filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.4));
}

/* Footer */
.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid rgba(30, 41, 59, 0.6);
  flex-shrink: 0;
}

.back-to-site {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  color: #94A3B8;
  text-decoration: none;
  font-size: 13.5px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.back-to-site:hover {
  background: rgba(30, 41, 59, 0.55);
  color: #F8FAFC;
}

.back-to-site .el-icon {
  font-size: 16px;
}

/* ===== MAIN AREA ===== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
  background: #020617;
}

/* ===== HEADER ===== */
.top-header {
  height: 56px;
  min-height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #0F172A;
  border-bottom: 1px solid rgba(30, 41, 59, 0.7);
  position: relative;
  z-index: 5;
  flex-shrink: 0;
  backdrop-filter: blur(12px);
}

.top-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(34, 197, 94, 0.08),
    transparent
  );
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: rgba(30, 41, 59, 0.45);
  color: #94A3B8;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
}

.collapse-btn:hover {
  background: rgba(30, 41, 59, 0.75);
  color: #F8FAFC;
  border-color: rgba(34, 197, 94, 0.2);
}

.breadcrumb-nav {
  --el-text-color-regular: #94A3B8;
}

:deep(.breadcrumb-nav .el-breadcrumb__inner) {
  color: #94A3B8 !important;
  font-size: 13px;
  transition: color 0.2s ease;
}

:deep(.breadcrumb-nav .el-breadcrumb__inner:hover) {
  color: #22C55E !important;
}

:deep(.breadcrumb-nav .el-breadcrumb__separator) {
  color: #334155 !important;
}

:deep(.breadcrumb-nav .el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #F8FAFC !important;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.user-dropdown-trigger:hover {
  background: rgba(30, 41, 59, 0.55);
  border-color: rgba(34, 197, 94, 0.15);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.25);
}

.user-name {
  font-size: 13.5px;
  font-weight: 500;
  color: #F8FAFC;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 12px;
  color: #64748B;
  transition: transform 0.2s ease;
}

/* ===== CONTENT ===== */
.content-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  position: relative;
}

.content-area::-webkit-scrollbar {
  width: 6px;
}

.content-area::-webkit-scrollbar-track {
  background: transparent;
}

.content-area::-webkit-scrollbar-thumb {
  background: rgba(30, 41, 59, 0.6);
  border-radius: 6px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: rgba(51, 65, 85, 0.8);
}

/* ===== TRANSITIONS ===== */
.logo-text-fade-enter-active,
.logo-text-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.logo-text-fade-enter-from,
.logo-text-fade-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ===== DROPDOWN OVERRIDES ===== */
:deep(.admin-dropdown-menu) {
  background: #0F172A !important;
  border: 1px solid #1E293B !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(34, 197, 94, 0.05) !important;
  padding: 6px !important;
}

:deep(.admin-dropdown-menu .el-dropdown-menu__item) {
  color: #94A3B8 !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 13px !important;
  transition: all 0.15s ease !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}

:deep(.admin-dropdown-menu .el-dropdown-menu__item:hover) {
  background: rgba(34, 197, 94, 0.1) !important;
  color: #22C55E !important;
}

:deep(.admin-dropdown-menu .el-dropdown-menu__item .el-icon) {
  font-size: 15px !important;
}

:deep(.admin-dropdown-menu .el-dropdown-menu__item--divided) {
  border-top-color: #1E293B !important;
  margin-top: 4px !important;
  padding-top: 8px !important;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .sidebar {
    position: absolute;
    z-index: 100;
    transform: translateX(-100%);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .sidebar:not(.collapsed) {
    width: 250px;
  }

  .user-name {
    display: none;
  }
}
</style>
