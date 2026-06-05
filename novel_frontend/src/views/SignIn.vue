<template>
  <div class="signin-root">
    <header class="signin-header">
      <div class="signin-header__inner">
        <h1 class="signin-logo" @click="goHome">墨香书阁</h1>
        <nav class="signin-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/user">个人中心</router-link>
        </nav>
      </div>
    </header>

    <main class="signin-main">
      <el-card class="signin-card" shadow="never">
        <h2 class="signin-title">每日签到</h2>

        <!-- 签到按钮区域 -->
        <div class="signin-btn-area">
          <button
            class="signin-btn"
            :class="{ 'is-signed': status.is_signed_today, 'is-loading': signing }"
            :disabled="status.is_signed_today || signing"
            @click="handleSignin"
          >
            <span v-if="signing" class="signin-btn__loading">
              <svg class="signin-spin" width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="31.4 31.4" stroke-linecap="round"/></svg>
            </span>
            <span v-else-if="status.is_signed_today" class="signin-btn__icon">✓</span>
            <span v-else>立即签到</span>
          </button>
          <p class="signin-streak">
            已连续签到 <strong>{{ status.consecutive_days || 0 }}</strong> 天
          </p>
          <p v-if="status.is_signed_today" class="signin-hint">今日已获得 {{ lastCoins }} 书币</p>
        </div>

        <!-- 7天签到日历 -->
        <div class="signin-calendar">
          <h3 class="signin-section-title">近七日签到</h3>
          <div class="signin-calendar__grid">
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              class="signin-day"
              :class="{
                'is-signed': day.signed,
                'is-today': day.isToday,
                'is-future': day.isFuture,
              }"
            >
              <span class="signin-day__date">{{ day.dateStr }}</span>
              <span class="signin-day__weekday">{{ day.weekday }}</span>
              <span v-if="day.signed" class="signin-day__check">✓</span>
              <span v-else-if="day.isFuture" class="signin-day__dot">·</span>
              <span v-else class="signin-day__dot signin-day__dot--miss">×</span>
            </div>
          </div>
        </div>

        <!-- 奖励说明 -->
        <div class="signin-rewards">
          <h3 class="signin-section-title">签到奖励</h3>
          <div class="signin-rewards__list">
            <div v-for="item in rewardRules" :key="item.day" class="signin-reward-item">
              <span class="signin-reward__day">第{{ item.day }}天</span>
              <span class="signin-reward__coins">+{{ item.coins }} 书币</span>
            </div>
          </div>
        </div>

        <!-- 最近签到记录 -->
        <div class="signin-records">
          <h3 class="signin-section-title">签到记录</h3>
          <el-table
            v-if="status.recent_records && status.recent_records.length > 0"
            :data="status.recent_records"
            stripe
            size="small"
            class="signin-table"
          >
            <el-table-column prop="created_at" label="签到日期" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="coins_earned" label="获得书币" width="120" align="center">
              <template #default="{ row }">
                <span class="signin-coins">+{{ row.coins_earned }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="consecutive_days" label="连续天数" align="center">
              <template #default="{ row }">{{ row.consecutive_days }} 天</template>
            </el-table-column>
          </el-table>
          <div v-else class="signin-empty">
            <p>暂无签到记录，快来签到吧！</p>
          </div>
        </div>
      </el-card>
    </main>

    <footer class="signin-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { signinApi } from '../api'

const router = useRouter()
const signing = ref(false)
const status = ref<any>({
  is_signed_today: false,
  consecutive_days: 0,
  total_count: 0,
  recent_records: [],
})
const lastCoins = ref(0)

// 签到奖励规则
const rewardRules = [
  { day: 1, coins: 10 },
  { day: 2, coins: 15 },
  { day: 3, coins: 20 },
  { day: 4, coins: 25 },
  { day: 5, coins: 30 },
  { day: 6, coins: 40 },
  { day: 7, coins: 50 },
  { day: 15, coins: 100 },
  { day: 30, coins: 200 },
]

// 计算近7天的日期
const calendarDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']

  // 从6天前到今天
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = `${d.getMonth() + 1}/${d.getDate()}`
    const isToday = i === 0

    // 检查是否已签到
    let signed = false
    if (status.value.recent_records) {
      const recordDate = d.toISOString().split('T')[0]
      signed = status.value.recent_records.some((r: any) =>
        r.created_at && r.created_at.startsWith(recordDate)
      )
    }

    days.push({
      dateStr,
      weekday: weekdays[d.getDay()],
      isToday,
      signed,
      isFuture: false,
    })
  }
  return days
})

const handleSignin = async () => {
  if (status.value.is_signed_today) return
  signing.value = true
  try {
    const res: any = await signinApi.doSignin()
    ElMessage.success(res.message || '签到成功！')
    lastCoins.value = res.coins_earned || 0
    await loadStatus()
  } catch (err: any) {
    const data = err?.response?.data
    if (data?.already_signed) {
      ElMessage.warning(data.message || '今日已签到')
    } else {
      ElMessage.error(data?.message || '签到失败，请稍后重试')
    }
  } finally {
    signing.value = false
  }
}

