<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, ImageProps } from 'element-plus'
import {
  Notebook, Search, Refresh, Download, Filter,
  Edit, Check, Close, Delete, View, DocumentCopy,
  Warning, CircleCheck, CircleClose, InfoFilled,
  DataLine, TrendCharts, Reading, ChatDotRound,
  Star, Timer, ArrowDown, SetUp
} from '@element-plus/icons-vue'
import request from '../../utils/request'

interface AdminNovel {
  id: number; title: string; author: string; cover: string
  description: string; category: string; tags: string
  status: number; status_display: string
  audit_status: number; audit_status_display: string
  word_count: number; view_count: number; recommend: number
  chapter_count?: number; comment_count?: number
  created_at: string; updated_at: string
}

const CATEGORIES = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']

const CATEGORY_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  '玄幻': { bg: 'rgba(168,85,247,0.15)', color: '#A855F7', border: 'rgba(168,85,247,0.3)' },
  '都市': { bg: 'rgba(59,130,246,0.15)', color: '#3B82F6', border: 'rgba(59,130,246,0.3)' },
  '穿越': { bg: 'rgba(236,72,153,0.15)', color: '#EC4899', border: 'rgba(236,72,153,0.3)' },
  '科幻': { bg: 'rgba(6,182,212,0.15)', color: '#06B6D4', border: 'rgba(6,182,212,0.3)' },
  '游戏': { bg: 'rgba(34,197,94,0.15)', color: '#22C55E', border: 'rgba(34,197,94,0.3)' },
  '悬疑': { bg: 'rgba(245,158,11,0.15)', color: '#F59E0B', border: 'rgba(245,158,11,0.3)' },
  '武侠': { bg: 'rgba(239,68,68,0.15)', color: '#EF4444', border: 'rgba(239,68,68,0.3)' },
  '历史': { bg: 'rgba(139,92,246,0.15)', color: '#8B5CF6', border: 'rgba(139,92,246,0.3)' },
}

const STATUS_MAP: Record<number, { type: '' | 'success' | 'info' | 'warning' | 'danger'; label: string }> = {
  0: { type: '', label: '连载中' },
  1: { type: 'success', label: '已完结' },
  2: { type: 'info', label: '已下架' },
}

const AUDIT_STATUS_MAP: Record<number, { type: '' | 'success' | 'warning' | 'danger' | 'info'; label: string }> = {
  0: { type: 'info', label: '草稿' },
  1: { type: 'warning', label: '审核中' },
  2: { type: 'success', label: '已发布' },
  3: { type: 'danger', label: '驳回' },
}

const loading = ref(false)
const tableData = ref<AdminNovel[]>([])
const total = ref(0)
const selectedRows = ref<AdminNovel[]>([])
const filterExpanded = ref(true)

const queryParams = reactive({
  page: 1,
  page_size: 12,
  category: '',
  status: undefined as number | undefined,
  audit_status: undefined as number | undefined,
  word_count_min: undefined as number | undefined,
  word_count_max: undefined as number | undefined,
  search: '',
  ordering: '-updated_at',
})

const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editingBook = ref<AdminNovel | null>(null)
const activeEditTab = ref('basic')

const editForm = reactive({
  title: '',
  author: '',
  category: '',
  tags: '',
  description: '',
  status: 0,
  cover: '',
})

const editRules: FormRules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }, { min: 1, max: 100, message: '书名长度1-100字符', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者名', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

const drawerVisible = ref(false)
const detailBook = ref<AdminNovel | null>(null)
const detailChapters = ref<any[]>([])
const detailComments = ref<any[]>([])
const batchCategoryPopoverVisible = ref(false)
const selectedBatchCategory = ref('')

const tableRef = ref()

function formatCount(num: number): string {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return String(num)
}

function getCategoryStyle(category: string) {
  return CATEGORY_COLORS[category] || { bg: 'rgba(148,163,184,0.15)', color: '#94A3B8', border: 'rgba(148,163,184,0.3)' }
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

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: queryParams.page,
      page_size: queryParams.page_size,
    }
    if (queryParams.category) params.category = queryParams.category
    if (queryParams.status != null && queryParams.status !== '') params.status = queryParams.status
    if (queryParams.audit_status != null && queryParams.audit_status !== '') params.audit_status = queryParams.audit_status
    if (queryParams.word_count_min != null && queryParams.word_count_min !== '') params.word_count_min = queryParams.word_count_min
    if (queryParams.word_count_max != null && queryParams.word_count_max !== '') params.word_count_max = queryParams.word_count_max
    if (queryParams.search) params.search = queryParams.search
    if (queryParams.ordering) params.ordering = queryParams.ordering

    const data: any = await request.get('/admin/books/', { params })
    tableData.value = data.results || []
    total.value = data.count || 0
  } catch (e) {
    console.error('加载书籍列表失败:', e)
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryParams.page = 1
  fetchData()
}

function handleReset() {
  queryParams.category = ''
  queryParams.status = undefined
  queryParams.audit_status = undefined
  queryParams.word_count_min = undefined
  queryParams.word_count_max = undefined
  queryParams.search = ''
  queryParams.ordering = '-updated_at'
  queryParams.page = 1
  fetchData()
}

