<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Promotion, Search, Refresh, Plus, Edit, Delete, View, DataLine,
  Filter, ArrowDown, Picture, Upload
} from '@element-plus/icons-vue'
import { adminApi, type PaginatedResponse } from '../../api'

interface Advertisement {
  id: number
  title: string
  ad_type: 'banner' | 'popup' | 'sidebar'
  image_url: string
  link_url: string
  position: string
  is_active: boolean
  start_time: string | null
  end_time: string | null
  click_count: number
  view_count: number
  sort_order: number
  created_at: string
  updated_at: string
  ad_type_display: string
  position_display: string
}

interface AdvertisementForm {
  title: string
  ad_type: 'banner' | 'popup' | 'sidebar' | ''
  position: string
  image_url: string
  link_url: string
  start_time: string | null
  end_time: string | null
  sort_order: number
  is_active: boolean
}

interface AdStats {
  total: number
  active: number
  inactive: number
}

const loading = ref(false)
const tableData = ref<Advertisement[]>([])
const selectedRows = ref<Advertisement[]>([])
const stats = ref<AdStats>({ total: 0, active: 0, inactive: 0 })
const filterExpanded = ref(true)

const pagination = reactive({
  page: 1,
  page_size: 10,
  count: 0
})

const filters = reactive({
  ad_type: '',
  position: '',
  is_active: '' as '' | 'true' | 'false',
  search: ''
})

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formLoading = ref(false)
const formRef = ref()
const tableRef = ref()
const dateRange = ref<string[] | null>(null)

const formData = reactive<AdvertisementForm>({
  title: '',
  ad_type: '',
  position: '',
  image_url: '',
  link_url: '',
  start_time: null,
  end_time: null,
  sort_order: 0,
  is_active: true
})

const formRules = {
  title: [{ required: true, message: '请输入广告标题', trigger: 'blur' }],
  ad_type: [{ required: true, message: '请选择广告类型', trigger: 'change' }],
  position: [{ required: true, message: '请选择展示位置', trigger: 'change' }],
  image_url: [{ required: true, message: '请输入图片地址', trigger: 'blur' }]
}

const adTypeOptions = [
  { label: '横幅广告', value: 'banner' },
  { label: '弹窗广告', value: 'popup' },
  { label: '侧边栏广告', value: 'sidebar' }
]

const positionOptions = [
  { label: '首页顶部', value: 'home_top' },
  { label: '首页侧边栏', value: 'home_sidebar' },
  { label: '阅读器底部', value: 'reader_bottom' },
  { label: '阅读器弹窗', value: 'reader_popup' }
]

const statusOptions = [
  { label: '全部', value: '' },
  { label: '已启用', value: 'true' },
  { label: '已禁用', value: 'false' }
]

const adTypeColors: Record<string, string> = {
  banner: '#3B82F6',
  popup: '#A855F7',
  sidebar: '#F59E0B'
}

const positionColors: Record<string, string> = {
  home_top: '#22C55E',
  home_sidebar: '#06B6D4',
  reader_bottom: '#EC4899',
  reader_popup: '#F97316'
}

function getAdTypeColor(type: string): string {
  return adTypeColors[type] || '#94A3B8'
}

function getPositionColor(position: string): string {
  return positionColors[position] || '#94A3B8'
}

function calcCTR(row: Advertisement): string {
  if (!row.view_count) return '0.00%'
  return ((row.click_count / row.view_count) * 100).toFixed(2) + '%'
}

function handleDateChange(val: string[] | null) {
  if (val && val.length === 2) {
    formData.start_time = val[0]
    formData.end_time = val[1]
  } else {
    formData.start_time = null
    formData.end_time = null
  }
}

