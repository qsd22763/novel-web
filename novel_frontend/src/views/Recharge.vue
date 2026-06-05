<template>
  <div class="recharge-root">
    <header class="recharge-header">
      <div class="recharge-header__inner">
        <h1 class="recharge-logo" @click="goHome">墨香书阁</h1>
        <nav class="recharge-nav">
          <router-link to="/">首页</router-link>
          <router-link to="/novels">书库</router-link>
          <router-link to="/user">个人中心</router-link>
        </nav>
      </div>
    </header>

    <main class="recharge-main">
      <!-- 会员状态卡片 -->
      <el-card class="recharge-status-card" shadow="never">
        <div class="status-card__inner">
          <div class="status-card__icon">
            <svg v-if="vipStatus.is_vip" width="48" height="48" viewBox="0 0 24 24" fill="var(--gold)"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>
            <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" stroke-width="1.5"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          </div>
          <div class="status-card__info">
            <h3 class="status-card__title">{{ vipStatus.is_vip ? '尊贵 VIP 会员' : '开通会员享特权' }}</h3>
            <p class="status-card__desc">
              {{ vipStatus.is_vip ? `有效期至 ${formatDate(vipStatus.expire_date)}` : '解锁全部专属权益，畅享阅读体验' }}
            </p>
          </div>
        </div>
      </el-card>

      <!-- 套餐选择 -->
      <div class="recharge-plans">
        <h2 class="recharge-section-title">选择套餐</h2>
        <div class="plans-grid">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="plan-card"
            :class="{ 'is-selected': selectedPlan === plan.id, 'is-recommended': plan.plan_type === 'yearly' }"
            @click="selectedPlan = plan.id"
          >
            <span v-if="plan.plan_type === 'yearly'" class="plan-badge">推荐</span>
            <h4 class="plan-name">{{ plan.name }}</h4>
            <div class="plan-price">
              <span class="plan-price__symbol">¥</span>
              <span class="plan-price__num">{{ plan.price }}</span>
            </div>
            <p class="plan-duration">{{ plan.days }} 天</p>
            <p class="plan-desc">{{ plan.description }}</p>
            <button
              class="plan-btn"
              :class="{ 'is-active': selectedPlan === plan.id }"
              @click.stop="handlePurchase(plan)"
            >
              立即开通
            </button>
          </div>
        </div>
      </div>

      <!-- 会员权益 -->
      <el-card class="recharge-benefits" shadow="never">
        <h2 class="recharge-section-title">会员权益</h2>
        <div class="benefits-grid">
          <div class="benefit-item">
            <div class="benefit-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
            </div>
            <h4 class="benefit-title">免广告阅读</h4>
            <p class="benefit-desc">全站无广告干扰，沉浸式阅读体验</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"/></svg>
            </div>
            <h4 class="benefit-title">专属标识</h4>
            <p class="benefit-desc">VIP 徽章彰显身份，评论区高亮显示</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
            </div>
            <h4 class="benefit-title">极速更新</h4>
            <p class="benefit-desc">新章节优先推送，抢先畅读精彩内容</p>
          </div>
          <div class="benefit-item">
            <div class="benefit-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>
            </div>
            <h4 class="benefit-title">更多书币</h4>
            <p class="benefit-desc">每日签到奖励翻倍，更多福利等你来</p>
          </div>
        </div>
      </el-card>
    </main>

    <footer class="recharge-footer">
      <p>墨香书阁 · 让阅读成为一种习惯</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { rechargeApi } from '../api'

const router = useRouter()
const vipStatus = ref<any>({ is_vip: false, expire_date: '' })
const plans = ref<any[]>([])
const selectedPlan = ref<number | null>(null)
const purchasing = ref(false)

const loadPlans = async () => {
  try {
    const res: any = await rechargeApi.getPlans()
    plans.value = res || []
    if (plans.value.length > 0 && !selectedPlan.value) {
      // 默认选中第一个
      selectedPlan.value = plans.value[0].id
    }
  } catch (error) {
    console.error('获取套餐列表失败:', error)
  }
}

const loadVipStatus = async () => {
  try {
    const res: any = await rechargeApi.vipStatus()
    vipStatus.value = res
  } catch (error) {
    console.error('获取VIP状态失败:', error)
  }
}

