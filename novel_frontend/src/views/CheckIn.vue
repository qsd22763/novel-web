<template>
  <div class="ci-root">
    <header class="ci-header">
      <div class="ci-header__inner">
        <h1 class="ci-logo" @click="goHome">墨香书阁</h1>
        <nav class="ci-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/user">个人中心</router-link>
        </nav>
        <div class="ci-header__actions">
          <span class="ci-header__user">
            <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.username" class="ci-header__avatar" />
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            {{ userInfo.username }}
          </span>
          <button class="ci-header__logout" @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <main class="ci-main">
      <!-- 签到卡片 -->
      <section class="ci-card-section">
        <div class="ci-check-card">
          <div class="ci-check-card__top">
            <svg class="ci-check-card__icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <h2 class="ci-check-card__title">每日签到</h2>
            <p class="ci-check-card__subtitle">坚持阅读，积攒书香币</p>
          </div>

          <div class="ci-check-card__coins">
            <span class="ci-check-card__coins-label">当前余额</span>
            <span class="ci-check-card__coins-value">{{ totalCoins }}</span>
            <span class="ci-check-card__coins-unit">书香币</span>
          </div>

          <div class="ci-check-card__action">
            <template v-if="!checkedToday && !checkingIn">
              <button class="ci-btn-sign" @click="handleCheckIn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                立即签到
              </button>
              <p class="ci-check-card__hint">签到可获得 {{ config?.daily_reward || 10 }} 书香币</p>
            </template>
            <template v-else-if="checkingIn">
              <button class="ci-btn-sign ci-btn-sign--loading" disabled>
                <span class="ci-spinner"></span>
                签到中...
              </button>
            </template>
            <template v-else>
              <div class="ci-checked">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>今日已签到</span>
              </div>
            </template>
          </div>

          <div class="ci-check-card__streak">
            <div class="ci-streak-item">
              <span class="ci-streak-num">{{ consecutiveDays }}</span>
              <span class="ci-streak-lbl">连续签到天数</span>
            </div>
            <div class="ci-streak-sep"></div>
            <div class="ci-streak-item">
              <span class="ci-streak-num">{{ checkedCount }}</span>
              <span class="ci-streak-lbl">本月已签次数</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 近30天签到日历 -->
      <section class="ci-calendar-section">
        <h3 class="ci-section-title">
          <span class="ci-section-title__bar"></span>
          近30天签到记录
        </h3>
        <div class="ci-calendar">
          <div class="ci-calendar__weekdays">
            <span v-for="wd in weekDays" :key="wd" class="ci-weekday">{{ wd }}</span>
          </div>
          <div class="ci-calendar__grid">
            <div
              v-for="(day, idx) in calendarDays"
              :key="idx"
              class="ci-day"
              :class="{
                'ci-day--checked': day.checked,
                'ci-day--today': day.isToday,
                'ci-day--empty': day.empty,
                'ci-day--future': day.isFuture,
              }"
            >
              <span v-if="!day.empty" class="ci-day__num">{{ day.date }}</span>
              <span v-if="day.checked && !day.empty" class="ci-day__dot"></span>
            </div>
          </div>
        </div>
      </section>

      <!-- 签到规则 -->
      <section class="ci-rules-section">
        <h3 class="ci-section-title">
          <span class="ci-section-title__bar"></span>
          签到规则
        </h3>
        <ul class="ci-rules-list">
          <li class="ci-rule">
            <span class="ci-rule__icon">&#9670;</span>
            每日签到可获得 <strong>{{ config?.daily_reward || 10 }}</strong> 书香币
          </li>
          <li class="ci-rule">
            <span class="ci-rule__icon">&#9670;</span>
            连续签到有额外奖励：连续7天额外奖励 <strong>{{ config?.weekly_bonus || 30 }}</strong> 书香币；连续30天额外奖励 <strong>{{ config?.monthly_bonus || 200 }}</strong> 书香币
          </li>
          <li class="ci-rule">
            <span class="ci-rule__icon">&#9670;</span>
            漏签不可补签，请每日坚持签到以保持连续记录
          </li>
          <li class="ci-rule">
            <span class="ci-rule__icon">&#9670;</span>
            书香币可用于兑换会员、解锁付费章节等特权
          </li>
        </ul>
      </section>
    </main>

    <footer class="ci-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { checkinApi } from '../api'
import request from '../utils/request'

const router = useRouter()