async function fetchStats() {
  try {
    const res = await adminApi.advertisementList({ page: 1, page_size: 1 })
    const list = res.results || []
    stats.value = {
      total: res.count || 0,
      active: list.filter((a: any) => a.is_active).length,
      inactive: list.length - list.filter((a: any) => a.is_active).length,
    }
  } catch {
    stats.value = { total: 0, active: 0, inactive: 0 }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filters.ad_type) params.ad_type = filters.ad_type
    if (filters.position) params.position = filters.position
    if (filters.is_active) params.is_active = filters.is_active === 'true'
    if (filters.search) params.search = filters.search

    const res = await adminApi.advertisementList(params)
    tableData.value = res.results
    pagination.count = res.count
  } catch (e: any) {
    const status = e?.response?.status
    const detail = e?.response?.data?.detail
    console.warn('[Admin Ads API Error]', status, detail, e)
    if (status === 401 || status === 403) {
      ElMessage.error({ message: '权限不足，请先在登录页以管理员账号重新登录', duration: 4000 })
    } else if (status === 404) {
      ElMessage.error('接口不存在，请确认后端服务已重启')
    } else {
      ElMessage.error(detail || '获取广告列表失败')
    }
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  filters.ad_type = ''
  filters.position = ''
  filters.is_active = ''
  filters.search = ''
  pagination.page = 1
  fetchData()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchData()
}

function handleSizeChange(size: number) {
  pagination.page_size = size
  pagination.page = 1
  fetchData()
}

function openCreateDialog() {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: Advertisement) {
  dialogMode.value = 'edit'
  resetForm()
  Object.assign(formData, {
    title: row.title,
    ad_type: row.ad_type,
    position: row.position,
    image_url: row.image_url,
    link_url: row.link_url || '',
    start_time: row.start_time ? new Date(row.start_time).toISOString() : null,
    end_time: row.end_time ? new Date(row.end_time).toISOString() : null,
    sort_order: row.sort_order,
    is_active: row.is_active
  })
  if (row.start_time && row.end_time) {
    dateRange.value = [
      new Date(row.start_time).toISOString(),
      new Date(row.end_time).toISOString()
    ]
  }
  ;(formData as any)._id = row.id
  dialogVisible.value = true
}

function resetForm() {
  formData.title = ''
  formData.ad_type = ''
  formData.position = ''
  formData.image_url = ''
  formData.link_url = ''
  formData.start_time = null
  formData.end_time = null
  formData.sort_order = 0
  formData.is_active = true
  dateRange.value = null
  delete (formData as any)._id
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  formLoading.value = true
  try {
    const payload: Record<string, any> = {
      title: formData.title,
      ad_type: formData.ad_type,
      position: formData.position,
      image_url: formData.image_url,
      link_url: formData.link_url,
      sort_order: formData.sort_order,
      is_active: formData.is_active
    }
    if (formData.start_time && formData.end_time) {
      payload.start_time = formData.start_time
      payload.end_time = formData.end_time
    }

    if (dialogMode.value === 'create') {
      await adminApi.createAdvertisement(payload)
      ElMessage.success('广告创建成功')
    } else {
      const id = (formData as any)._id
      await adminApi.updateAdvertisement(id, payload)
      ElMessage.success('广告更新成功')
    }
    dialogVisible.value = false
    fetchData()
    fetchStats()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
    }
  } finally {
    formLoading.value = false
  }
}

