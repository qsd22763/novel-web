<template>
  <div class="mem-root">
    <header class="mem-header">
      <div class="mem-header__inner">
        <h1 class="mem-logo" @click="goHome">墨香书阁</h1>
        <nav class="mem-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/rankings">排行榜</router-link>
          <router-link to="/user">个人中心</router-link>
          <router-link to="/user/membership" class="active">充值会员</router-link>
        </nav>
        <div class="mem-header__actions">
          <span class="mem-header__user">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            {{ userInfo.username }}
          </span>
          <button class="mem-header__logout" @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <main class="mem-main">
      <!-- 会员状态卡 -->
      <section class="mem-status-card" :class="{ 'is-vip': isVip }">
        <div class="mem-status-card__inner">
          <div class="mem-status-card__icon">
            <svg v-if="isVip" width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>
            <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
          </div>
          <div class="mem-status-card__info">
            <div class="mem-status-card__top">
              <h2 class="mem-status-card__title">{{ isVip ? '尊贵 VIP 会员' : '普通用户' }}</h2>
              <el-tag :type="isVip ? 'warning' : 'info'" effect="dark" round>{{ isVip ? 'VIP' : '普通' }}</el-tag>
            </div>
            <p v-if="isVip && vipExpireDate" class="mem-status-card__expire">
              有效期至：<span class="mem-status-card__date">{{ formatDate(vipExpireDate) }}</span>
            </p>
            <p v-else class="mem-status-card__hint">开通会员享受全站免广告 · 专属标识 · 更多权益</p>
          </div>
        </div>
      </section>

      <!-- 套餐选择区 -->
      <section class="mem-plans-section">
        <h3 class="mem-section-title">选择会员套餐</h3>
        <div class="mem-plans-grid">
          <div
            v-for="plan in plans"
            :key="plan.key"
            class="mem-plan-card"
            :class="{
              selected: selectedPlan === plan.key,
              recommended: plan.key === 'quarterly',
              bestValue: plan.key === 'yearly'
            }"
            @click="selectedPlan = plan.key"
          >
            <div v-if="plan.key === 'quarterly'" class="mem-plan-card__badge mem-plan-card__badge--hot">热门</div>
            <div v-if="plan.key === 'yearly'" class="mem-plan-card__badge mem-plan-card__badge--value">超值</div>
            <div class="mem-plan-card__name">{{ plan.name }}</div>
            <div class="mem-plan-card__price">
              <span class="mem-plan-card__currency">&yen;</span>
              <span class="mem-plan-card__amount">{{ plan.price }}</span>
              <span class="mem-plan-card__unit">元/{{ getUnit(plan.days) }}</span>
            </div>
            <div class="mem-plan-card__duration">{{ plan.days }} 天有效期</div>
            <ul class="mem-plan-card__benefits">
              <li><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>全站免广告阅读</li>
              <li><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>VIP 专属标识</li>
              <li><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>优先客服支持</li>
              <li><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>新书上架提醒</li>
            </ul>
          </div>
        </div>
        <div class="mem-action-row">
          <button
            class="mem-btn-purchase"
            :disabled="!selectedPlan"
            @click="handlePurchase(selectedPlan)"
          >
            {{ isVip ? '续费会员' : '立即开通' }}
          </button>
        </div>
      </section>

      <!-- 我的订单列表 -->
      <section class="mem-orders-section">
        <h3 class="mem-section-title">我的订单</h3>
        <div v-if="orders.length > 0" class="mem-orders-list">
          <div
            v-for="order in orders"
            :key="order.id"
            class="mem-order-item"
          >
            <div class="mem-order-item__left">
              <span class="mem-order-item__no">订单号：{{ order.order_no || order.id }}</span>
              <el-tag
                :type="order.status === 'paid' ? 'success' : order.status === 'pending' ? 'warning' : 'info'"
                size="small"
                effect="light"
                round
              >{{ getStatusText(order.status) }}</el-tag>
            </div>
            <div class="mem-order-item__center">
              <span class="mem-order-item__plan">{{ getPlanName(order.plan_type) }}</span>
              <span class="mem-order-item__amount">&yen;{{ order.amount }}</span>
            </div>
            <div class="mem-order-item__right">
              <span class="mem-order-item__time">{{ formatDate(order.created_at) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="mem-empty">
          <svg class="mem-empty__icon" width="64" height="64" viewBox="0 0 64 64" fill="none">
            <rect x="16" y="10" width="32" height="44" rx="3" fill="#F5F1EA" stroke="#CA8A04" stroke-width="1.5"/>
            <rect x="22" y="18" width="20" height="3" rx="1" fill="#E8D5B0"/>
            <rect x="22" y="26" width="14" height="3" rx="1" fill="#E8D5B0"/>
            <rect x="22" y="34" width="18" height="3" rx="1" fill="#E8D5B0"/>
            <path d="M28 42l3 3 7-7" stroke="#CA8A04" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p class="mem-empty__title">暂无订单记录</p>
          <p class="mem-empty__hint">选择上方套餐，开启您的 VIP 之旅</p>
        </div>
      </section>
    </main>

    <footer class="mem-footer">
      <p>墨香书阁 &middot; 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { membershipApi, type MembershipPlan } from '../api'
import request from '../utils/request'

const router = useRouter()

const userInfo = ref<any>({})
const isVip = ref(false)
const vipExpireDate = ref<string>('')
const plans = ref<MembershipPlan[]>([])
const orders = ref<any[]>([])
const selectedPlan = ref<string>('')

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

const loadUserInfo = async () => {
  try {
    const res: any = await request.get('/auth/me/')
    userInfo.value = res
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

const loadMyStatus = async () => {
  try {
    const res: any = await membershipApi.myStatus()
    isVip.value = res.is_vip || false
    vipExpireDate.value = res.vip_expire_date || ''
  } catch (error) {
    console.error('获取会员状态失败:', error)
  }
}

const loadPlans = async () => {
  try {
    const res = await membershipApi.plans()
    plans.value = res as MembershipPlan[]
    if (plans.value.length > 0 && !selectedPlan.value) {
      selectedPlan.value = plans.value[1]?.key || plans.value[0].key
    }
  } catch (error) {
    console.error('获取套餐列表失败:', error)
  }
}

const loadOrders = async () => {
  try {
    const res: any = await membershipApi.myOrders()
    orders.value = res.results || res || []
  } catch (error) {
    console.error('获取订单列表失败:', error)
  }
}

const handlePurchase = async (planType: string) => {
  if (!planType) return
  try {
    await ElMessageBox.confirm(`确认购买该套餐？`, '开通会员', {
      confirmButtonText: '确认支付',
      cancelButtonText: '再想想',
      type: 'info',
    })
    await membershipApi.createOrder(planType)
    ElMessage.success('开通成功')
    await loadMyStatus()
    await loadOrders()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '支付失败，请稍后重试')
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getUnit = (days: number) => {
  if (days <= 30) return '月'
  if (days <= 120) return '季'
  return '年'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    paid: '已支付',
    pending: '待支付',
    cancelled: '已取消',
    expired: '已过期',
  }
  return map[status] || status
}

const getPlanName = (planType: string) => {
  const found = plans.value.find((p) => p.key === planType)
  return found?.name || planType
}

onMounted(() => {
  if (!localStorage.getItem('user')) {
    router.push({ name: 'Login' })
    return
  }
  loadUserInfo()
  loadMyStatus()
  loadPlans()
  loadOrders()
})
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.mem-root {
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
.mem-header {
  background: var(--ink);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid var(--accent);
}

.mem-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.mem-logo {
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

.mem-nav {
  display: flex;
  gap: 0.25rem;
  flex: 1;
}

.mem-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
  letter-spacing: 0.5px;
  cursor: pointer;
}

.mem-nav a:hover,
.mem-nav a.active {
  color: var(--accent);
  background: rgba(202, 138, 4, 0.1);
}

.mem-header__actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.mem-header__user {
  color: #D1D5DB;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mem-header__logout {
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

.mem-header__logout:hover {
  border-color: #EF4444;
  color: #EF4444;
}

/* ── Main ── */
.mem-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 2rem 3rem;
}

/* ── Status Card ── */
.mem-status-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-left: 4px solid var(--border);
  border-radius: 3px;
  margin-bottom: 2.5rem;
  overflow: hidden;
  transition: border-color 0.3s;
}

.mem-status-card.is-vip {
  background: linear-gradient(135deg, #CA8A04 0%, #92600A 100%);
  border-color: transparent;
}

.mem-status-card.is-vip .mem-status-card__icon {
  color: rgba(255, 255, 255, 0.95);
}

.mem-status-card.is-vip .mem-status-card__title {
  color: #fff;
}

.mem-status-card.is-vip .mem-status-card__expire,
.mem-status-card.is-vip .mem-status-card__hint {
  color: rgba(255, 255, 255, 0.85);
}

.mem-status-card.is-vip .mem-status-card__date {
  color: #FFF8DC;
  font-weight: 700;
}

.mem-status-card__inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 2.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.mem-status-card__icon {
  color: var(--muted);
  flex-shrink: 0;
}

.mem-status-card__info {
  flex: 1;
}

.mem-status-card__top {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.mem-status-card__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 2px;
  margin: 0;
}

.mem-status-card__expire {
  font-size: 0.92rem;
  color: var(--muted);
  margin: 0;
}

.mem-status-card__date {
  font-family: 'Noto Serif SC', serif;
}

.mem-status-card__hint {
  font-size: 0.9rem;
  color: var(--muted);
  font-style: italic;
  font-family: 'Noto Serif SC', serif;
  margin: 0;
  letter-spacing: 0.5px;
}

/* ── Section Title ── */
.mem-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 2px;
  position: relative;
  padding-left: 14px;
  margin: 0 0 1.5rem;
}

.mem-section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 18px;
  background: var(--accent);
  border-radius: 2px;
}

/* ── Plans Section ── */
.mem-plans-section {
  margin-bottom: 2.5rem;
}

.mem-plans-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.mem-plan-card {
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: 6px;
  padding: 2rem 1.5rem;
  text-align: center;
  cursor: pointer;
  position: relative;
  transition: border-color 0.25s, box-shadow 0.25s, background-color 0.25s;
  overflow: hidden;
}

.mem-plan-card:hover {
  border-color: var(--accent);
  background: #FFFBF0;
}

.mem-plan-card.selected {
  border: 2px solid var(--accent);
  background: linear-gradient(180deg, #FFFBF0 0%, #FFF8E8 100%);
  box-shadow: 0 4px 16px rgba(202, 138, 4, 0.25);
}

.mem-plan-card.recommended {
  border-color: var(--accent);
  border-width: 2px;
}

.mem-plan-card.bestValue {
  border-color: var(--accent-dark);
  border-width: 2px;
}

.mem-plan-card__badge {
  position: absolute;
  top: 12px;
  right: -28px;
  padding: 3px 36px;
  font-size: 0.68rem;
  font-weight: 600;
  color: #fff;
  transform: rotate(45deg);
  letter-spacing: 1px;
  font-family: 'Noto Sans SC', sans-serif;
}

.mem-plan-card__badge--hot {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
}

.mem-plan-card__badge--value {
  background: linear-gradient(135deg, var(--accent) 0%, #92600A 100%);
}

.mem-plan-card__name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 1px;
  margin-bottom: 1rem;
}

.mem-plan-card__price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
  margin-bottom: 0.5rem;
}

.mem-plan-card__currency {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--accent);
}

.mem-plan-card__amount {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Noto Serif SC', serif;
  line-height: 1;
}

.mem-plan-card__unit {
  font-size: 0.82rem;
  color: var(--muted);
  margin-left: 2px;
}

.mem-plan-card__duration {
  font-size: 0.82rem;
  color: var(--muted);
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px dashed var(--border);
}

.mem-plan-card__benefits {
  list-style: none;
  padding: 0;
  margin: 0;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.mem-plan-card__benefits li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--muted);
}

.mem-plan-card__benefits li svg {
  color: var(--accent);
  flex-shrink: 0;
}

.mem-plan-card.selected .mem-plan-card__benefits li {
  color: var(--ink);
}

/* ── Action Row ── */
.mem-action-row {
  text-align: center;
}

.mem-btn-purchase {
  background: linear-gradient(135deg, var(--accent) 0%, #92600A 100%);
  color: #fff;
  border: none;
  padding: 13px 56px;
  border-radius: 3px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 2px;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 4px 16px rgba(202, 138, 4, 0.35);
}

.mem-btn-purchase:hover:not(:disabled) {
  opacity: 0.92;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(202, 138, 4, 0.45);
}

.mem-btn-purchase:active:not(:disabled) {
  transform: translateY(0);
}

.mem-btn-purchase:disabled {
  background: #C9CDD4;
  cursor: not-allowed;
  box-shadow: none;
}

/* ── Orders Section ── */
.mem-orders-section {
  margin-bottom: 2rem;
}

.mem-orders-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.mem-order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.1rem 1.5rem;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-left: 3px solid var(--border);
  border-radius: 0 3px 3px 0;
  transition: border-color 0.2s, background-color 0.2s;
}

.mem-order-item:hover {
  border-left-color: var(--accent);
  background: #FAFAF8;
}

.mem-order-item__left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 0;
}