// 状态数据
const checkedToday = ref(false)
const consecutiveDays = ref(0)
const totalCoins = ref(0)
const config = ref<any>({})
const records = ref<string[]>([])
const checkingIn = ref(false)
const userInfo = ref<any>({})

const weekDays = ['一', '二', '三', '四', '五', '六', '日']

const checkedCount = computed(() => records.value.length)

// 构建近30天日历数据
const calendarDays = computed(() => {
  const days: any[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // 从30天前开始
  const startDate = new Date(today)
  startDate.setDate(startDate.getDate() - 29)

  // 计算起始日期是周几（0=周日），调整为周一为起始
  let startWeekDay = startDate.getDay()
  startWeekDay = startWeekDay === 0 ? 6 : startWeekDay - 1

  // 填充前面的空白格子
  for (let i = 0; i < startWeekDay; i++) {
    days.push({ date: '', empty: true, checked: false, isToday: false, isFuture: false })
  }

  // 填充30天
  for (let i = 0; i < 30; i++) {
    const d = new Date(startDate)
    d.setDate(d.getDate() + i)
    const dateStr = formatDateKey(d)
    const isToday = d.getTime() === today.getTime()
    const isFuture = d > today
    const checked = records.value.includes(dateStr) || isToday && checkedToday.value

    days.push({
      date: d.getDate(),
      empty: false,
      checked,
      isToday,
      isFuture,
      fullDate: dateStr,
    })
  }

  return days
})

function formatDateKey(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 加载签到状态
const loadStatus = async () => {
  try {
    const res: any = await checkinApi.status()
    checkedToday.value = res.checked_today ?? false
    consecutiveDays.value = res.consecutive_days ?? 0
    totalCoins.value = res.total_coins ?? 0
    config.value = res.config ?? {}
  } catch (error) {
    console.error('获取签到状态失败:', error)
  }
}

// 加载签到记录
const loadRecords = async () => {
  try {
    const res: any = await checkinApi.records(30)
    records.value = Array.isArray(res) ? res : (res.results || [])
  } catch (error) {
    console.error('获取签到记录失败:', error)
  }
}

// 执行签到
const handleCheckIn = async () => {
  if (checkingIn.value) return
  checkingIn.value = true
  try {
    await checkinApi.doCheckin()
    ElMessage.success(`签到成功！获得 ${config.value?.daily_reward || 10} 书香币`)
    await loadStatus()
    await loadRecords()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.response?.data?.message || '签到失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    checkingIn.value = false
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const res: any = await request.get('/auth/me/')
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const goHome = () => {
  router.push({ name: 'Home' })
}

const handleLogout = async () => {
  try {
    await request.post('/auth/logout/')
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
  loadStatus()
  loadRecords()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.ci-root {
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

/* ── Header ── */
.ci-header {
  background: var(--ink);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid var(--accent);
}

.ci-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.ci-logo {
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

.ci-nav {
  display: flex;
  gap: 0.25rem;
  flex: 1;
}

.ci-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
  letter-spacing: 0.5px;
  cursor: pointer;
}

.ci-nav a:hover,
.ci-nav a.active {
  color: var(--accent);
  background: rgba(202, 138, 4, 0.1);
}

.ci-header__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.ci-header__user {
  color: #D1D5DB;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ci-header__avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid rgba(202, 138, 4, 0.5);
}

.ci-header__logout {
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

.ci-header__logout:hover {
  border-color: #EF4444;
  color: #EF4444;
}

/* ── Main ── */
.ci-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 2.5rem 2rem 3rem;
}

/* ── 签到卡片 ── */
.ci-card-section {
  margin-bottom: 2rem;
}

.ci-check-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-top: none;
  border-bottom: 3px solid var(--accent);
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 20px rgba(202, 138, 4, 0.12);
  overflow: hidden;
  text-align: center;
  padding: 2.5rem 2rem 2rem;
}

.ci-check-card__top {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.ci-check-card__icon {
  color: var(--accent);
  opacity: 0.85;
}

.ci-check-card__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 3px;
  margin: 0;
}

.ci-check-card__subtitle {
  font-size: 0.85rem;
  color: var(--muted);
  font-style: italic;
  font-family: 'Noto Serif SC', serif;
  margin: 0;
  letter-spacing: 1px;
}

.ci-check-card__coins {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
}

.ci-check-card__coins-label {
  font-size: 0.82rem;
  color: var(--muted);
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
}

.ci-check-card__coins-value {
  font-family: 'Noto Serif SC', serif;
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--accent);
  line-height: 1;
  text-shadow: 0 1px 3px rgba(202, 138, 4, 0.2);
}

.ci-check-card__coins-unit {
  font-size: 0.9rem;
  color: var(--accent);
  font-weight: 500;
  letter-spacing: 1px;
}

.ci-check-card__action {
  margin-bottom: 1.75rem;
  min-height: 56px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
}

.ci-btn-sign {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #CA8A04 0%, #92600A 100%);
  color: #fff;
  border: none;
  padding: 14px 48px;
  border-radius: 4px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 3px;
  transition: transform 0.2s, box-shadow 0.2s, filter 0.2s;
  box-shadow: 0 4px 16px rgba(202, 138, 4, 0.35);
  user-select: none;
}

.ci-btn-sign:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(202, 138, 4, 0.45);
  filter: brightness(1.08);
}

.ci-btn-sign:active:not(:disabled) {
  transform: translateY(0);
}

.ci-btn-sign--loading {
  background: linear-gradient(135deg, #B89A2E 0%, #8B6914 100%);
  cursor: wait;
  min-width: 160px;
}

.ci-check-card__hint {
  font-size: 0.78rem;
  color: var(--muted);
  margin: 0;
}

.ci-checked {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--accent);
  font-size: 1.15rem;
  font-weight: 500;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 2px;
  animation: ciFadeIn 0.5s ease-out;
}

@keyframes ciFadeIn {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}

.ci-check-card__streak {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border);
}

.ci-streak-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.ci-streak-num {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.2;
}

.ci-streak-lbl {
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.5px;
}

.ci-streak-sep {
  width: 1px;
  height: 36px;
  background: var(--border);
}

/* ── Spinner ── */
.ci-spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: ciSpin 0.7s linear infinite;
}

@keyframes ciSpin {
  to { transform: rotate(360deg); }
}

/* ── 日历区域 ── */
.ci-calendar-section {
  margin-bottom: 2rem;
}

.ci-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 2px;
  position: relative;
  padding-left: 14px;
  margin: 0 0 1.25rem;
}

.ci-section-title__bar {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: var(--accent);
  border-radius: 2px;
}

.ci-calendar {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1.5rem 1.25rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.ci-calendar__weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 0.5rem;
}

.ci-weekday {
  text-align: center;
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 500;
  padding: 6px 0;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 0.5px;
}

.ci-calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.ci-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  position: relative;
  transition: background-color 0.2s, border-color 0.2s;
  border: 1.5px solid transparent;
  background: #FAF9F7;
}