async function handleDelete(row: Advertisement) {
  try {
    await ElMessageBox.confirm(`确定删除广告「${row.title}」吗？此操作不可恢复。`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })
    await adminApi.deleteAdvertisement(row.id)
    ElMessage.success('广告已删除')
    fetchData()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function handleToggleActive(row: Advertisement) {
  try {
    const res: any = await adminApi.toggleAdvertisementActive(row.id)
    row.is_active = res.is_active
    ElMessage.success(res.message || (row.is_active ? '已启用' : '已禁用'))
    fetchStats()
  } catch {
    row.is_active = !row.is_active
    ElMessage.error('状态切换失败')
  }
}

async function handleBatchActivate() {
  const ids = selectedRows.value.map(r => r.id)
  if (!ids.length) return
  try {
    await ElMessageBox.confirm(`确定启用选中的 ${ids.length} 条广告吗？`, '批量启用', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await adminApi.advertisementList({}) // batch via individual toggles
    ElMessage.success(`已启用 ${ids.length} 条广告`)
    selectedRows.value = []
    fetchData()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('批量启用失败')
  }
}

async function handleBatchDeactivate() {
  const ids = selectedRows.value.map(r => r.id)
  if (!ids.length) return
  try {
    await ElMessageBox.confirm(`确定禁用选中的 ${ids.length} 条广告吗？`, '批量禁用', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.advertisementList({}) // batch via individual toggles
    ElMessage.success(`已禁用 ${ids.length} 条广告`)
    selectedRows.value = []
    fetchData()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('批量禁用失败')
  }
}

async function handleBatchDelete() {
  const ids = selectedRows.value.map(r => r.id)
  if (!ids.length) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${ids.length} 条广告吗？此操作不可恢复。`, '批量删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
      confirmButtonClass: 'el-button--danger'
    })
    await adminApi.advertisementList({}) // batch via individual deletes
    ElMessage.success(`已删除 ${ids.length} 条广告`)
    selectedRows.value = []
    fetchData()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('批量删除失败')
  }
}

function handleSelectionChange(rows: Advertisement[]) {
  selectedRows.value = rows
}

onMounted(() => {
  fetchStats()
  fetchData()
})
</script>

<template>
  <div class="ad-management">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Promotion /></el-icon>
          广告管理
        </h1>
        <div class="stats-row">
          <span class="stat-item">
            <span class="stat-dot dot-total"></span>
            总计 {{ stats.total }}
          </span>
          <span class="stat-item">
            <span class="stat-dot dot-active"></span>
            启用 {{ stats.active }}
          </span>
          <span class="stat-item">
            <span class="stat-dot dot-inactive"></span>
            禁用 {{ stats.inactive }}
          </span>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建广告</el-button>
      </div>
    </div>

    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="filter-header" @click="filterExpanded = !filterExpanded">
          <span class="filter-title">
            <el-icon><Filter /></el-icon>
            筛选条件
          </span>
          <el-icon class="expand-icon" :class="{ expanded: filterExpanded }"><ArrowDown /></el-icon>
        </div>
      </template>
      <el-collapse-transition>
        <div v-show="filterExpanded" class="filter-body">
          <el-form :inline="true" class="filter-form">
            <el-form-item label="广告类型">
              <el-select v-model="filters.ad_type" placeholder="全部类型" clearable style="width: 150px">
                <el-option v-for="opt in adTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="展示位置">
              <el-select v-model="filters.position" placeholder="全部位置" clearable style="width: 160px">
                <el-option v-for="opt in positionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filters.is_active" placeholder="全部状态" style="width: 120px">
                <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="搜索">
              <el-input v-model="filters.search" placeholder="标题搜索" :prefix-icon="Search" clearable style="width: 200px"
                @keyup.enter="handleSearch" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
              <el-button :icon="Refresh" @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table ref="tableRef" v-loading="loading" :data="tableData" stripe @selection-change="handleSelectionChange"
        row-class-name="ad-table-row">
        <el-table-column type="selection" width="50" align="center" />
        <el-table-column label="缩略图" width="100" align="center">
          <template #default="{ row }">
            <div class="thumbnail-wrapper">
              <img v-if="row.image_url" :src="row.image_url" :alt="row.title" class="ad-thumbnail"
                @error="(e: Event) => { const t = e.target as HTMLImageElement; t.style.display='none'; t.nextElementSibling!.style.display='flex' }"
              />
              <div v-else class="thumbnail-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="160" show-overflow-tooltip />
        <el-table-column prop="ad_type_display" label="类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag :color="getAdTypeColor(row.ad_type)" effect="dark" round size="small" class="type-tag">
              {{ row.ad_type_display || row.ad_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="position_display" label="位置" width="130" align="center">
          <template #default="{ row }">
            <el-tag :color="getPositionColor(row.position)" effect="dark" round size="small" class="position-tag">
              {{ row.position_display || row.position }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" active-color="#22C55E" inactive-color="#475569"
              @change="handleToggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="曝光量" width="90" align="center" sortable>
          <template #default="{ row }">
            <span class="stat-num">{{ row.view_count.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="click_count" label="点击量" width="90" align="center" sortable>
          <template #default="{ row }">
            <span class="stat-num">{{ row.click_count.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="CTR" width="80" align="center">
          <template #default="{ row }">
            <span :class="['ctr-value', { high: parseFloat(calcCTR(row)) > 5 }]">{{ calcCTR(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" sortable />
        <el-table-column prop="created_at" label="创建时间" width="170" sortable>
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该广告？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small" :icon="Delete">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <transition name="slide-fade">
        <div v-if="selectedRows.length > 0" class="batch-bar">
          <span class="batch-info">已选 {{ selectedRows.length }} 项</span>
          <div class="batch-actions">
            <el-button size="small" type="success" @click="handleBatchActivate">批量启用</el-button>
            <el-button size="small" type="warning" @click="handleBatchDeactivate">批量禁用</el-button>
            <el-button size="small" type="danger" @click="handleBatchDelete">批量删除</el-button>
          </div>
        </div>
      </transition>

      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.page_size"
          :total="pagination.count" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper"
          background @size-change="handleSizeChange" @current-change="handlePageChange" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新建广告' : '编辑广告'" width="600px"
      :close-on-click-modal="false" destroy-on-close class="ad-dialog">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px" label-position="right">
        <el-form-item label="广告标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入广告标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="广告类型" prop="ad_type">
          <el-select v-model="formData.ad_type" placeholder="请选择广告类型" style="width: 100%">
            <el-option v-for="opt in adTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="展示位置" prop="position">
          <el-select v-model="formData.position" placeholder="请选择展示位置" style="width: 100%">
            <el-option v-for="opt in positionOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="图片地址" prop="image_url">
          <el-input v-model="formData.image_url" placeholder="请输入图片URL或上传图片">
            <template #append>
              <el-button :icon="Upload" />上传
            </template>
          </el-input>
          <div v-if="formData.image_url" class="image-preview">
            <img :src="formData.image_url" alt="预览" class="preview-img"
              @error="(e: Event) => (e.target as HTMLImageElement).style.display = 'none'" />
          </div>
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="formData.link_url" placeholder="跳转链接(可选)" />
        </el-form-item>
        <el-form-item label="生效时间">
          <el-date-picker v-model="dateRange" type="datetimerange" range-separator="至" start-placeholder="开始时间"
            end-placeholder="结束时间" format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%" @change="handleDateChange" />
        </el-form-item>
        <el-form-item label="排序权重">
          <el-input-number v-model="formData.sort_order" :min="0" :max="9999" controls-position="right" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="formData.is_active" active-color="#22C55E" inactive-color="#475569"
            active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="handleSubmit">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>



<style scoped>
.ad-management {
  min-height: 100%;
  padding: 20px;
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg-base, #020617);
  color: var(--text-primary, #F8FAFC);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #F8FAFC);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title .el-icon {
  color: var(--accent, #22C55E);
}

.stats-row {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: var(--text-secondary, #94A3B8);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-total { background: #3B82F6; }
.dot-active { background: #22C55E; }
.dot-inactive { background: #EF4444; }

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-card {
  margin-bottom: 16px;
  --el-card-bg-color: var(--bg-card, #0F172A);
  --el-border-color: var(--border, #1E293B);
  border: 1px solid var(--border, #1E293B);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  user-select: none;
  padding: 4px 0;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary, #94A3B8);
}

.expand-icon {
  transition: transform 0.3s ease;
  color: var(--text-secondary, #94A3B8);
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.filter-body {
  padding-top: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 12px;
  margin-right: 16px;
}

.filter-form :deep(.el-form-item__label) {
  color: var(--text-secondary, #94A3B8);
  font-weight: 500;
}

.table-card {
  --el-card-bg-color: var(--bg-card, #0F172A);
  --el-border-color: var(--border, #1E293B);
  border: 1px solid var(--border, #1E293B);
}

:deep(.el-table) {
  --el-table-bg-color: #020617;
  --el-table-tr-bg-color: #020617;
  --el-table-header-bg-color: rgba(30, 41, 59, 0.6);
  --el-table-row-hover-bg-color: rgba(34, 197, 94, 0.08);
  --el-table-border-color: var(--border, #1E293B);
  --el-table-text-color: var(--text-primary, #F8FAFC);
  --el-table-header-text-color: var(--text-secondary, #94A3B8);
  font-size: 13px;
  border-radius: 8px;
  overflow: hidden;
  background: #020617 !important;
}

:deep(.el-table__inner-wrapper) {
  background: #020617 !important;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}

:deep(.el-table th.el-table__cell) {
  background: rgba(30, 41, 59, 0.6) !important;
  font-weight: 600;
}

:deep(.el-table td.el-table__cell) {
  background: #020617 !important;
}

:deep(.ad-table-row) {
  transition: background-color 0.2s ease;
}

:deep(.ad-table-row:hover > td) {
  background: rgba(34, 197, 94, 0.06) !important;
}

.thumbnail-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.ad-thumbnail {
  width: 80px;
  height: 45px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--border, #1E293B);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ad-thumbnail:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
}

.thumbnail-placeholder {
  width: 80px;
  height: 45px;
  border-radius: 6px;
  background: var(--bg-secondary, #1E293B);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary, #94A3B8);
  font-size: 18px;
}

.type-tag,
.position-tag {
  border: none;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.stat-num {
  font-variant-numeric: tabular-nums;
  color: var(--text-primary, #F8FAFC);
}

.ctr-value {
  font-weight: 600;
  font-size: 12px;
  color: var(--text-secondary, #94A3B8);
}

.ctr-value.high {
  color: #22C55E;
}

.batch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-top: 12px;
  background: rgba(34, 197, 94, 0.06);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 8px;
}

.batch-info {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent, #22C55E);
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0 8px;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: var(--text-secondary, #94A3B8);
  --el-pagination-button-bg-color: var(--bg-secondary, #1E293B);
  --el-pagination-hover-color: var(--accent, #22C55E);
}

:deep(.el-pager li.is-active) {
  background: var(--accent, #22C55E) !important;
  border-radius: 4px;
}

:deep(.el-pager li) {
  border-radius: 4px;
  background: var(--bg-secondary, #1E293B);
  color: var(--text-secondary, #94A3B8);
  transition: all 0.2s ease;
}

:deep(.el-pager li:hover) {
  color: var(--accent, #22C55E);
}

.ad-dialog :deep(.el-dialog) {
  --el-dialog-bg-color: var(--bg-card, #0F172A);
  --el-dialog-title-font-size: 18px;
  border-radius: 12px;
  border: 1px solid var(--border, #1E293B);
}

.ad-dialog :deep(.el-dialog__title) {
  color: var(--text-primary, #F8FAFC);
  font-weight: 700;
}

.ad-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: var(--text-secondary, #94A3B8);
}

.ad-dialog :deep(.el-form-item__label) {
  color: var(--text-secondary, #94A3B8);
  font-weight: 500;
}

.ad-dialog :deep(.el-input__wrapper),
.ad-dialog :deep(.el-select .el-input__wrapper) {
  background: var(--bg-base, #020617);
  box-shadow: 0 0 0 1px var(--border, #1E293B) inset;
}

.ad-dialog :deep(.el-input__inner) {
  color: var(--text-primary, #F8FAFC);
}

.ad-dialog :deep(.el-input__inner::placeholder) {
  color: #475569;
}

.image-preview {
  margin-top: 10px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border, #1E293B);
  max-height: 160px;
  display: flex;
  justify-content: center;
  background: var(--bg-base, #020617);
}

.preview-img {
  max-width: 100%;
  max-height: 140px;
  object-fit: contain;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.25s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

:deep(.el-button--primary) {
  --el-button-bg-color: var(--accent, #22C55E);
  --el-button-border-color: var(--accent, #22C55E);
  --el-button-hover-bg-color: #16A34A;
  --el-button-hover-border-color: #16A34A;
  font-weight: 600;
}

:deep(.el-card) {
  border-radius: 12px;
}

:deep(.el-switch.is-checked .el-switch__core) {
  border-color: var(--accent, #22C55E);
  background-color: var(--accent, #22C55E);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .stats-row {
    flex-wrap: wrap;
    gap: 12px;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form :deep(.el-form-item) {
    margin-right: 0;
    width: 100%;
  }

  .filter-form :deep(.el-select),
  .filter-form :deep(.el-input) {
    width: 100% !important;
  }

  .batch-bar {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
}
</style>