function handleRefresh() {
  fetchData()
  ElMessage.success('数据已刷新')
}

async function handleExport() {
  try {
    const params: Record<string, string> = {}
    if (queryParams.category) params.category = queryParams.category
    if (queryParams.status != null && queryParams.status !== '') params.status = String(queryParams.status)
    if (queryParams.audit_status != null && queryParams.audit_status !== '') params.audit_status = String(queryParams.audit_status)
    if (queryParams.search) params.search = queryParams.search
    if (queryParams.word_count_min) params.word_count_min = queryParams.word_count_min
    if (queryParams.word_count_max) params.word_count_max = queryParams.word_count_max

    const res: any = await request.get('/admin/books/export_excel/', {
      params,
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    const now = new Date()
    const filename = `书籍列表_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}.xlsx`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败，请重试')
  }
}

function handleSizeChange(val: number) {
  queryParams.page_size = val
  queryParams.page = 1
  fetchData()
}

function handleCurrentChange(val: number) {
  queryParams.page = val
  fetchData()
}

function handleSelectionChange(rows: AdminNovel[]) {
  selectedRows.value = rows
}

function openEditDialog(row?: AdminNovel) {
  if (row) {
    editingBook.value = row
    Object.assign(editForm, {
      title: row.title,
      author: row.author,
      category: row.category,
      tags: row.tags,
      description: row.description,
      status: row.status,
      cover: row.cover,
    })
  } else {
    editingBook.value = null
    Object.assign(editForm, { title: '', author: '', category: '', tags: '', description: '', status: 0, cover: '' })
  }
  activeEditTab.value = 'basic'
  editDialogVisible.value = true
  nextTick(() => editFormRef.value?.clearValidate())
}

async function handleSubmitEdit() {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (editingBook.value) {
        await request.patch(`/admin/books/${editingBook.value.id}/`, editForm)
        ElMessage.success('更新成功')
      } else {
        ElMessage.success('创建成功')
      }
      editDialogVisible.value = false
      fetchData()
    } catch {
      ElMessage.error(editingBook.value ? '更新失败' : '创建失败')
    }
  })
}

function openDetailDrawer(row: AdminNovel) {
  detailBook.value = row
  detailChapters.value = Array.from({ length: Math.min(row.chapter_count || 5, 5) }, (_, i) => ({
    id: i + 1,
    title: `第${i + 1}章 ${['启程', '初遇', '危机', '转折', '成长'][i] || '新篇章'}`,
    word_count: Math.floor(Math.random() * 3000) + 2000,
    created_at: new Date(Date.now() - i * 86400000 * 3).toISOString(),
  }))
  detailComments.value = [
    { id: 1, username: '读者甲', content: '非常精彩！期待后续更新', rating: 5, created_at: '2026-05-30T10:00:00Z' },
    { id: 2, username: '书虫乙', content: '文笔不错，情节紧凑', rating: 4, created_at: '2026-05-29T15:30:00Z' },
  ]
  drawerVisible.value = true
}

async function handleAuditAction(id: number, status: number) {
  const actionText = status === 2 ? '通过' : '驳回'
  try {
    await ElMessageBox.confirm(`确定要${actionText}审核该书籍吗？`, '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: status === 2 ? 'success' : 'warning',
    })
    await request.post('/admin/books/batch_audit/', { ids: [id], status })
    ElMessage.success(`已${actionText}审核`)
    fetchData()
  } catch {
    // cancelled
  }
}

