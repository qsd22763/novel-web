<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Wallet, Search, Refresh, DataLine, Coin,
  Ticket, Calendar, CircleCheck, CircleClose, Warning, InfoFilled,
} from '@element-plus/icons-vue'
import { adminApi } from '../../api'

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)

const stats = ref({
  total_orders: 0,
  paid_orders: 0,
  total_revenue: 0,
  monthly_count: 0,
  quarterly_count: 0,
  yearly_count: 0,
})

const queryParams = reactive({
  page: 1,
  page_size: 50,
  status: '',
  plan_type: '',
  search: '',
})

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待支付', value: 'pending' },
  { label: '已支付', value: 'paid' },
  { label: '已过期', value: 'expired' },
  { label: '已取消', value: 'cancelled' },
]

const planTypeOptions = [
  { label: '全部', value: '' },
  { label: '月卡', value: 'monthly' },
  { label: '季卡', value: 'quarterly' },
  { label: '年卡', value: 'yearly' },
]

const STATUS_MAP: Record<string, { type: '' | 'success' | 'info' | 'warning' | 'danger'; label: string }> = {
  pending: { type: 'warning', label: '待支付' },
  paid: { type: 'success', label: '已支付' },
  expired: { type: 'info', label: '已过期' },
  cancelled: { type: 'danger', label: '已取消' },
}

const PLAN_TYPE_MAP: Record<string, string> = {
  monthly: '月卡',
  quarterly: '季卡',
  yearly: '年卡',
}