.mem-order-item__no {
  font-size: 0.85rem;
  color: var(--muted);
  font-family: monospace;
}

.mem-order-item__center {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.mem-order-item__plan {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
}

.mem-order-item__amount {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent);
  font-family: 'Noto Serif SC', serif;
}

.mem-order-item__right {
  flex-shrink: 0;
}

.mem-order-item__time {
  font-size: 0.78rem;
  color: #9CA3AF;
  white-space: nowrap;
}

/* ── Empty State ── */
.mem-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3.5rem 0;
  gap: 0.6rem;
}

.mem-empty__icon {
  margin-bottom: 0.5rem;
  opacity: 0.65;
}

.mem-empty__title {
  font-size: 1rem;
  color: var(--ink);
  font-family: 'Noto Serif SC', serif;
  margin: 0;
}

.mem-empty__hint {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
}

/* ── Footer ── */
.mem-footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.83rem;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}

.mem-footer p {
  margin: 0;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .mem-plans-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }

  .mem-plan-card {
    padding: 1.5rem 1rem;
  }

  .mem-plan-card__amount {
    font-size: 1.6rem;
  }
}

@media (max-width: 768px) {
  .mem-main {
    padding: 1.5rem 1.25rem 2.5rem;
  }

  .mem-header__inner {
    padding: 0 1rem;
    gap: 1rem;
  }

  .mem-nav {
    display: none;
  }

  .mem-plans-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .mem-status-card__inner {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem 1.25rem;
    gap: 1rem;
  }

  .mem-status-card__top {
    justify-content: center;
  }

  .mem-order-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .mem-order-item__center,
  .mem-order-item__right {
    align-self: flex-start;
  }

  .mem-btn-purchase {
    width: 100%;
    padding: 12px 0;
  }
}

@media (max-width: 375px) {
  .mem-main {
    padding: 1rem 1rem 2rem;
  }

  .mem-header__inner {
    padding: 0 0.75rem;
  }

  .mem-logo {
    font-size: 1.2rem;
    letter-spacing: 2px;
  }

  .mem-header__user {
    font-size: 0.78rem;
  }

  .mem-status-card__title {
    font-size: 1.15rem;
  }
}
</style>
