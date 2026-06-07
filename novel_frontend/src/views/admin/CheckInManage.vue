<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(15)

// 筛选条件
const dateRange = ref<[string, string] | null>(null)
const search = ref('')

// 统计数据
const stats = ref({
  today_count: 0,
  total_checkins: 0,
  unique_users: 0,
  daily_reward: 10,
})

// 近7天趋势
const trendData = ref<{ date: string; count: number }[]>([])

// 奖励编辑弹窗
const rewardDialogVisible = ref(false)
const rewardInput = ref(0)

function openRewardDialog() {
  rewardInput.value = stats.value.daily_reward
  rewardDialogVisible.value = true
}

async function handleUpdateReward() {
  try {
    await adminApi.checkin.updateReward(rewardInput.value)
    stats.value.daily_reward = rewardInput.value
    rewardDialogVisible.value = false
    ElMessage.success('奖励币数已更新')
  } catch {
    ElMessage.error('更新失败，请重试')
  }
}

async function loadStats() {
  try {
    const data: any = await adminApi.checkin.stats()
    if (data) {
      stats.value = { ...stats.value, ...data }
    }
  } catch {}
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (dateRange.value?.[0]) params.date_from = dateRange.value[0]
    if (dateRange.value?.[1]) params.date_to = dateRange.value[1]
    if (search.value) params.search = search.value

    const res: any = await adminApi.checkin.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0

    // 如果接口返回了趋势数据则使用
    if (res.trend_data) {
      trendData.value = res.trend_data
    }
  } catch {} finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadData()
}

function handleReset() {
  dateRange.value = null
  search.value = ''
  page.value = 1
  loadData()
}

function handlePageChange(val: number) {
  page.value = val
  loadData()
}

function handleSizeChange(val: number) {
  pageSize.value = val
  page.value = 1
  loadData()
}

// 趋势图最大值
const trendMax = computed(() => Math.max(...trendData.value.map(d => d.count), 1))

onMounted(() => {
  loadStats()
  loadData()
})
</script>

