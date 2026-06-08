<template>
  <div class="review-page">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-pending">
          <div class="stat-number">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-approved">
          <div class="stat-number">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-rejected">
          <div class="stat-number">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-total">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">总计</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card shadow="never" class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input
            v-model="queryParams.search"
            placeholder="搜索书名或作者"
            clearable
            prefix-icon="Search"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="queryParams.audit_status" placeholder="审核状态" clearable @change="handleSearch">
            <el-option label="待审核" value="1" />
            <el-option label="已通过" value="2" />
            <el-option label="已驳回" value="3" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="queryParams.category" placeholder="分类筛选" clearable @change="handleSearch">
            <el-option
              v-for="cat in CATEGORIES"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" icon="Refresh" @click="handleSearch">刷新</el-button>
        </el-col>
      </el-row>

      <!-- 状态标签栏 -->
      <div class="status-tabs">
        <span
          v-for="tab in statusTabs"
          :key="tab.value"
          class="status-tab"
          :class="{ active: queryParams.audit_status === tab.value }"
          @click="switchTab(tab.value)"
        >
          {{ tab.label }}
          <span class="tab-count">{{ tab.count }}</span>
        </span>
      </div>
    </el-card>

    <!-- 审核列表表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="tableData"
        stripe
        border
        highlight-current-row
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="45" align="center" />
        <el-table-column label="书籍信息" min-width="260">
          <template #default="{ row }">
            <div class="book-info">
              <el-image
                :src="row.cover || '/default-cover.png'"
                fit="cover"
                class="book-cover"
                :preview-src-list="[row.cover]"
              >
                <template #error>
                  <div class="cover-placeholder">
                    <el-icon><Notebook /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="book-text">
                <div class="book-title">{{ row.title }}</div>
                <div class="book-author">作者：{{ row.author }}</div>
                <el-tag size="small" :type="getCategoryTagType(row.category)" effect="plain">
                  {{ row.category }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="word_count" label="字数" width="100" align="center">
          <template #default="{ row }">
            {{ formatCount(row.word_count) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="safeAuditType(row.audit_status)" size="small" effect="dark">
              {{ safeAuditLabel(row.audit_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button
                v-if="row.audit_status === 1 || row.audit_status === 3"
                type="success"
                size="small"
                icon="CircleCheck"
                :loading="row._approving"
                @click="handleApprove(row)"
              >通过</el-button>
              <el-button
                v-if="row.audit_status === 1 || row.audit_status === 2"
                type="danger"
                size="small"
                icon="CircleClose"
                :loading="row._rejecting"
                @click="openRejectDialog(row)"
              >驳回</el-button>
              <el-button
                type="primary"
                size="small"
                icon="View"
                text
                @click="previewBook(row)"
              >预览</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 驳回原因弹窗 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="驳回审核"
      width="480px"
      destroy-on-close
    >
      <div class="reject-info">
        <p><strong>书名：</strong>{{ rejectTarget?.title }}</p>
        <p><strong>作者：</strong>{{ rejectTarget?.author }}</p>
      </div>
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="驳回原因" required>
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入驳回原因，将反馈给作者..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="rejectLoading" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 书籍预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="书籍详情预览"
      width="640px"
      destroy-on-close
    >
      <div v-if="previewData" class="preview-content">
        <div class="preview-header">
          <el-image :src="previewData.cover" fit="cover" class="preview-cover" />
          <div class="preview-meta">
            <h3>{{ previewData.title }}</h3>
            <p>作者：{{ previewData.author }}</p>
            <p>分类：{{ previewData.category }}</p>
            <p>字数：{{ formatCount(previewData.word_count) }} | 状态：{{ STATUS_MAP[previewData.status]?.label }}</p>
            <el-tag :type="safeAuditType(previewData.audit_status)" size="small">
              {{ safeAuditLabel(previewData.audit_status) }}
            </el-tag>
          </div>
        </div>
        <el-divider content-position="left">简介</el-divider>
        <p class="preview-desc">{{ previewData.description || '暂无简介' }}</p>
        <el-divider content-position="left">标签</el-divider>
        <div class="preview-tags">
          <el-tag
            v-for="tag in parsedTags(previewData.tags)"
            :key="tag"
            size="small"
            effect="plain"
          >{{ tag }}</el-tag>
          <span v-if="!parsedTags(previewData.tags).length" class="no-tags">暂无标签</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Notebook, Search, CircleCheck, CircleClose, View } from '@element-plus/icons-vue'
import { adminApi } from '../../api'

interface ReviewBook {
  id: number; title: string; author: string; cover: string
  description: string; category: string; tags: string
  status: number; audit_status: number
  word_count: number; view_count: number
  created_at: string; updated_at: string
  _approving?: boolean; _rejecting?: boolean
}

const CATEGORIES = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']

const STATUS_MAP: Record<number, { label: string }> = {
  0: { label: '连载中' },
  1: { label: '已完结' },
  2: { label: '已下架' },
}

const AUDIT_STATUS_MAP: Record<number | string, { type: string; label: string }> = {
  0: { type: 'info', label: '草稿' },
  1: { type: 'warning', label: '待审核' },
  2: { type: 'success', label: '已通过' },
  3: { type: 'danger', label: '已驳回' },
}

/** 安全获取审核状态类型，始终返回 Element Plus 合法 type 字符串 */
function safeAuditType(status: any): string {
  const entry = AUDIT_STATUS_MAP[status]
  return entry?.type || 'info'
}

/** 安全获取审核状态标签 */
function safeAuditLabel(status: any): string {
  const entry = AUDIT_STATUS_MAP[status]
  return entry?.label || '未知'
}

// ── 数据 ──
const loading = ref(false)
const tableData = ref<ReviewBook[]>([])
const total = ref(0)
const selectedRows = ref<ReviewBook[]>([])

const stats = reactive({ pending: 0, approved: 0, rejected: 0, total: 0 })

const statusTabs = computed(() => [
  { value: '', label: '全部', count: stats.total },
  { value: '1', label: '待审核', count: stats.pending },
  { value: '2', label: '已通过', count: stats.approved },
  { value: '3', label: '已驳回', count: stats.rejected },
])

const queryParams = reactive({
  page: 1,
  page_size: 15,
  audit_status: '1',
  search: '',
  category: '',
})

// ── 驳回弹窗 ──
const rejectDialogVisible = ref(false)
const rejectTarget = ref<ReviewBook | null>(null)
const rejectLoading = ref(false)
const rejectForm = reactive({ reason: '' })

// ── 预览弹窗 ──
const previewVisible = ref(false)
const previewData = ref<ReviewBook | null>(null)

// ── 方法 ──

const loadStats = async () => {
  try {
    // 从各状态分别查询总数（只取 count，不取数据）
    const [pendingRes, approvedRes, rejectedRes]: any[] = await Promise.all([
      adminApi.reviewList({ audit_status: '1', page_size: 1 }),
      adminApi.reviewList({ audit_status: '2', page_size: 1 }),
      adminApi.reviewList({ audit_status: '3', page_size: 1 }),
    ])
    stats.pending = pendingRes.count || 0
    stats.approved = approvedRes.count || 0
    stats.rejected = rejectedRes.count || 0
    stats.total = stats.pending + stats.approved + stats.rejected
  } catch {
    // 统计加载失败不影响主列表
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = { ...queryParams }
    if (!params.audit_status) delete params.audit_status
    if (!params.search) delete params.search
    if (!params.category) delete params.category
    const res: any = await adminApi.reviewList(params)
    tableData.value = (res.results || []).map((item: any) => ({
      ...item,
      _approving: false,
      _rejecting: false,
    }))
    total.value = res.count || 0
  } catch (e) {
    console.error('加载审核列表失败:', e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  loadData()
  loadStats()
}

const switchTab = (val: string) => {
  queryParams.audit_status = val
  queryParams.page = 1
  loadData()
}

const handleSelectionChange = (rows: ReviewBook[]) => {
  selectedRows.value = rows
}

// ── 审核操作 ──

const handleApprove = async (row: ReviewBook) => {
  try {
    await ElMessageBox.confirm(
      `确认通过《${row.title}》的审核？通过后将在前台展示。`,
      '审核确认',
      { confirmButtonText: '确认通过', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  row._approving = true
  try {
    await adminApi.approveBook(row.id)
    ElMessage.success(`《${row.title}》审核通过`)
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    row._approving = false
  }
}

const openRejectDialog = (row: ReviewBook) => {
  rejectTarget.value = row
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  if (!rejectTarget.value) return
  rejectLoading.value = true
  try {
    await adminApi.rejectBook(rejectTarget.value.id, rejectForm.reason.trim())
    ElMessage.success(`《${rejectTarget.value.title}》已驳回`)
    rejectDialogVisible.value = false
    loadData()
    loadStats()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '操作失败')
  } finally {
    rejectLoading.value = false
  }
}

// ── 预览 ──

const previewBook = (row: ReviewBook) => {
  previewData.value = row
  previewVisible.value = true
}

// ── 工具函数 ──

const formatCount = (num: number): string => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return String(num)
}

const formatTime = (s: string): string => {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const parsedTags = (tags: string): string[] => {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

const getCategoryTagType = (cat: string): '' | 'success' | 'warning' | 'danger' | 'info' => {
  const map: Record<string, '' | 'success' | 'warning' | 'danger' | 'info'> = {
    '玄幻': '', '都市': 'success', '穿越': 'danger',
    '科幻': 'warning', '游戏': 'success', '悬疑': 'warning',
    '武侠': 'danger', '历史': 'info',
  }
  return map[cat] || ''
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.review-page { padding: 0; }

/* ── 统计卡片 ── */
.stats-row { margin-bottom: 20px; }
.stat-card {
  text-align: center;
  padding: 8px 0;
  border-radius: 10px;
  transition: transform 0.25s;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.3;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.stat-pending .stat-number { color: #E6A23C; }
.stat-approved .stat-number { color: #67C23A; }
.stat-rejected .stat-number { color: #F56C6C; }
.stat-total .stat-number { color: #409EFF; }

/* ── 筛选栏 ── */
.filter-card { margin-bottom: 18px; border-radius: 10px; }

.status-tabs {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-wrap: wrap;
}
.status-tab {
  padding: 5px 16px;
  border-radius: 18px;
  font-size: 13px;
  cursor: pointer;
  background: #f4f4f5;
  color: #606266;
  transition: all 0.25s;
  user-select: none;
}
.status-tab:hover { background: #ecf5ff; color: #409eff; }
.status-tab.active {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  box-shadow: 0 2px 8px rgba(64,158,255,0.35);
}
.tab-count {
  display: inline-block;
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  border-radius: 9px;
  background: rgba(255,255,255,0.3);
  font-size: 11px;
  margin-left: 5px;
  padding: 0 5px;
}
.status-tab:not(.active) .tab-count {
  background: #e9e9eb;
  color: #909399;
}

/* ── 表格 ── */
.table-card { border-radius: 10px; }
.book-info { display: flex; gap: 12px; align-items: center; }
.book-cover {
  width: 50px;
  height: 68px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  flex-shrink: 0;
}
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
  font-size: 22px;
}
.book-text { overflow: hidden; }
.book-title {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}
.book-author {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}
.action-btns { display: flex; justify-content: center; gap: 6px; }

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* ── 驳回弹窗 ── */
.reject-info p { margin: 4px 0; font-size: 14px; color: #606266; }

/* ── 预览弹窗 ── */
.preview-content { padding: 0 10px; }
.preview-header { display: flex; gap: 16px; }
.preview-cover {
  width: 120px;
  height: 160px;
  border-radius: 8px;
  flex-shrink: 0;
}
.preview-meta h3 { margin: 0 0 10px; font-size: 18px; }
.preview-meta p { margin: 5px 0; font-size: 13px; color: #606266; }
.preview-desc {
  line-height: 1.8;
  color: #303133;
  font-size: 14px;
  text-indent: 2em;
  max-height: 200px;
  overflow-y: auto;
}
.preview-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.no-tags { color: #c0c4cc; font-size: 13px; }

@media (max-width: 768px) {
  .stats-row .el-col { margin-bottom: 10px; }
  .book-info { flex-direction: column; align-items: flex-start; }
  .action-btns { flex-direction: column; }
}
</style>