const loadStatus = async () => {
  try {
    const res: any = await signinApi.getStatus()
    status.value = res
  } catch (error) {
    console.error('获取签到状态失败:', error)
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const goHome = () => {
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadStatus()
})
</script>

<style scoped>
.signin-root {
  --gold: #B8860B;
  --gold-dark: #9A7209;
  --gold-light: #D4A843;
  --bg: #FAF8F5;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --border: #E8E0D4;
  --card-bg: #FFFFFF;

  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
}

.signin-header {
  background: var(--ink);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid var(--gold);
}

.signin-header__inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.signin-logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--gold);
  cursor: pointer;
  letter-spacing: 3px;
  user-select: none;
  margin: 0;
  flex-shrink: 0;
}

.signin-nav {
  display: flex;
  gap: 0.25rem;
}

.signin-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
  cursor: pointer;
}

.signin-nav a:hover {
  color: var(--gold);
  background: rgba(184, 134, 11, 0.1);
}

.signin-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 2rem 3rem;
}

.signin-card {
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card-bg);
}

.signin-card :deep(.el-card__body) {
  padding: 2.5rem 2rem;
}

.signin-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--ink);
  text-align: center;
  letter-spacing: 6px;
  margin: 0 0 2.5rem;
  position: relative;
}

.signin-title::after {
  content: '';
  display: block;
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 0.75rem auto 0;
  border-radius: 2px;
}

/* 签到按钮 */
.signin-btn-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border);
}

.signin-btn {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid var(--gold);
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
  color: #fff;
  font-size: 1.15rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(184, 134, 11, 0.35);
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 2px;
  position: relative;
  overflow: hidden;
}

.signin-btn:hover:not(:disabled):not(.is-signed) {
  transform: scale(1.06);
  box-shadow: 0 6px 28px rgba(184, 134, 11, 0.5);
}

.signin-btn:active:not(:disabled):not(.is-signed) {
  transform: scale(0.98);
}

.signin-btn.is-signed {
  background: #C9CDD4;
  border-color: #C9CDD4;
  box-shadow: none;
  cursor: default;
  font-size: 1rem;
}

.signin-btn.is-loading {
  cursor: wait;
}

.signin-btn__icon {
  font-size: 2rem;
}

.signin-spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.signin-streak {
  font-size: 1rem;
  color: var(--muted);
  margin: 0;
}

.signin-streak strong {
  color: var(--gold);
  font-size: 1.2rem;
  font-weight: 700;
  font-family: 'Noto Serif SC', serif;
}

.signin-hint {
  font-size: 0.85rem;
  color: var(--gold);
  margin: 0;
  font-weight: 500;
}

/* 区块标题 */
.signin-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 2px;
  margin: 0 0 1.25rem;
  position: relative;
  padding-left: 12px;
}

.signin-section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: var(--gold);
  border-radius: 2px;
}

/* 日历 */
.signin-calendar {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border);
}

.signin-calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.signin-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: #FAFAFA;
  transition: all 0.2s;
}

.signin-day.is-today {
  border-color: var(--gold);
  background: #FFFBF0;
}

.signin-day.is-signed {
  background: linear-gradient(135deg, #FFF9E6 0%, #FFF3CC 100%);
  border-color: var(--gold-light);
}

.signin-day.is-future {
  opacity: 0.45;
}

.signin-day__date {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
}

.signin-day__weekday {
  font-size: 0.72rem;
  color: var(--muted);
}

.signin-day__check {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--gold);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  margin-top: 2px;
}

.signin-day__dot {
  font-size: 1.2rem;
  color: #D1D5DB;
  line-height: 1;
}

.signin-day__dot--miss {
  color: #EF4444;
  opacity: 0.5;
}

/* 奖励说明 */
.signin-rewards {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px dashed var(--border);
}

.signin-rewards__list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.signin-reward-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #FAFAFA;
  border: 1px solid var(--border);
  border-radius: 4px;
  transition: border-color 0.2s;
}

.signin-reward-item:hover {
  border-color: var(--gold-light);
}

.signin-reward__day {
  font-size: 0.88rem;
  color: var(--muted);
  font-family: 'Noto Serif SC', serif;
}

.signin-reward__coins {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--gold);
}

/* 签到记录 */
.signin-coins {
  color: var(--gold);
  font-weight: 600;
}

.signin-table {
  width: 100%;
}

.signin-empty {
  text-align: center;
  padding: 2rem 0;
  color: var(--muted);
  font-size: 0.9rem;
}

.signin-footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.83rem;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  border-top: 1px solid var(--border);
  margin-top: 1rem;
}

.signin-footer p {
  margin: 0;
}

@media (max-width: 768px) {
  .signin-main {
    padding: 1.25rem 1rem 2rem;
  }

  .signin-card :deep(.el-card__body) {
    padding: 1.5rem 1rem;
  }

  .signin-title {
    font-size: 1.4rem;
    letter-spacing: 4px;
  }

  .signin-btn {
    width: 100px;
    height: 100px;
    font-size: 1rem;
  }

  .signin-calendar__grid {
    gap: 6px;
  }

  .signin-day {
    padding: 8px 4px 6px;
  }

  .signin-day__date {
    font-size: 0.82rem;
  }

  .signin-rewards__list {
    grid-template-columns: repeat(2, 1fr);
  }

  .signin-header__inner {
    padding: 0 1rem;
  }

  .signin-nav {
    display: none;
  }
}
</style>