<template>
  <div class="checkin-manage" v-loading="loading">
    <!-- Page Title -->
    <div class="page-header">
      <h1 class="page-title">签到记录管理</h1>
      <p class="page-subtitle">查看和管理用户签到数据</p>
    </div>

    <!-- 统计卡片区 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value">{{ stats.today_count }}</span>
              <span class="stat-label">今日签到人数</span>
            </div>
            <div class="stat-icon-wrap" style="background: rgba(34,197,94,0.12); color: #22C55E;">
              <el-icon :size="26"><Calendar /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_checkins }}</span>
              <span class="stat-label">总签到次数</span>
            </div>
            <div class="stat-icon-wrap" style="background: rgba(59,130,246,0.12); color: #3B82F6;">
              <el-icon :size="26"><Document /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value">{{ stats.unique_users }}</span>
              <span class="stat-label">签到用户数</span>
            </div>
            <div class="stat-icon-wrap" style="background: rgba(168,85,247,0.12); color: #A855F7;">
              <el-icon :size="26"><User /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-reward">
          <div class="stat-card-inner">
            <div class="stat-info">
              <div class="reward-value-row">
                <span class="stat-value reward-value">{{ stats.daily_reward }}</span>
                <el-button size="small" type="primary" link @click="openRewardDialog" class="edit-btn">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </div>
              <span class="stat-label">每日奖励币数</span>
            </div>
            <div class="stat-icon-wrap" style="background: rgba(245,158,11,0.12); color: #F59E0B;">
              <el-icon :size="26"><Coin /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选区 -->
    <div class="panel filter-panel">
      <div class="filter-row">
        <div class="filter-item">
          <label>日期范围</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="~"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px;"
            :clearable="true"
          />
        </div>
        <div class="filter-item">
          <label>用户名</label>
          <el-input v-model="search" placeholder="输入用户名搜索" clearable style="width: 200px;" @keyup.enter="handleSearch" />
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="panel table-panel">
      <div class="panel-header">
        <h3 class="panel-title">签到记录列表</h3>
        <span class="panel-badge">共 {{ total }} 条</span>
      </div>
      <el-table :data="tableData" class="admin-table" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="table-user">
              <div class="table-avatar-sm">{{ row.username ? row.username.charAt(0).toUpperCase() : '?' }}</div>
              <span>{{ row.username || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="checkin_date" label="签到日期" min-width="120" />
        <el-table-column prop="coins_earned" label="获得虚拟币" min-width="110">
          <template #default="{ row }">
            <span class="coin-text">{{ row.coins_earned || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="签到时间" min-width="170" />
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 15, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 近7天趋势图 -->
    <div class="panel trend-panel">
      <div class="panel-header">
        <h3 class="panel-title">近7天签到趋势</h3>
        <span class="panel-badge">柱状图</span>
      </div>
      <div class="chart-area">
        <div class="bar-chart" v-if="trendData.length">
          <div class="bar-chart-body">
            <div class="y-axis">
              <span>{{ trendMax }}</span>
              <span>0</span>
            </div>
            <div class="bars-container">
              <div class="bar-group" v-for="(item, index) in trendData" :key="index">
                <div class="bar-wrapper">
                  <div
                    class="bar"
                    :style="{ height: `${(item.count / trendMax) * 100}%` }"
                    :title="`${item.date}: ${item.count}人`"
                  >
                    <span class="bar-value">{{ item.count }}</span>
                  </div>
                </div>
                <span class="bar-label">{{ item.date.slice(5) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-hint">暂无趋势数据</div>
      </div>
    </div>

    <!-- 奖励修改弹窗 -->
    <el-dialog
      v-model="rewardDialogVisible"
      title="修改每日奖励币数"
      width="420px"
      :close-on-click-modal="false"
      class="reward-dialog"
    >
      <div class="dialog-content">
        <p class="dialog-tip">设置用户每日签到可获得的虚拟币数量</p>
        <el-input-number
          v-model="rewardInput"
          :min="0"
          :max="9999"
          :step="1"
          controls-position="right"
          size="large"
          style="width: 100%;"
        />
      </div>
      <template #footer>
        <el-button @click="rewardDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateReward">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

.checkin-manage {
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

/* ── 统计卡片 ── */
.stat-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 14px;
  padding: 22px;
  border: 1px solid rgba(30,41,59,0.5);
  background: rgba(15,23,42,0.6);
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
  border-color: rgba(34,197,94,0.15);
}

.stat-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info {
  flex: 1;
}

.stat-value {
  display: block;
  font-size: 30px;
  font-weight: 700;
  color: #22C55E;
  line-height: 1.15;
  letter-spacing: -0.5px;
  font-family: 'Fira Code', monospace;
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

.reward-value-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.reward-value {
  font-size: 28px;
}

.edit-btn {
  padding: 2px !important;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.edit-btn:hover {
  opacity: 1;
}

/* ── 面板通用 ── */
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

/* ── 筛选区 ── */
.filter-panel {
  padding: 18px 22px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-item label {
  font-size: 13px;
  color: #94A3B8;
  white-space: nowrap;
  font-weight: 500;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

/* ── 表格区 ── */
.table-panel {
  padding: 0;
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

.coin-text {
  color: #F59E0B;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 22px;
}

.pagination-wrap :deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: #94A3B8;
  --el-pagination-button-bg-color: rgba(30,41,59,0.45);
  --el-pagination-hover-color: #22C55E;
  --el-pagination-button-color: #CBD5E1;
}

/* ── 趋势图 ── */
.trend-panel .chart-area {
  padding: 22px;
}

.bar-chart {
  width: 100%;
}

.bar-chart-body {
  display: flex;
  align-items: flex-end;
  gap: 0;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 12px;
  height: 200px;
  width: 36px;
  flex-shrink: 0;
}

.y-axis span {
  font-size: 11px;
  color: #64748B;
  font-family: 'Fira Code', monospace;
}

.bars-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex: 1;
  height: 200px;
  padding-bottom: 24px;
  border-left: 1px solid rgba(30,41,59,0.5);
  border-bottom: 1px solid rgba(30,41,59,0.5);
  position: relative;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
  height: 100%;
  justify-content: flex-end;
}

.bar-wrapper {
  width: 100%;
  height: calc(100% - 24px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 70%;
  min-width: 24px;
  max-width: 48px;
  background: linear-gradient(180deg, #22C55E 0%, rgba(34,197,94,0.4) 100%);
  border-radius: 6px 6px 2px 2px;
  position: relative;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.bar:hover {
  background: linear-gradient(180deg, #16A34A 0%, rgba(22,163,74,0.5) 100%);
  box-shadow: 0 0 12px rgba(34,197,94,0.3);
}

.bar-value {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #22C55E;
  font-family: 'Fira Code', monospace;
  white-space: nowrap;
}

.bar-label {
  font-size: 11px;
  color: #64748B;
  font-family: 'Fira Code', monospace;
  margin-top: 6px;
  white-space: nowrap;
}

.empty-hint {
  padding: 40px 22px;
  text-align: center;
  color: #64748B;
  font-size: 14px;
}

/* ── 弹窗 ── */
.dialog-content {
  padding: 10px 0 20px;
}

.dialog-tip {
  font-size: 13px;
  color: #94A3B8;
  margin: 0 0 16px;
}

.reward-dialog :deep(.el-dialog) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
}

.reward-dialog :deep(.el-dialog__title) {
  color: #F8FAFC;
  font-weight: 600;
}

.reward-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

.reward-dialog :deep(.el-input-number) {
  --el-input-bg-color: rgba(30,41,59,0.5);
  --el-input-border-color: #334155;
  --el-input-text-color: #F8FAFC;
}

.reward-dialog :deep(.el-input-number .el-input__inner) {
  color: #F8FAFC;
  font-family: 'Fira Code', monospace;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

@media (max-width: 992px) {
  .stat-row .el-col {
    margin-bottom: 16px;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-actions {
    margin-left: 0;
  }
}
</style>