const handlePurchase = async (plan: any) => {
  selectedPlan.value = plan.id
  if (purchasing.value) return
  purchasing.value = true
  try {
    const res: any = await rechargeApi.createOrder(plan.id)
    ElMessage.success(res.message || '开通成功！')
    await loadVipStatus()
  } catch (err: any) {
    const data = err?.response?.data
    ElMessage.error(data?.message || data?.detail || '开通失败，请稍后重试')
  } finally {
    purchasing.value = false
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const goHome = () => {
  router.push({ name: 'Home' })
}

onMounted(() => {
  loadPlans()
  loadVipStatus()
})
</script>

<style scoped>
.recharge-root {
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

.recharge-header {
  background: var(--ink);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 2px solid var(--gold);
}

.recharge-header__inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.recharge-logo {
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

.recharge-nav {
  display: flex;
  gap: 0.25rem;
}

.recharge-nav a {
  color: #9CA3AF;
  text-decoration: none;
  font-size: 0.88rem;
  padding: 6px 14px;
  border-radius: 2px;
  transition: color 0.2s, background-color 0.2s;
  cursor: pointer;
}

.recharge-nav a:hover {
  color: var(--gold);
  background: rgba(184, 134, 11, 0.1);
}

.recharge-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 2rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 会员状态卡片 */
.recharge-status-card {
  border-radius: 6px;
  border: 1px solid var(--border);
  background: linear-gradient(135deg, #FFFBF0 0%, #FFF8E8 100%);
  overflow: hidden;
}

.status-card__inner {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.status-card__icon {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(184, 134, 11, 0.12) 0%, rgba(184, 134, 11, 0.05) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-card__info {
  flex: 1;
}

.status-card__title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ink);
  letter-spacing: 2px;
  margin: 0 0 0.35rem;
}

.status-card__desc {
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
}

/* 区块标题 */
.recharge-section-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 2px;
  margin: 0 0 1.5rem;
  position: relative;
  padding-left: 12px;
}

.recharge-section-title::before {
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

/* 套餐网格 */
.plans-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
}

.plan-card {
  position: relative;
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 2rem 1.25rem 1.75rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.plan-card:hover {
  border-color: var(--gold-light);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(184, 134, 11, 0.12);
}

.plan-card.is-selected {
  border-color: var(--gold);
  background: linear-gradient(180deg, #FFFBF0 0%, var(--card-bg) 40%);
  box-shadow: 0 4px 20px rgba(184, 134, 11, 0.2);
}

.plan-badge {
  position: absolute;
  top: -10px;
  right: 16px;
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
  color: #fff;
  font-size: 0.72rem;
  padding: 3px 12px;
  border-radius: 20px;
  letter-spacing: 1px;
  font-weight: 600;
}

.plan-name {
  font-family: 'Noto Serif SC', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  letter-spacing: 2px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
  margin: 0.5rem 0;
}

.plan-price__symbol {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--gold);
}

.plan-price__num {
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--gold);
  font-family: 'Noto Serif SC', serif;
  line-height: 1;
}

.plan-duration {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
  background: #F5F1EA;
  padding: 2px 14px;
  border-radius: 20px;
}

.plan-desc {
  font-size: 0.8rem;
  color: #9CA3AF;
  margin: 0;
  line-height: 1.4;
  min-height: 2.2em;
}

.plan-btn {
  width: 100%;
  max-width: 160px;
  padding: 10px 0;
  border: 2px solid var(--gold);
  background: transparent;
  color: var(--gold);
  font-size: 0.92rem;
  font-weight: 600;
  border-radius: 4px;
  cursor: pointer;
  font-family: 'Noto Sans SC', sans-serif;
  letter-spacing: 2px;
  transition: all 0.25s;
  margin-top: 0.5rem;
}

.plan-btn:hover {
  background: var(--gold);
  color: #fff;
}

.plan-btn.is-active {
  background: var(--gold);
  color: #fff;
}

/* 会员权益 */
.recharge-benefits {
  border-radius: 6px;
  border: 1px solid var(--border);
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.benefit-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(184, 134, 11, 0.1) 0%, rgba(184, 134, 11, 0.04) 100%);
  color: var(--gold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.benefit-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.3rem;
  font-family: 'Noto Serif SC', serif;
}

.benefit-desc {
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.5;
}

.recharge-footer {
  text-align: center;
  padding: 2rem;
  color: var(--muted);
  font-size: 0.83rem;
  font-family: 'Noto Serif SC', serif;
  letter-spacing: 1px;
  border-top: 1px solid var(--border);
  margin-top: 1rem;
}

.recharge-footer p {
  margin: 0;
}

@media (max-width: 768px) {
  .recharge-main {
    padding: 1.25rem 1rem 2rem;
  }

  .plans-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .plan-card {
    padding: 1.5rem 1.25rem 1.25rem;
  }

  .benefits-grid {
    grid-template-columns: 1fr;
  }

  .status-card__inner {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .recharge-header__inner {
    padding: 0 1rem;
  }

  .recharge-nav {
    display: none;
  }
}
</style>