function formatMoney(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : (amount || 0)
  return num.toFixed(2)
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

async function loadStats() {
  try {
    const data: any = await adminApi.order.stats()
    if (data) {
      // 后端返回 by_plan: [{key:'monthly',count:N}, ...] → 转为 flat 字段
      const planMap = {}
      if (Array.isArray(data.by_plan)) {
        for (const p of data.by_plan) { planMap[p.key] = p.count }
      }
      stats.value = {
        ...stats.value,
        ...data,
        monthly_count: planMap.monthly || 0,
        quarterly_count: planMap.quarterly || 0,
        yearly_count: planMap.yearly || 0,
      }
    }
  } catch (e) {
    console.error('加载订单统计失败:', e)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: queryParams.page,
      page_size: queryParams.page_size,
    }
    if (queryParams.status) params.status = queryParams.status
    if (queryParams.plan_type) params.plan_type = queryParams.plan_type
    if (queryParams.search) params.search = queryParams.search

    const data: any = await adminApi.order.list(params)
    // 兼容 DRF 分页 {results:[], count:N} 和非分页直接数组两种格式
    if (Array.isArray(data)) {
      tableData.value = data
      total.value = data.length
    } else if (data && data.results) {
      tableData.value = data.results
      total.value = data.count || data.results.length
    } else {
      // 兜底：如果返回的是单个对象或异常格式
      tableData.value = Array.isArray(data) ? data : (data ? [data] : [])
      total.value = tableData.value.length
    }
  } catch (e) {
    console.error('加载订单列表失败:', e)
    ElMessage.error('加载订单列表失败: ' + (e as Error)?.message)
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryParams.page = 1
  loadData()
}

function handleReset() {
  queryParams.status = ''
  queryParams.plan_type = ''
  queryParams.search = ''
  queryParams.page = 1
  loadData()
}

function handleRefresh() {
  loadStats()
  loadData()
  ElMessage.success('数据已刷新')
}

function handleSizeChange(val: number) {
  queryParams.page_size = val
  queryParams.page = 1
  loadData()
}

function handleCurrentChange(val: number) {
  queryParams.page = val
  loadData()
}

onMounted(() => {
  loadStats()
  loadData()
})
</script>

<template>
  <div class="order-manage" v-loading="loading">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon :size="22" class="title-icon"><Wallet /></el-icon>
          充值订单管理
        </h1>
        <span class="total-count" style="font-family:'Fira Code',monospace">
          共 <em>{{ total }}</em> 条订单
        </span>
      </div>
      <div class="header-right">
        <el-button @click="handleRefresh" :icon="Refresh" type="primary" class="refresh-btn">
          刷新
        </el-button>
      </div>
    </div>

    <!-- Stat Cards -->
    <el-row :gutter="20" class="stat-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-total">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value" style="font-family:'Fira Code',monospace;color:#22C55E">{{ stats.total_orders }}</span>
              <span class="stat-label">总订单数</span>
            </div>
            <div class="stat-icon-wrap" style="background:rgba(34,197,94,0.12);color:#22C55E">
              <el-icon :size="24"><DataLine /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-paid">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value" style="font-family:'Fira Code',monospace;color:#3B82F6">{{ stats.paid_orders }}</span>
              <span class="stat-label">已支付订单</span>
            </div>
            <div class="stat-icon-wrap" style="background:rgba(59,130,246,0.12);color:#3B82F6">
              <el-icon :size="24"><CircleCheck /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-revenue">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value" style="font-family:'Fira Code',monospace;color:#F59E0B">&yen;{{ formatMoney(stats.total_revenue) }}</span>
              <span class="stat-label">总营收金额</span>
            </div>
            <div class="stat-icon-wrap" style="background:rgba(245,158,11,0.12);color:#F59E0B">
              <el-icon :size="24"><Coin /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card stat-card-plans">
          <div class="stat-card-inner">
            <div class="stat-info">
              <span class="stat-value" style="font-family:'Fira Code',monospace;color:#A855F7;font-size:18px;line-height:1.5">
                月{{ stats.monthly_count }} / 季{{ stats.quarterly_count }} / 年{{ stats.yearly_count }}
              </span>
              <span class="stat-label">套餐销量分布</span>
            </div>
            <div class="stat-icon-wrap" style="background:rgba(168,85,247,0.12);color:#A855F7">
              <el-icon :size="24"><Ticket /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-item">
          <label class="filter-label">订单状态</label>
          <el-select v-model="queryParams.status" placeholder="全部状态" clearable class="filter-select" popper-class="dark-select-dropdown">
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </div>
        <div class="filter-item">
          <label class="filter-label">套餐类型</label>
          <el-select v-model="queryParams.plan_type" placeholder="全部类型" clearable class="filter-select" popper-class="dark-select-dropdown">
            <el-option v-for="opt in planTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </div>
        <div class="filter-item filter-search">
          <label class="filter-label">搜索</label>
          <el-input v-model="queryParams.search" placeholder="订单号 / 用户名" :prefix-icon="Search" clearable class="search-input" @keyup.enter="handleSearch" />
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="handleSearch" :icon="Search" class="query-btn">查询</el-button>
          <el-button @click="handleReset" plain class="reset-btn">重置</el-button>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <el-table
        :data="tableData"
        stripe
        class="order-table"
        row-class-name="order-row"
      >
        <el-table-column prop="id" label="ID" width="65" align="center">
          <template #default="{ row }">
            <span style="font-family:'Fira Code',monospace;color:#64748B;font-size:12px">#{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="订单号" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="font-family:'Fira Code',monospace;font-size:12px;color:#CBD5E1">{{ row.order_no }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="username" label="用户名" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.username || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="plan_type" label="套餐类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              round
              size="small"
              effect="dark"
              :type="row.plan_type === 'yearly' ? 'danger' : row.plan_type === 'quarterly' ? 'warning' : ''"
              class="plan-tag"
            >{{ PLAN_TYPE_MAP[row.plan_type] || row.plan_type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额(元)" width="100" align="right">
          <template #default="{ row }">
            <span class="amount-cell">&yen;{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="95" align="center">
          <template #default="{ row }">
            <el-tag
              :type="STATUS_MAP[row.status]?.type"
              size="small"
              round
              effect="dark"
              class="status-tag"
              :class="'status-tag--' + row.status"
            >{{ STATUS_MAP[row.status]?.label || row.status }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="paid_at" label="支付时间" width="155">
          <template #default="{ row }">
            <span class="time-cell" style="font-family:'Fira Code',monospace;font-size:12px">{{ row.paid_at ? formatDate(row.paid_at) : '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="expire_at" label="到期时间" width="155">
          <template #default="{ row }">
            <span class="time-cell" style="font-family:'Fira Code',monospace;font-size:12px">{{ row.expire_at ? formatDate(row.expire_at) : '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="155">
          <template #default="{ row }">
            <span class="time-cell" style="font-family:'Fira Code',monospace;font-size:12px">{{ row.created_at ? formatDate(row.created_at) : '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :page-sizes="[15, 30, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="dark-pagination"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.order-manage {
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding-bottom: 32px;
}

/* ===== PAGE HEADER ===== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
  padding: 0 2px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.3px;
}

.title-icon {
  color: #22C55E;
}

.total-count {
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
}

.total-count em {
  color: #22C55E;
  font-style: normal;
  font-weight: 700;
  font-size: 15px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(34,197,94,0.05));
  border-color: rgba(34,197,94,0.35);
  color: #22C55E;
}

.refresh-btn:hover {
  background: linear-gradient(135deg, rgba(34,197,94,0.25), rgba(34,197,94,0.1));
  box-shadow: 0 0 20px rgba(34,197,94,0.15);
}

/* ===== STAT CARDS ===== */
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 14px;
  padding: 20px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(30,41,59,0.5);
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
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.5px;
}

.stat-label {
  display: block;
  font-size: 12.5px;
  color: #94A3B8;
  font-weight: 500;
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ===== FILTER SECTION ===== */
.filter-section {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  padding: 18px 22px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.filter-select {
  width: 150px;
}

.filter-search {
  flex: 1;
  max-width: 280px;
}

.search-input {
  width: 100%;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.query-btn {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  border: none;
  font-weight: 600;
}

.query-btn:hover {
  background: linear-gradient(135deg, #16A34A, #15803D);
  box-shadow: 0 4px 16px rgba(34,197,94,0.3);
}

.reset-btn {
  border-color: #334155;
  color: #94A3B8;
  background: transparent;
}

.reset-btn:hover {
  border-color: #475569;
  color: #E2E8F0;
}

/* ===== TABLE WRAPPER ===== */
.table-wrapper {
  position: relative;
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  overflow: hidden;
  padding: 4px;
}

/* ===== ORDER TABLE ===== */
.order-table {
  --el-table-bg-color: #020617;
  --el-table-tr-bg-color: #020617;
  --el-table-header-bg-color: rgba(15,23,42,0.8);
  --el-table-row-hover-bg-color: rgba(30,41,59,0.5);
  --el-table-border-color: #1E293B;
  --el-table-text-color: #E2E8F0;
  --el-table-header-text-color: #94A3B8;
  font-size: 13px;
  border: none;
  width: 100%;
  background: #020617 !important;
}

.order-table :deep(.el-table__inner-wrapper) {
  background: #020617 !important;
}

.order-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.order-table :deep(th.el-table__cell) {
  font-weight: 650;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748B !important;
  background: rgba(15,23,42,0.6) !important;
  border-bottom: 1px solid #1E293B !important;
  padding: 12px 0;
}

.order-table :deep(td.el-table__cell) {
  border-bottom: 1px solid rgba(30,41,59,0.4);
  padding: 12px 0;
  vertical-align: middle;
  background: #020617 !important;
}

.order-table :deep(.el-table__body tr) {
  cursor: default;
  transition: all 0.2s ease;
  position: relative;
}

.order-table :deep(.el-table__body tr::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: linear-gradient(180deg, #22C55E, #16A34A);
  border-radius: 0 3px 3px 0;
  transition: width 0.2s ease;
}

.order-table :deep(.el-table__body tr:hover::before) {
  width: 3px;
}

.order-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(30,41,59,0.2) !important;
}

.order-table :deep(.el-table__empty-text) {
  color: #64748B;
}

/* Amount Cell */
.amount-cell {
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  font-weight: 700;
  color: #F59E0B;
}

/* Plan Tag */
.plan-tag {
  font-size: 11.5px !important;
  font-weight: 600 !important;
  height: 22px !important;
  line-height: 20px !important;
  padding: 0 10px !important;
}

/* Status Tag */
.status-tag {
  font-size: 11px !important;
  font-weight: 600 !important;
}

.status-tag--paid {
  background: #22C55E !important;
  border-color: #22C55E !important;
}

.time-cell {
  color: #64748B;
  font-weight: 400;
}

/* ===== PAGINATION ===== */
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px 8px;
}

.dark-pagination :deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: #94A3B8;
  --el-pagination-button-bg-color: #1E293B;
  --el-pagination-hover-color: #22C55E;
}

.dark-pagination :deep(.el-pager li) {
  background: transparent;
  color: #94A3B8;
  border-radius: 6px;
  min-width: 32px;
  font-weight: 500;
}

.dark-pagination :deep(.el-pager li.is-active) {
  background: #22C55E !important;
  color: #fff !important;
  font-weight: 700;
}

.dark-pagination :deep(.el-pager li:hover:not(.is-active)) {
  color: #22C55E;
}

.dark-pagination :deep(.btn-prev),
.dark-pagination :deep(.btn-next) {
  background: transparent;
  border-radius: 6px;
  color: #94A3B8;
}

.dark-pagination :deep(.el-input__wrapper) {
  background: #1E293B;
  box-shadow: none;
  border: 1px solid #334155;
  border-radius: 6px;
}

.dark-pagination :deep(.el-pagination__sizes) {
  color: #64748B;
}

.dark-pagination :deep(.el-pagination__total) {
  color: #64748B;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 992px) {
  .filter-row {
    flex-wrap: wrap;
  }

  .filter-search {
    max-width: 100%;
    flex: 1 1 100%;
  }

  .filter-actions {
    margin-left: 0;
    width: 100%;
  }

  .stat-row .el-col {
    margin-bottom: 12px;
  }
}
</style>
