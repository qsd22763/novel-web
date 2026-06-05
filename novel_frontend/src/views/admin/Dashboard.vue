<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api'

const loading = ref(true)

const overview = ref({
  total_books: 0,
  total_users: 0,
  today_reads: 0,
  new_comments: 0,
  books_change: 0,
  users_change: 0,
  reads_change: 0,
  comments_change: 0,
})

const recentUsers = ref<any[]>([])
const recentComments = ref<any[]>([])
const byCategory = ref<any[]>([])
const categoryTotal = ref(0)
const weeklyTrend = ref<any[]>([])

const statCards = [
  {
    key: 'total_books',
    title: '总书籍数',
    icon: 'Notebook',
    color: '#3B82F6',
    bgGradient: 'linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0.04) 100%)',
    borderColor: 'rgba(59,130,246,0.25)',
    shadowColor: 'rgba(59,130,246,0.12)',
    changeKey: 'books_change' as const,
  },
  {
    key: 'total_users',
    title: '总用户数',
    icon: 'User',
    color: '#22C55E',
    bgGradient: 'linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(34,197,94,0.04) 100%)',
    borderColor: 'rgba(34,197,94,0.25)',
    shadowColor: 'rgba(34,197,94,0.12)',
    changeKey: 'users_change' as const,
  },
  {
    key: 'today_reads',
    title: '今日阅读',
    icon: 'Reading',
    color: '#A855F7',
    bgGradient: 'linear-gradient(135deg, rgba(168,85,247,0.15) 0%, rgba(168,85,247,0.04) 100%)',
    borderColor: 'rgba(168,85,247,0.25)',
    shadowColor: 'rgba(168,85,247,0.12)',
    changeKey: 'reads_change' as const,
  },
  {
    key: 'new_comments',
    title: '新增评论',
    icon: 'ChatDotRound',
    color: '#F59E0B',
    bgGradient: 'linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(245,158,11,0.04) 100%)',
    borderColor: 'rgba(245,158,11,0.25)',
    shadowColor: 'rgba(245,158,11,0.12)',
    changeKey: 'comments_change' as const,
  },
]

const pieColors = ['#22C55E', '#3B82F6', '#A855F7', '#F59E0B', '#EF4444', '#06B6D4', '#EC4899', '#8B5CF6']

function buildLinePath(data: number[], maxVal: number): string {
  if (!data.length) return ''
  const w = 600, h = 160, pad = 10
  const pts = data.map((v, i) => ({
    x: pad + (i / (data.length - 1)) * (w - pad * 2),
    y: h - pad - (v / maxVal) * (h - pad * 2)
  }))
  let d = `M${pts[0].x},${pts[0].y}`
  for (let i = 1; i < pts.length; i++) d += ` L${pts[i].x},${pts[i].y}`
  return d
}

function buildAreaPath(linePath: string): string {
  return linePath + ` L600,200 L0,200 Z`
}

const linePath = ref('')
const areaPath = ref('')
const chartMax = ref(1)
const chartLabels = ref<string[]>([])

onMounted(async () => {
  try {
    const data: any = await adminApi.dashboard.fullStats()
    if (data?.overview) {
      overview.value = { ...overview.value, ...data.overview }
    }
    if (data?.recent_users) recentUsers.value = data.recent_users
    if (data?.recent_comments) recentComments.value = data.recent_comments
    if (data?.by_category) {
      byCategory.value = data.by_category.slice(0, 6)
      categoryTotal.value = data.category_total || sumByCategory(byCategory.value)
    }
    if (data?.weekly_trend && data.weekly_trend.length) {
      weeklyTrend.value = data.weekly_trend
      const novelsData = weeklyTrend.value.map((t: any) => t.novels || 0)
      chartMax.value = Math.max(...novelsData, 1)
      linePath.value = buildLinePath(novelsData, chartMax.value)
      areaPath.value = buildAreaPath(linePath.value)
      chartLabels.value = weeklyTrend.value.map((t: any) => t.date)
    }
  } catch {
  } finally {
    loading.value = false
  }
})

function sumByCategory(arr: any[]): number {
  return arr.reduce((s, c) => s + (c.count || 0), 0)
}
</script>