async function handleTakeDown(id: number) {
  try {
    await ElMessageBox.confirm('确定要下架该书籍吗？下架后用户将无法查看。', '确认下架', {
      confirmButtonText: '确定下架',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.post('/admin/books/batch_take_down/', { ids: [id] })
    ElMessage.success('已下架')
    fetchData()
  } catch {
    // cancelled
  }
}

async function handleBatchAudit(status: number) {
  const ids = selectedRows.value.map(r => r.id)
  const actionText = status === 2 ? '通过' : '驳回'
  try {
    await ElMessageBox.confirm(`确定要批量${actionText}审核选中的 ${ids.length} 项吗？`, '批量审核', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: status === 2 ? 'success' : 'warning',
    })
    await request.post('/admin/books/batch_audit/', { ids, status })
    ElMessage.success(`已批量${actionText}审核 ${ids.length} 项`)
    tableRef.value?.clearSelection()
    fetchData()
  } catch {
    // cancelled
  }
}

async function handleBatchCategory() {
  if (!selectedBatchCategory.value) {
    ElMessage.warning('请选择目标分类')
    return
  }
  const ids = selectedRows.value.map(r => r.id)
  try {
    await request.post('/admin/books/batch_category/', { ids, category: selectedBatchCategory.value })
    ElMessage.success(`已将 ${ids.length} 项书籍分类修改为「${selectedBatchCategory.value}」`)
    batchCategoryPopoverVisible.value = false
    selectedBatchCategory.value = ''
    tableRef.value?.clearSelection()
    fetchData()
  } catch {
    ElMessage.error('批量修改分类失败')
  }
}

async function handleBatchTakeDown() {
  const ids = selectedRows.value.map(r => r.id)
  try {
    await ElMessageBox.confirm(`确定要批量下架选中的 ${ids.length} 项书籍吗？`, '批量下架', {
      confirmButtonText: '确定下架',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await request.post('/admin/books/batch_take_down/', { ids })
    ElMessage.success(`已批量下架 ${ids.length} 项书籍`)
    tableRef.value?.clearSelection()
    fetchData()
  } catch {
    // cancelled
  }
}

function clearSelection() {
  tableRef.value?.clearSelection()
}

function handleSortChange({ prop, order }: { prop: string; order: string | null }) {
  if (order === 'ascending') queryParams.ordering = prop
  else if (order === 'descending') queryParams.ordering = `-${prop}`
  else queryParams.ordering = '-updated_at'
  fetchData()
}

onMounted(() => {
  fetchData()
})

const hasActiveFilters = computed(() => {
  const q = queryParams
  return !!(q.category || q.status !== undefined || q.audit_status !== undefined ||
    q.word_count_min !== undefined || q.word_count_max !== undefined || q.search)
})
</script>

<template>
  <div class="books-management">
    <!-- ===== TOP BAR ===== -->
    <div class="top-bar">
      <div class="top-bar-left">
        <h1 class="page-title">
          <el-icon :size="22" class="title-icon"><Notebook /></el-icon>
          书籍管理
        </h1>
        <span class="total-count" style="font-family:'Fira Code',monospace">
          共 <em>{{ total }}</em> 本书籍
        </span>
      </div>
      <div class="top-bar-right">
        <el-button @click="handleExport" :icon="Download" plain class="action-btn">
          导出数据
        </el-button>
        <el-button @click="handleRefresh" :icon="Refresh" type="primary" class="action-btn refresh-btn">
          刷新
        </el-button>
      </div>
    </div>

    <!-- ===== FILTER SECTION ===== -->
    <el-card shadow="never" class="filter-card" :class="{ collapsed: !filterExpanded }">
      <template #header>
        <div class="filter-header" @click="filterExpanded = !filterExpanded">
          <div class="filter-header-left">
            <el-icon :size="16"><Filter /></el-icon>
            <span>高级筛选</span>
            <el-tag size="small" type="info" round class="filter-count" v-if="hasActiveFilters">已启用</el-tag>
          </div>
          <el-icon :size="14" class="expand-icon" :class="{ rotated: filterExpanded }"><ArrowDown /></el-icon>
        </div>
      </template>
      <transition name="slide-fade">
        <div v-show="filterExpanded" class="filter-body">
          <!-- Row 1 -->
          <div class="filter-row">
            <div class="filter-item">
              <label class="filter-label">分类</label>
              <el-select v-model="queryParams.category" placeholder="全部分类" clearable class="filter-select" popper-class="dark-select-dropdown">
                <el-option v-for="cat in CATEGORIES" :key="cat" :label="cat" :value="cat" />
              </el-select>
            </div>
            <div class="filter-item">
              <label class="filter-label">连载状态</label>
              <el-select v-model="queryParams.status" placeholder="全部状态" clearable class="filter-select" popper-class="dark-select-dropdown">
                <el-option :value="0" label="连载中" />
                <el-option :value="1" label="已完结" />
                <el-option :value="2" label="已下架" />
              </el-select>
            </div>
            <div class="filter-item">
              <label class="filter-label">审核状态</label>
              <el-select v-model="queryParams.audit_status" placeholder="全部状态" clearable class="filter-select" popper-class="dark-select-dropdown">
                <el-option :value="2" label="已发布" />
                <el-option :value="1" label="审核中" />
                <el-option :value="3" label="驳回" />
                <el-option :value="0" label="草稿" />
              </el-select>
            </div>
          </div>
          <!-- Row 2 -->
          <div class="filter-row">
            <div class="filter-item filter-range">
              <label class="filter-label">字数范围</label>
              <div class="range-inputs">
                <el-input-number v-model="queryParams.word_count_min" :min="0" :max="99999999" placeholder="最小" controls-position="right" class="range-num" />
                <span class="range-sep">~</span>
                <el-input-number v-model="queryParams.word_count_max" :min="0" :max="99999999" placeholder="最大" controls-position="right" class="range-num" />
              </div>
            </div>
            <div class="filter-item filter-search">
              <label class="filter-label">搜索</label>
              <el-input v-model="queryParams.search" placeholder="书名 / 作者" :prefix-icon="Search" clearable class="search-input" @keyup.enter="handleSearch" />
            </div>
            <div class="filter-item filter-actions">
              <el-button type="primary" @click="handleSearch" :icon="Search" class="query-btn">查询</el-button>
              <el-button @click="handleReset" plain class="reset-btn">重置</el-button>
            </div>
          </div>
        </div>
      </transition>
    </el-card>

    <!-- ===== DATA TABLE ===== -->
    <div class="table-wrapper">
      <el-table
        ref="tableRef"
        :data="tableData"
        v-loading="loading"
        stripe
        class="books-table"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        row-class-name="books-row"
      >
        <!-- Selection -->
        <el-table-column type="selection" width="46" align="center" />

        <!-- Cover -->
        <el-table-column label="封面" width="80" align="center">
          <template #default="{ row }">
            <div class="cover-cell">
              <el-image
                :src="row.cover || `https://picsum.photos/seed/novel${row.id}/50/70`"
                fit="cover"
                class="cover-img"
                lazy
                :preview-src-list="[row.cover || `https://picsum.photos/seed/novel${row.id}/200/280`]"
                preview-teleported
              >
                <template #placeholder>
                  <div class="cover-skeleton" />
                </template>
                <template #error>
                  <div class="cover-error">
                    <el-icon :size="18"><Notebook /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </template>
        </el-table-column>

        <!-- Title & Author -->
        <el-table-column label="书名" min-width="180" show-overflow-tooltip sortable="custom" prop="title">
          <template #default="{ row }">
            <div class="title-cell">
              <a class="book-title-link" @click="openDetailDrawer(row)">{{ row.title }}</a>
              <span class="book-author">{{ row.author }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- Category -->
        <el-table-column label="分类" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              round
              size="small"
              :style="{
                background: getCategoryStyle(row.category).bg,
                color: getCategoryStyle(row.category).color,
                borderColor: getCategoryStyle(row.category).border,
                border: `1px solid ${getCategoryStyle(row.category).border}`,
              }"
              class="category-tag"
            >{{ row.category }}</el-tag>
          </template>
        </el-table-column>

        <!-- Word Count -->
        <el-table-column label="字数" width="100" align="right" sortable="custom" prop="word_count">
          <template #default="{ row }">
            <span class="num-cell" style="font-family:'Fira Code',monospace">{{ formatCount(row.word_count) }}</span>
          </template>
        </el-table-column>

        <!-- Views -->
        <el-table-column label="阅读量" width="100" align="right" sortable="custom" prop="view_count">
          <template #default="{ row }">
            <span class="num-cell" style="font-family:'Fira Code',monospace">{{ formatCount(row.view_count) }}</span>
          </template>
        </el-table-column>

        <!-- Chapters -->
        <el-table-column label="章节" width="80" align="center" sortable="custom" prop="chapter_count">
          <template #default="{ row }">
            <span class="num-cell" style="font-family:'Fira Code',monospace">{{ row.chapter_count || 0 }}</span>
          </template>
        </el-table-column>

        <!-- Status -->
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="STATUS_MAP[row.status]?.type" size="small" round effect="dark" class="status-tag">
              {{ STATUS_MAP[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- Audit Status -->
        <el-table-column label="审核" width="85" align="center">
          <template #default="{ row }">
            <el-tag :type="AUDIT_STATUS_MAP[row.audit_status]?.type" size="small" round effect="dark" class="audit-tag">
              {{ AUDIT_STATUS_MAP[row.audit_status]?.label }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- Updated At -->
        <el-table-column label="更新时间" width="155" sortable="custom" prop="updated_at">
          <template #default="{ row }">
            <span class="time-cell" style="font-family:'Fira Code',monospace;font-size:12px">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>

        <!-- Actions -->
        <el-table-column label="操作" width="70" align="center" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" class="action-dropdown">
              <el-button link class="dropdown-trigger">
                <el-icon :size="16"><SetUp /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="dark-dropdown-menu">
                  <el-dropdown-item @click="openEditDialog(row)">
                    <el-icon><Edit /></el-icon>
                    <span>编辑信息</span>
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleAuditAction(row.id, 2)" divided v-if="row.audit_status !== 2">
                    <el-icon style="color:#22C55E"><CircleCheck /></el-icon>
                    <span style="color:#22C55E">审核通过</span>
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleAuditAction(row.id, 3)" v-if="row.audit_status !== 3">
                    <el-icon style="color:#EF4444"><CircleClose /></el-icon>
                    <span style="color:#EF4444">审核驳回</span>
                  </el-dropdown-item>
                  <el-dropdown-item @click="handleTakeDown(row.id)" divided v-if="row.status !== 2">
                    <el-icon style="color:#F59E0B"><Warning /></el-icon>
                    <span style="color:#F59E0B">下架</span>
                  </el-dropdown-item>
                  <el-dropdown-item @click="openDetailDrawer(row)" divided>
                    <el-icon style="color:#3B82F6"><View /></el-icon>
                    <span style="color:#3B82F6">查看详情</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :page-sizes="[12, 24, 48, 96]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="dark-pagination"
        />
      </div>
    </div>

    <!-- ===== BATCH ACTION BAR ===== -->
    <transition name="slide-up">
      <div class="batch-bar" v-if="selectedRows.length > 0">
        <div class="batch-info">
          <el-icon :size="16" class="batch-icon"><DocumentCopy /></el-icon>
          已选 <strong style="font-family:'Fira Code',monospace;color:#22C55E">{{ selectedRows.length }}</strong> 项
        </div>
        <div class="batch-actions">
          <el-popover placement="top" :width="180" trigger="click" v-model:visible="batchCategoryPopoverVisible">
            <template #reference>
              <el-button size="small" plain>
                <el-icon><SetUp /></el-icon> 批量改分类
              </el-button>
            </template>
            <div class="batch-category-popover">
              <p class="popover-title">选择目标分类</p>
              <div class="popover-cats">
                <span
                  v-for="cat in CATEGORIES"
                  :key="cat"
                  class="popover-cat-item"
                  :class="{ active: selectedBatchCategory === cat }"
                  @click="selectedBatchCategory = cat"
                >{{ cat }}</span>
              </div>
              <div class="popover-footer">
                <el-button size="small" @click="batchCategoryPopoverVisible = false">取消</el-button>
                <el-button size="small" type="primary" @click="handleBatchCategory">确定</el-button>
              </div>
            </div>
          </el-popover>
          <el-button size="small" type="warning" plain @click="handleBatchTakeDown">
            <el-icon><Delete /></el-icon> 批量下架
          </el-button>
          <el-button size="small" plain @click="clearSelection" class="clear-btn">
            清空选择
          </el-button>
        </div>
      </div>
    </transition>

    <!-- ===== EDIT DIALOG ===== -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editingBook ? '编辑书籍' : '新建书籍'"
      width="800px"
      :close-on-click-modal="false"
      class="edit-dialog"
      destroy-on-close
    >
      <el-tabs v-model="activeEditTab" class="edit-tabs">
        <el-tab-pane label="基本信息" name="basic">
          <el-form
            ref="editFormRef"
            :model="editForm"
            :rules="editRules"
            label-width="80px"
            label-position="top"
            class="edit-form"
          >
            <el-row :gutter="20">
              <el-col :span="16">
                <el-form-item label="书名" prop="title">
                  <el-input v-model="editForm.title" placeholder="请输入书名" maxlength="100" show-word-limit />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="作者" prop="author">
                  <el-input v-model="editForm.author" placeholder="作者名" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="分类" prop="category">
                  <el-select v-model="editForm.category" placeholder="选择分类" class="full-width" popper-class="dark-select-dropdown">
                    <el-option v-for="cat in CATEGORIES" :key="cat" :label="cat" :value="cat" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标签">
                  <el-input v-model="editForm.tags" placeholder="用逗号分隔，如: 热血,冒险" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="简介">
              <el-input v-model="editForm.description" type="textarea" :rows="4" placeholder="书籍简介..." maxlength="500" show-word-limit />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="状态">
                  <el-select v-model="editForm.status" class="full-width" popper-class="dark-select-dropdown">
                    <el-option :value="0" label="连载中" />
                    <el-option :value="1" label="已完结" />
                    <el-option :value="2" label="已下架" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="封面URL">
                  <div class="cover-url-input">
                    <el-input v-model="editForm.cover" placeholder="封面图片地址">
                      <template #append v-if="editForm.cover">
                        <el-image
                          :src="editForm.cover"
                          fit="cover"
                          class="cover-preview-thumb"
                          :preview-src-list="[editForm.cover]"
                          preview-teleported
                        />
                      </template>
                    </el-input>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="数据统计" name="stats">
          <div class="stats-grid" v-if="editingBook">
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(34,197,94,0.12);color:#22C55E">
                <el-icon :size="22"><Reading /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace">{{ formatCount(editingBook.word_count) }}</span>
                <span class="stat-box-label">总字数</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(59,130,246,0.12);color:#3B82F6">
                <el-icon :size="22"><TrendCharts /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace">{{ formatCount(editingBook.view_count) }}</span>
                <span class="stat-box-label">阅读量</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(168,85,247,0.12);color:#A855F7">
                <el-icon :size="22"><DocumentCopy /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace">{{ editingBook.chapter_count || 0 }}</span>
                <span class="stat-box-label">章节数</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(245,158,11,0.12);color:#F59E0B">
                <el-icon :size="22"><ChatDotRound /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace">{{ editingBook.comment_count || 0 }}</span>
                <span class="stat-box-label">评论数</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(236,72,153,0.12);color:#EC4899">
                <el-icon :size="22"><Star /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace">{{ editingBook.recommend || 0 }}</span>
                <span class="stat-box-label">推荐数</span>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-box-icon" style="background:rgba(6,182,212,0.12);color:#06B6D4">
                <el-icon :size="22"><Timer /></el-icon>
              </div>
              <div class="stat-box-info">
                <span class="stat-box-value" style="font-family:'Fira Code',monospace;font-size:13px">{{ formatDate(editingBook.created_at) }}</span>
                <span class="stat-box-label">创建时间</span>
              </div>
            </div>
          </div>
          <div class="stats-empty" v-else>
            <el-empty description="请先保存基本信息后查看统计数据" :image-size="100" />
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitEdit" :loading="false">
          {{ editingBook ? '保存修改' : '创建书籍' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ===== DETAIL DRAWER ===== -->
    <el-drawer
      v-model="drawerVisible"
      :title="detailBook?.title || '书籍详情'"
      direction="rtl"
      size="520px"
      class="detail-drawer"
      :with-header="true"
    >
      <template v-if="detailBook">
        <!-- Cover & Basic Info -->
        <div class="drawer-cover-section">
          <el-image
            :src="detailBook.cover || `https://picsum.photos/seed/novel${detailBook.id}/160/220`"
            fit="cover"
            class="drawer-cover"
            :preview-src-list="[detailBook.cover || `https://picsum.photos/seed/novel${detailBook.id}/400/560`]"
            preview-teleported
          >
            <template #error>
              <div class="drawer-cover-placeholder">
                <el-icon :size="36"><Notebook /></el-icon>
              </div>
            </template>
          </el-image>
          <div class="drawer-book-meta">
            <h2 class="drawer-book-title">{{ detailBook.title }}</h2>
            <p class="drawer-book-author">
              <el-icon><Reading /></el-icon>
              {{ detailBook.author }}
            </p>
            <div class="drawer-tags">
              <el-tag
                round
                size="small"
                :style="{
                  background: getCategoryStyle(detailBook.category).bg,
                  color: getCategoryStyle(detailBook.category).color,
                  borderColor: getCategoryStyle(detailBook.category).border,
                  border: `1px solid ${getCategoryStyle(detailBook.category).border}`,
                }"
              >{{ detailBook.category }}</el-tag>
              <el-tag :type="STATUS_MAP[detailBook.status]?.type" size="small" round effect="dark">
                {{ STATUS_MAP[detailBook.status]?.label }}
              </el-tag>
              <el-tag :type="AUDIT_STATUS_MAP[detailBook.audit_status]?.type" size="small" round effect="dark">
                {{ AUDIT_STATUS_MAP[detailBook.audit_status]?.label }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="drawer-section">
          <h3 class="section-title"><el-icon><DocumentCopy /></el-icon> 简介</h3>
          <p class="section-content">{{ detailBook.description || '暂无简介' }}</p>
        </div>

        <!-- Stats Overview -->
        <div class="drawer-section">
          <h3 class="section-title"><el-icon><DataLine /></el-icon> 数据概览</h3>
          <div class="mini-stats">
            <div class="mini-stat">
              <span class="mini-stat-value" style="font-family:'Fira Code',monospace">{{ formatCount(detailBook.word_count) }}</span>
              <span class="mini-stat-label">字数</span>
            </div>
            <div class="mini-stat">
              <span class="mini-stat-value" style="font-family:'Fira Code',monospace">{{ formatCount(detailBook.view_count) }}</span>
              <span class="mini-stat-label">阅读</span>
            </div>
            <div class="mini-stat">
              <span class="mini-stat-value" style="font-family:'Fira Code',monospace">{{ detailBook.chapter_count || 0 }}</span>
              <span class="mini-stat-label">章节</span>
            </div>
            <div class="mini-stat">
              <span class="mini-stat-value" style="font-family:'Fira Code',monospace">{{ detailBook.recommend || 0 }}</span>
              <span class="mini-stat-label">推荐</span>
            </div>
          </div>
        </div>

        <!-- Chapters List -->
        <div class="drawer-section">
          <h3 class="section-title"><el-icon><DocumentCopy /></el-icon> 章节列表</h3>
          <el-table :data="detailChapters" size="small" class="chapters-sub-table" max-height="240">
            <el-table-column prop="id" label="#" width="45" align="center">
              <template #default="{ row }">
                <span style="font-family:'Fira Code',monospace;font-size:11px;color:#64748B">{{ row.id }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="word_count" label="字数" width="75" align="right">
              <template #default="{ row }">
                <span style="font-family:'Fira Code',monospace;font-size:11px">{{ formatCount(row.word_count) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Comments Preview -->
        <div class="drawer-section">
          <h3 class="section-title"><el-icon><ChatDotRound /></el-icon> 最新评论</h3>
          <div class="comments-preview">
            <div v-for="c in detailComments" :key="c.id" class="comment-entry">
              <div class="comment-entry-head">
                <span class="comment-user-name">{{ c.username }}</span>
                <el-rate v-model="c.rating" disabled size="small" :colors="['#F59E0B','#F59E0B','#F59E0B']" />
              </div>
              <p class="comment-entry-text">{{ c.content }}</p>
            </div>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.books-management {
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding-bottom: 32px;
}

/* ===== TOP BAR ===== */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
  padding: 0 2px;
}

.top-bar-left {
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

.top-bar-right {
  display: flex;
  gap: 10px;
}

.action-btn {
  border-color: #1E293B;
  background: transparent;
  color: #94A3B8;
  font-size: 13px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  border-color: rgba(34,197,94,0.4);
  color: #22C55E;
  background: rgba(34,197,94,0.06);
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

/* ===== FILTER CARD ===== */
.filter-card {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  margin-bottom: 20px;
  overflow: hidden;
  transition: all 0.25s ease;
}

.filter-card.collapsed {
  border-radius: 12px;
}

.filter-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
}

.filter-card :deep(.el-card__header:hover) {
  background: rgba(30,41,59,0.3);
}

.filter-card :deep(.el-card__body) {
  padding: 18px 20px;
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #E2E8F0;
}

.filter-count {
  font-size: 10.5px !important;
  height: 18px;
  line-height: 17px;
  padding: 0 7px !important;
  background: rgba(34,197,94,0.12) !important;
  color: #22C55E !important;
  border-color: rgba(34,197,94,0.25) !important;
}

.expand-icon {
  color: #64748B;
  transition: transform 0.3s ease;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.filter-body {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-fade-enter-active { transition: all 0.25s ease; }
.slide-fade-leave-active { transition: all 0.15s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-8px); }

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 14px;
}

.filter-row:last-child {
  margin-bottom: 0;
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

.filter-range {
  width: 300px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-num {
  width: 120px;
}

.range-sep {
  color: #64748B;
  font-size: 14px;
  font-weight: 500;
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

/* ===== BOOKS TABLE ===== */
.books-table {
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

.books-table :deep(.el-table__inner-wrapper) {
  background: #020617 !important;
}

.books-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.books-table :deep(th.el-table__cell) {
  font-weight: 650;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748B !important;
  background: rgba(15,23,42,0.6) !important;
  border-bottom: 1px solid #1E293B !important;
  padding: 12px 0;
}

.books-table :deep(td.el-table__cell) {
  border-bottom: 1px solid rgba(30,41,59,0.4);
  padding: 12px 0;
  vertical-align: middle;
  background: #020617 !important;
}

.books-table :deep(.el-table__body tr) {
  cursor: default;
  transition: all 0.2s ease;
  position: relative;
}

.books-table :deep(.el-table__body tr::before) {
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

.books-table :deep(.el-table__body tr:hover::before) {
  width: 3px;
}

.books-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(30,41,59,0.2) !important;
}

.books-table :deep(.el-checkbox__inner) {
  background: transparent;
  border-color: #475569;
  border-radius: 4px;
  width: 16px;
  height: 16px;
}

.books-table :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: #22C55E;
  border-color: #22C55E;
}

.books-table :deep(.el-table__empty-text) {
  color: #64748B;
}

/* Cover Cell */
.cover-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.cover-img {
  width: 50px;
  height: 70px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #1E293B;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.cover-img:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.cover-skeleton {
  width: 50px;
  height: 70px;
  border-radius: 4px;
  background: linear-gradient(90deg, #1E293B 25%, #334155 50%, #1E293B 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.cover-error {
  width: 50px;
  height: 70px;
  border-radius: 4px;
  background: #1E293B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}

/* Title Cell */
.title-cell {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.book-title-link {
  font-weight: 600;
  font-size: 13.5px;
  color: #F8FAFC;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-title-link:hover {
  color: #22C55E;
}

.book-author {
  font-size: 11.5px;
  color: #64748B;
  font-weight: 400;
}

/* Category Tag */
.category-tag {
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

.audit-tag {
  font-size: 11px !important;
  font-weight: 600 !important;
}

.num-cell {
  font-size: 13px;
  font-weight: 600;
  color: #CBD5E1;
}

.time-cell {
  color: #64748B;
  font-weight: 400;
}

/* Action Dropdown */
.action-dropdown {
  display: inline-flex;
}

.dropdown-trigger {
  color: #64748B;
  padding: 4px;
}

.dropdown-trigger:hover {
  color: #22C55E;
  background: rgba(34,197,94,0.08);
  border-radius: 6px;
}

.dark-dropdown-menu {
  background: #161d2f !important;
  border: 1px solid #1E293B !important;
  border-radius: 10px !important;
  padding: 6px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
}

.dark-dropdown-menu .el-dropdown-item {
  color: #CBD5E1;
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s ease;
}

.dark-dropdown-menu .el-dropdown-item:hover {
  background: rgba(34,197,94,0.1);
  color: #22C55E;
}

.dark-dropdown-menu .el-dropdown-item.is-divided {
  border-top: 1px solid #1E293B;
  margin-top: 4px;
  padding-top: 8px;
}

/* Pagination */
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

/* ===== BATCH BAR ===== */
.batch-bar {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(15,23,42,0.98));
  border: 1px solid rgba(34,197,94,0.2);
  border-radius: 14px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 60px rgba(34,197,94,0.06);
  animation: slideUpIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes slideUpIn {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.slide-up-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.slide-up-leave-active { transition: all 0.2s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateX(-50%) translateY(20px); }

.batch-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #CBD5E1;
  white-space: nowrap;
}

.batch-icon {
  color: #22C55E;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.batch-actions .el-button {
  font-size: 12px;
  border-radius: 8px;
}

.clear-btn {
  color: #64748B !important;
  border-color: #334155 !important;
}

.clear-btn:hover {
  color: #EF4444 !important;
  border-color: rgba(239,68,68,0.4) !important;
}

/* Batch Category Popover */
.batch-category-popover {
  padding: 4px 0;
}

.popover-title {
  font-size: 12px;
  color: #64748B;
  margin: 0 0 10px;
  font-weight: 600;
}

.popover-cats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.popover-cat-item {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #94A3B8;
  background: #1E293B;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.popover-cat-item:hover {
  color: #E2E8F0;
  border-color: #334155;
}

.popover-cat-item.active {
  background: rgba(34,197,94,0.15);
  color: #22C55E;
  border-color: rgba(34,197,94,0.3);
}

.popover-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #1E293B;
}

/* ===== EDIT DIALOG ===== */
.edit-dialog :deep(.el-dialog) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.edit-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.edit-dialog :deep(.el-dialog__title) {
  color: #F8FAFC;
  font-size: 17px;
  font-weight: 700;
}

.edit-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

.edit-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.edit-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(30,41,59,0.5);
}

/* Edit Tabs */
.edit-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.edit-tabs :deep(.el-tabs__item) {
  color: #64748B;
  font-size: 14px;
  font-weight: 600;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

.edit-tabs :deep(.el-tabs__item.is-active) {
  color: #22C55E;
}

.edit-tabs :deep(.el-tabs__active-bar) {
  background: #22C55E;
  height: 3px;
  border-radius: 2px;
}

.edit-tabs :deep(.el-tabs__nav-wrap::after) {
  background: #1E293B;
}

/* Edit Form */
.edit-form :deep(.el-form-item__label) {
  color: #94A3B8;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding-bottom: 4px;
}

.edit-form :deep(.el-input__wrapper),
.edit-form :deep(.el-textarea__inner) {
  background: #1E293B;
  box-shadow: 0 0 0 1px #334155;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.edit-form :deep(.el-input__wrapper:hover),
.edit-form :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #475569;
}

.edit-form :deep(.el-input__wrapper.is-focus),
.edit-form :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #22C55E, 0 0 0 3px rgba(34,197,94,0.1);
}

.edit-form :deep(.el-input__inner) {
  color: #F8FAFC;
}

.edit-form :deep(.el-textarea__inner) {
  color: #F8FAFC;
  background: #1E293B;
}

.edit-form :deep(.el-select .el-input__wrapper) {
  background: #1E293B;
}

.full-width {
  width: 100%;
}

.cover-url-input :deep(.el-input-group__append) {
  background: #1E293B;
  border-color: #334155;
  padding: 0 6px;
}

.cover-preview-thumb {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.stat-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(30,41,59,0.4);
  border: 1px solid rgba(30,41,59,0.5);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.stat-box:hover {
  border-color: rgba(34,197,94,0.15);
  background: rgba(30,41,59,0.6);
}

.stat-box-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-box-info {
  display: flex;
  flex-direction: column;
}

.stat-box-value {
  font-size: 20px;
  font-weight: 700;
  color: #F8FAFC;
  line-height: 1.2;
}

.stat-box-label {
  font-size: 11.5px;
  color: #64748B;
  font-weight: 500;
  margin-top: 2px;
}

.stats-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.stats-empty :deep(.el-empty__description p) {
  color: #64748B;
}

/* ===== DETAIL DRAWER ===== */
.detail-drawer :deep(.el-drawer) {
  background: #0F172A;
  border-left: 1px solid #1E293B;
}

.detail-drawer :deep(.el-drawer__header) {
  padding: 20px 24px 16px;
  margin-bottom: 0;
  border-bottom: 1px solid rgba(30,41,59,0.5);
  color: #F8FAFC;
  font-size: 17px;
  font-weight: 700;
}

.detail-drawer :deep(.el-drawer__close-btn) {
  color: #64748B;
}

.detail-drawer :deep(.el-drawer__body) {
  padding: 0;
  overflow-y: auto;
}

.drawer-cover-section {
  display: flex;
  gap: 18px;
  padding: 24px;
  border-bottom: 1px solid rgba(30,41,59,0.4);
}

.drawer-cover {
  width: 120px;
  height: 165px;
  border-radius: 8px;
  flex-shrink: 0;
  border: 1px solid #1E293B;
  object-fit: cover;
}

.drawer-cover-placeholder {
  width: 120px;
  height: 165px;
  border-radius: 8px;
  background: #1E293B;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #334155;
}

.drawer-book-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.drawer-book-title {
  font-size: 18px;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
  line-height: 1.3;
}

.drawer-book-author {
  font-size: 13px;
  color: #64748B;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.drawer-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.drawer-section {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(30,41,59,0.3);
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #E2E8F0;
  margin: 0 0 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  color: #22C55E;
  font-size: 16px;
}

.section-content {
  font-size: 13px;
  color: #94A3B8;
  line-height: 1.7;
  margin: 0;
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.mini-stat {
  text-align: center;
  padding: 12px 8px;
  background: rgba(30,41,59,0.35);
  border-radius: 10px;
  border: 1px solid rgba(30,41,59,0.4);
}

.mini-stat-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #F8FAFC;
  line-height: 1.3;
}

.mini-stat-label {
  display: block;
  font-size: 11px;
  color: #64748B;
  margin-top: 3px;
}

/* Chapters Sub Table */
.chapters-sub-table :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(30,41,59,0.4);
  --el-table-border-color: #1E293B;
  --el-table-text-color: #CBD5E1;
  --el-table-header-text-color: #64748B;
  font-size: 12px;
  border: none;
}

.chapters-sub-table :deep(th.el-table__cell) {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 0;
  background: transparent !important;
  border-bottom: 1px solid #1E293B !important;
}

.chapters-sub-table :deep(td.el-table__cell) {
  padding: 8px 0;
  border-bottom: 1px solid rgba(30,41,59,0.3);
}

.chapters-sub-table :deep(.el-table__row:hover > td.el-table__cell) {
  background: rgba(30,41,59,0.3) !important;
}

/* Comments Preview */
.comments-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-entry {
  padding: 12px 14px;
  background: rgba(30,41,59,0.3);
  border-radius: 10px;
  border: 1px solid rgba(30,41,59,0.4);
}

.comment-entry-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.comment-user-name {
  font-size: 12.5px;
  font-weight: 600;
  color: #E2E8F0;
}

.comment-entry-text {
  font-size: 12.5px;
  color: #94A3B8;
  line-height: 1.5;
  margin: 0;
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
  .filter-range {
    width: 100%;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .mini-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