.ci-day--empty {
  visibility: hidden;
}

.ci-day--future {
  opacity: 0.35;
}

.ci-day--checked {
  background: #FFFBF0;
  border-left: 3px solid var(--accent);
  border-color: rgba(202, 138, 4, 0.2);
}

.ci-day--today {
  border-color: var(--accent);
  border-width: 1.8px;
  box-shadow: 0 0 0 2px rgba(202, 138, 4, 0.15);
  font-weight: 700;
}

.ci-day__num {
  font-size: 0.85rem;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}

.ci-day--checked .ci-day__num {
  color: var(--accent-dark);
  font-weight: 600;
}

.ci-day--today .ci-day__num {
  color: var(--accent);
}

.ci-day__dot {
  position: absolute;
  bottom: 4px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
}

/* ── 规则区域 ── */
.ci-rules-section {
  margin-bottom: 2rem;
}

.ci-rules-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ci-rule {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.88rem;
  color: var(--ink);
  line-height: 1.6;
  padding: 0.75rem 1.25rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 0 4px 4px 0;
}

.ci-rule__icon {
  color: var(--accent);
  font-size: 0.6rem;
  flex-shrink: 0;
  margin-top: 5px;
}

.ci-rule strong {
  color: var(--accent);
  font-weight: 600;
}

/* ── Footer ── */
.ci-footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.83rem;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  border-top: 1px solid var(--border);
  margin-top: 1rem;
}

.ci-footer p {
  margin: 0;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .ci-main {
    padding: 1.5rem 1rem 2rem;
  }

  .ci-header__inner {
    padding: 0 1rem;
  }

  .ci-nav {
    display: none;
  }

  .ci-check-card {
    padding: 2rem 1.25rem 1.5rem;
  }

  .ci-check-card__coins-value {
    font-size: 2.2rem;
  }

  .ci-check-card__streak {
    gap: 1.5rem;
  }

  .ci-calendar {
    padding: 1rem 0.6rem;
  }

  .ci-day__num {
    font-size: 0.76rem;
  }
}
</style>