<template>
  <div class="dashboard" v-loading="loading">
    <!-- Page Title -->
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
      <p class="page-subtitle">欢迎回来，这是系统运行概览</p>
    </div>

    <!-- Stat Cards -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="card in statCards" :key="card.key">
        <div class="stat-card" :style="{ background: card.bgGradient, borderColor: card.borderColor }">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value" style="font-family: 'Fira Code', monospace">
                {{ (overview as any)[card.key] || 0 }}
              </span>
              <span class="stat-label">{{ card.title }}</span>
            </div>
            <div class="stat-icon-wrap" :style="{ background: `rgba(${hexToRgb(card.color)},0.12)`, color: card.color }">
              <el-icon :size="26"><component :is="card.icon" /></el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span class="trend" :class="{ up: (overview as any)[card.changeKey] >= 0, down: (overview as any)[card.changeKey] < 0 }">
              <el-icon :size="13"><Top v-if="(overview as any)[card.changeKey] >= 0" /><Bottom v-else /></el-icon>
              {{ Math.abs((overview as any)[card.changeKey]) || 0 }}%
            </span>
            <span class="trend-label">较昨日</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Area -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">近7天新增书籍趋势</h3>
            <span class="panel-badge">实时</span>
          </div>
          <div class="chart-placeholder chart-line">
            <svg v-if="linePath" viewBox="0 0 600 200" preserveAspectRatio="none" class="chart-svg">
              <defs>
                <linearGradient id="lineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="#22C55E" stop-opacity="0.3"/>
                  <stop offset="100%" stop-color="#22C55E" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <path :d="areaPath" fill="url(#lineGrad)" />
              <path :d="linePath" fill="none" stroke="#22C55E" stroke-width="2.5" stroke-linecap="round"/>
              <circle v-for="(pt, i) in weeklyTrend" :key="i"
                      :cx="10 + (i / Math.max(weeklyTrend.length - 1, 1)) * 580"
                      :cy="190 - ((pt.novels || 0) / chartMax) * 170"
                      r="4" fill="#22C55E"/>
            </svg>
            <svg v-else viewBox="0 0 600 200" preserveAspectRatio="none" class="chart-svg">
              <text x="300" y="100" text-anchor="middle" fill="#64748B" font-size="14">暂无数据</text>
            </svg>
            <div class="chart-labels" v-if="chartLabels.length">
              <span v-for="(label, i) in chartLabels" :key="i">{{ label }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">分类占比</h3>
            <span class="panel-badge">{{ categoryTotal }} 本</span>
          </div>
          <div class="chart-placeholder chart-pie">
            <svg v-if="byCategory.length" viewBox="0 0 200 200" class="pie-svg">
              <template v-for="(cat, i) in byCategory" :key="cat.category">
                <circle cx="100" cy="100" r="70" fill="none"
                        :stroke="pieColors[i % pieColors.length]" stroke-width="28"
                        :stroke-dasharray="`${(cat.count / categoryTotal) * 440} ${440 - (cat.count / categoryTotal) * 440}`"
                        :stroke-dashoffset="-(i > 0 ? byCategory.slice(0, i).reduce((s, c) => s + (c.count / categoryTotal) * 440, 0) : 0)"
                        transform="rotate(-90 100 100)"
                        style="transition: stroke-dasharray 0.8s ease;"/>
              </template>
              <circle cx="100" cy="100" r="70" fill="none" stroke="#1E293B" stroke-width="28"/>
              <text x="100" y="96" text-anchor="middle" fill="#F8FAFC" font-size="20" font-weight="700" font-family="'Fira Code',monospace">{{ categoryTotal }}</text>
              <text x="100" y="116" text-anchor="middle" fill="#64748B" font-size="11">总书籍</text>
            </svg>
            <svg v-else viewBox="0 0 200 200" class="pie-svg">
              <text x="100" y="105" text-anchor="middle" fill="#64748B" font-size="14">暂无数据</text>
            </svg>
            <div class="pie-legend">
              <div v-for="(cat, i) in byCategory" :key="cat.category" class="legend-item">
                <span class="legend-dot" :style="{ background: pieColors[i % pieColors.length] }"></span>
                {{ cat.category }} {{ Math.round((cat.count / categoryTotal) * 100) }}%
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Recent Activity -->
    <el-row :gutter="20" class="activity-row">
      <el-col :xs="24" :lg="12">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">最新注册用户</h3>
            <span class="panel-badge">{{ recentUsers.length }} 人</span>
          </div>
          <el-table v-if="recentUsers.length" :data="recentUsers" class="admin-table" stripe style="width: 100%">
            <el-table-column prop="username" label="用户名" min-width="120">
              <template #default="{ row }">
                <div class="table-user">
                  <div class="table-avatar-sm">{{ row.username.charAt(0) }}</div>
                  <span>{{ row.username }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
            <el-table-column prop="date_joined" label="注册时间" min-width="150" />
          </el-table>
          <div v-else class="empty-hint">暂无注册用户数据</div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="panel">
          <div class="panel-header">
            <h3 class="panel-title">最新评论</h3>
            <span class="panel-badge">{{ recentComments.length }} 条</span>
          </div>
          <div v-if="recentComments.length" class="comment-list">
            <div v-for="comment in recentComments" :key="comment.id" class="comment-item">
              <div class="comment-meta">
                <span class="comment-user">{{ comment.user }}</span>
                <span class="comment-novel">《{{ comment.novel }}》</span>
                <span class="comment-time">{{ comment.time }}</span>
              </div>
              <p class="comment-content">{{ comment.content }}</p>
            </div>
          </div>
          <div v-else class="empty-hint">暂无评论数据</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? `${parseInt(result[1],16)},${parseInt(result[2],16)},${parseInt(result[3],16)}` : '0,0,0'
}
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

.dashboard {
  font-family: 'Fira Sans', system-ui, -apple-system, sans-serif;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0 0 6px;
  letter-spacing: -0.3px;
  text-shadow: 0 0 30px rgba(255,255,255,0.06);
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.stat-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 14px;
  padding: 22px;
  border: 1px solid;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  height: 100%;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.25);
}

.stat-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.stat-value {
  display: block;
  font-size: 30px;
  font-weight: 700;
  color: #F8FAFC;
  line-height: 1.15;
  letter-spacing: -0.5px;
  text-shadow: 0 0 20px rgba(255,255,255,0.08);
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #94A3B8;
  margin-top: 5px;
  font-weight: 500;
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 14px;
  border-top: 1px solid rgba(30,41,59,0.5);
}

.trend {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12.5px;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
  padding: 2px 6px;
  border-radius: 5px;
}

.trend.up {
  color: #22C55E;
  background: rgba(34,197,94,0.1);
}

.trend.down {
  color: #EF4444;
  background: rgba(239,68,68,0.1);
}

.trend-label {
  font-size: 12px;
  color: #64748B;
}

.panel {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 24px;
  transition: all 0.25s ease;
}

.panel:hover {
  border-color: rgba(34,197,94,0.15);
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid rgba(30,41,59,0.6);
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #F8FAFC;
  margin: 0;
}

.panel-badge {
  font-size: 11px;
  font-weight: 600;
  color: #22C55E;
  background: rgba(34,197,94,0.1);
  padding: 3px 10px;
  border-radius: 20px;
  font-family: 'Fira Code', monospace;
  letter-spacing: 0.3px;
}

.chart-placeholder {
  padding: 22px;
  position: relative;
}

.chart-line {
  height: 220px;
}

.chart-svg {
  width: 100%;
  height: 170px;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 11px;
  color: #64748B;
  font-family: 'Fira Code', monospace;
}

.chart-pie {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 32px 22px;
}

.pie-svg {
  width: 180px;
  height: 180px;
  flex-shrink: 0;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #CBD5E1;
}

.legend-dot {
  width: 9px;
  height: 9px;
  border-radius: 3px;
  flex-shrink: 0;
}

.admin-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(30,41,59,0.45);
  --el-table-row-hover-bg-color: rgba(30,41,59,0.4);
  --el-table-border-color: #1E293B;
  --el-table-text-color: #E2E8F0;
  --el-table-header-text-color: #94A3B8;
  border: none;
  font-size: 13px;
  border-radius: 0;
}

.admin-table :deep(.el-table th.el-table__cell) {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-table :deep(.el-table .el-table__row) {
  cursor: default;
}

.admin-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(30,41,59,0.25);
}

.table-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.comment-list {
  padding: 0 22px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item {
  padding: 14px 16px;
  background: rgba(30,41,59,0.3);
  border-radius: 10px;
  border: 1px solid rgba(30,41,59,0.4);
  transition: all 0.2s ease;
}

.comment-item:hover {
  background: rgba(30,41,59,0.5);
  border-color: rgba(34,197,94,0.1);
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 7px;
  flex-wrap: wrap;
}

.comment-user {
  font-weight: 600;
  font-size: 13px;
  color: #F8FAFC;
}

.comment-novel {
  font-size: 12px;
  color: #22C55E;
  background: rgba(34,197,94,0.08);
  padding: 1px 8px;
  border-radius: 4px;
}

.comment-time {
  font-size: 11.5px;
  color: #64748B;
  font-family: 'Fira Code', monospace;
  margin-left: auto;
}

.comment-content {
  font-size: 13px;
  color: #94A3B8;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-hint {
  padding: 40px 22px;
  text-align: center;
  color: #64748B;
  font-size: 14px;
}

@media (max-width: 992px) {
  .stat-row .el-col {
    margin-bottom: 16px;
  }
}
</style>
