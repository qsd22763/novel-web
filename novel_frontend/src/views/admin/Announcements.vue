<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi, type AdminAnnouncement } from '../../api'

interface Announcement extends AdminAnnouncement {}

const loading = ref(false)
const tableData = ref<Announcement[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const filterType = ref<string>('')
const filterStatus = ref<boolean | null>(null)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const showPreview = ref(false)

const formRef = ref()
const form = reactive({
  title: '',
  content: '',
  announcement_type: 'notice' as 'notice' | 'maintenance' | 'activity',
  is_pinned: false,
  is_active: true,
})

const rules = {
  title: [{ required: true, message: '请输入公告标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入公告内容', trigger: 'blur' }],
}

const typeOptions = [
  { value: '', label: '全部' },
  { value: 'notice', label: '通知' },
  { value: 'maintenance', label: '维护' },
  { value: 'activity', label: '活动' },
]

const statusOptions = [
  { value: null as boolean | null, label: '全部' },
  { value: true, label: '已发布' },
  { value: false, label: '草稿' },
]

const typeConfig: Record<string, { color: string; bg: string; dot: string }> = {
  notice: { color: '#3B82F6', bg: 'rgba(59,130,246,0.12)', dot: '#60A5FA' },
  maintenance: { color: '#EF4444', bg: 'rgba(239,68,68,0.12)', dot: '#F87171' },
  activity: { color: '#22C55E', bg: 'rgba(34,197,94,0.12)', dot: '#4ADE80' },
}

const sortedData = ref<Announcement[]>([])

function updateSortedData() {
  sortedData.value = [...tableData.value].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return 0
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filterType.value) params.announcement_type = filterType.value
    if (filterStatus.value !== null) params.is_active = filterStatus.value
    if (searchKeyword.value) params.search = searchKeyword.value

    const res = await adminApi.announcement.list(params)
    tableData.value = res.results || []
    total.value = res.count || 0
    updateSortedData()
  } catch {
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchData()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchData()
}

const resetForm = () => {
  form.title = ''
  form.content = ''
  form.announcement_type = 'notice'
  form.is_pinned = false
  form.is_active = true
  isEdit.value = false
  editingId.value = null
  showPreview.value = false
}

const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: Announcement) => {
  resetForm()
  isEdit.value = true
  editingId.value = row.id
  form.title = row.title
  form.content = row.content
  form.announcement_type = row.announcement_type
  form.is_pinned = row.is_pinned
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  dialogLoading.value = true
  try {
    if (isEdit.value && editingId.value !== null) {
      await adminApi.announcement.update(editingId.value, { ...form })
      ElMessage.success('更新成功')
    } else {
      await adminApi.announcement.create({ ...form })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    dialogLoading.value = false
  }
}

const handleDelete = async (row: Announcement) => {
  try {
    await ElMessageBox.confirm(`确定删除公告「${row.title}」吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await adminApi.announcement.delete(row.id)
    ElMessage.success('已删除')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleTogglePin = async (row: Announcement) => {
  try {
    await adminApi.announcement.togglePin(row.id)
    ElMessage.success(row.is_pinned ? '已取消置顶' : '已置顶')
    fetchData()
  } catch {
    ElMessage.error('操作失败')
  }
}

const handlePublish = async (row: Announcement) => {
  try {
    await adminApi.announcement.publish(row.id)
    ElMessage.success('已发布')
    fetchData()
  } catch {
    ElMessage.error('发布失败')
  }
}

const handleWithdraw = async (row: Announcement) => {
  try {
    await adminApi.announcement.withdraw(row.id)
    ElMessage.success('已撤回为草稿')
    fetchData()
  } catch {
    ElMessage.error('撤回失败')
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const truncateContent = (content: string, len = 80) => {
  if (!content) return ''
  return content.length > len ? content.slice(0, len) + '...' : content
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="announcements-page">
    <div class="page-header">
      <h1 class="page-title">公告管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建公告
      </el-button>
    </div>

    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <div class="filter-left">
          <div class="filter-group">
            <span class="filter-label">类型</span>
            <el-radio-group v-model="filterType" size="small" @change="handleFilterChange">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="notice">通知</el-radio-button>
              <el-radio-button value="maintenance">维护</el-radio-button>
              <el-radio-button value="activity">活动</el-radio-button>
            </el-radio-group>
          </div>
          <div class="filter-group">
            <span class="filter-label">状态</span>
            <el-radio-group v-model="filterStatus" size="small" @change="handleFilterChange">
              <el-radio-button :value="null">全部</el-radio-button>
              <el-radio-button :value="true">已发布</el-radio-button>
              <el-radio-button :value="false">草稿</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="filter-right">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索标题..."
            clearable
            size="default"
            style="width: 240px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="sortedData"
        stripe
        style="width: 100%"
        row-class-name="announcement-row"
      >
        <el-table-column width="50" align="center">
          <template #default="{ row }">
            <span v-if="row.is_pinned" class="pin-icon" title="已置顶">📌</span>
            <span v-else class="pin-placeholder"></span>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-text">{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="announcement_type_display" label="类型" width="110" align="center">
          <template #default="{ row }">
            <span
              class="type-badge"
              :style="{
                color: typeConfig[row.announcement_type]?.color,
                background: typeConfig[row.announcement_type]?.bg,
              }"
            >
              <span
                class="type-dot"
                :style="{ background: typeConfig[row.announcement_type]?.dot }"
              ></span>
              {{ row.announcement_type_display }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.is_active ? 'success' : 'info'"
              size="small"
              effect="dark"
              round
              class="status-tag"
            >
              {{ row.is_active ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="170" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-button link type="primary" size="small" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button
                v-if="!row.is_active"
                link
                type="success"
                size="small"
                @click="handlePublish(row)"
              >
                发布
              </el-button>
              <el-button
                v-else
                link
                type="warning"
                size="small"
                @click="handleWithdraw(row)"
              >
                撤回
              </el-button>
              <el-tooltip :content="row.is_pinned ? '取消置顶' : '置顶'" placement="top">
                <el-button
                  link
                  :type="row.is_pinned ? 'warning' : 'default'"
                  size="small"
                  class="pin-btn"
                  :class="{ active: row.is_pinned }"
                  @click="handleTogglePin(row)"
                >
                  📌
                </el-button>
              </el-tooltip>
              <el-popconfirm
                title="确定删除此公告？"
                confirm-button-text="确定"
                cancel-button-text="取消"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <el-button link type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <el-icon :size="48" class="empty-icon"><Bell /></el-icon>
            <p>暂无公告数据</p>
          </div>
        </template>
      </el-table>

      <div class="pagination-wrap" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑公告' : '新建公告'"
      width="700px"
      :close-on-click-modal="false"
      destroy-on-close
      class="announcement-dialog"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="90px"
        label-position="top"
      >
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="公告类型" prop="announcement_type">
          <el-radio-group v-model="form.announcement_type" size="default">
            <el-radio-button value="notice">
              <span class="radio-type-dot" style="background:#3B82F6"></span>通知
            </el-radio-button>
            <el-radio-button value="maintenance">
              <span class="radio-type-dot" style="background:#EF4444"></span>维护
            </el-radio-button>
            <el-radio-button value="activity">
              <span class="radio-type-dot" style="background:#22C55E"></span>活动
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="公告内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入公告内容，支持纯文本或 Markdown 格式..."
          />
        </el-form-item>

        <div class="switch-row">
          <div class="switch-item">
            <span class="switch-label">是否置顶</span>
            <el-switch v-model="form.is_pinned" active-color="#F59E0B" inactive-color="#334155" />
          </div>
          <div class="switch-item">
            <span class="switch-label">立即发布</span>
            <el-switch v-model="form.is_active" active-color="#22C55E" inactive-color="#334155" />
          </div>
        </div>
      </el-form>

      <el-collapse v-model="showPreview" class="preview-collapse">
        <el-collapse-item name="preview">
          <template #title>
            <div class="preview-title">
              <el-icon><View /></el-icon>
              <span>预览效果</span>
            </div>
          </template>
          <div class="preview-content">
            <div v-if="form.title" class="preview-title-text">{{ form.title }}</div>
            <div v-if="form.announcement_type" class="preview-meta">
              <span
                class="type-badge"
                :style="{
                  color: typeConfig[form.announcement_type]?.color,
                  background: typeConfig[form.announcement_type]?.bg,
                }"
              >
                <span
                  class="type-dot"
                  :style="{ background: typeConfig[form.announcement_type]?.dot }"
                ></span>
                {{ typeOptions.find(t => t.value === form.announcement_type)?.label }}
              </span>
              <el-tag v-if="form.is_pinned" size="small" type="warning" effect="dark" round class="ml-8">📌 置顶</el-tag>
              <el-tag :type="form.is_active ? 'success' : 'info'" size="small" effect="dark" round class="ml-8">
                {{ form.is_active ? '已发布' : '草稿' }}
              </el-tag>
            </div>
            <div class="preview-body">
              {{ form.content || '(暂无内容)' }}
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '创建公告' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.announcements-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #F8FAFC;
  margin: 0;
  letter-spacing: -0.3px;
}

.filter-card {
  background: #0F172A !important;
  border: 1px solid #1E293B !important;
  border-radius: 12px !important;
}

:deep(.filter-card .el-card__body) {
  padding: 18px 22px;
}

.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 28px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 13px;
  color: #94A3B8;
  white-space: nowrap;
  font-weight: 500;
}

.filter-right {
  display: flex;
  align-items: center;
}

:deep(.filter-group .el-radio-group) {
  --el-radio-button-checked-bg-color: rgba(34,197,94,0.15);
  --el-radio-button-checked-border-color: #22C55E;
  --el-radio-button-checked-text-color: #22C55E;
  --el-fill-color-blank: #1E293B;
  --el-border-color: #334155;
  --el-text-color-regular: #94A3B8;
  --el-radio-button-checked-hover-border-color: #22C55E;
}

.table-card {
  background: #0F172A !important;
  border: 1px solid #1E293B !important;
  border-radius: 12px !important;
}

:deep(.table-card .el-card__body) {
  padding: 0;
}

:deep(.el-table) {
  --el-table-bg-color: #020617;
  --el-table-tr-bg-color: #020617;
  --el-table-header-bg-color: #0F172A;
  --el-table-row-hover-bg-color: rgba(34,197,94,0.05);
  --el-table-border-color: #1E293B;
  --el-table-text-color: #F8FAFC;
  --el-table-header-text-color: #94A3B8;
  --el-font-size-base: 13.5px;
  --el-table-current-row-bg-color: rgba(34,197,94,0.06);
  border: none;
  font-size: 13.5px;
  background: #020617 !important;
}

:deep(.el-table__inner-wrapper) {
  background: #020617 !important;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}

:deep(.el-table th.el-table__cell) {
  background: #0F172A !important;
  color: #94A3B8;
  font-weight: 600;
  font-size: 12.5px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  border-bottom: 1px solid #1E293B !important;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(30,41,59,0.6) !important;
  background: #020617 !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(30,41,59,0.25) !important;
}

:deep(.el-table .el-table__inner-wrapper::before) {
  background: #1E293B;
}

.pin-icon {
  font-size: 16px;
  display: inline-block;
  filter: drop-shadow(0 0 4px rgba(245,158,11,0.5));
}

.pin-icon:hover {
  animation: pin-bounce 0.4s ease-in-out;
}

@keyframes pin-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

.pin-placeholder {
  display: inline-block;
  width: 16px;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  color: #F8FAFC;
  font-weight: 500;
  cursor: default;
  transition: color 0.2s ease;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.type-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-tag {
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.3px;
  transition: all 0.25s ease;
}

.time-text {
  color: #64748B;
  font-size: 12.5px;
  font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace;
}

.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.action-btns .el-button {
  font-size: 12.5px;
  transition: all 0.2s ease;
}

.pin-btn {
  font-size: 14px !important;
  opacity: 0.45;
  transition: all 0.25s ease;
}

.pin-btn.active {
  opacity: 1;
  transform: scale(1.15);
  filter: drop-shadow(0 0 3px rgba(245,158,11,0.5));
}

.pin-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

:deep(.announcement-row) {
  transition: all 0.25s ease;
}

:deep(.announcement-row.pinned-row > td) {
  background: linear-gradient(90deg, rgba(245,158,11,0.06) 0%, transparent 40%) !important;
  position: relative;
}

:deep(.announcement-row.pinned-row > td:first-child::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #F59E0B, #D97706);
  border-radius: 0 2px 2px 0;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 18px 22px 4px;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: #94A3B8;
  --el-pagination-button-bg-color: #1E293B;
  --el-pagination-hover-color: #22C55E;
  --el-pagination-button-color: #94A3B8;
}

:deep(.el-pager li.is-active) {
  background: #22C55E !important;
  color: #fff !important;
  border-radius: 6px;
}

:deep(.el-pager li:hover:not(.is-active)) {
  color: #22C55E;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
  gap: 12px;
  color: #475569;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.empty-icon {
  color: #334155;
  opacity: 0.6;
}

.announcement-dialog {
  --el-dialog-bg-color: #0F172A;
  --el-dialog-border-color: #1E293B;
  --el-dialog-title-font-size: 17px;
  --el-dialog-title-font-weight: 700;
  --el-dialog-padding-primary: 24px;
}

:deep(.announcement-dialog .el-dialog) {
  border: 1px solid #1E293B;
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(34,197,94,0.04);
}

:deep(.announcement-dialog .el-dialog__header) {
  border-bottom: 1px solid #1E293B;
  padding-bottom: 16px;
}

:deep(.announcement-dialog .el-dialog__title) {
  color: #F8FAFC;
}

:deep(.announcement-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

:deep(.announcement-dialog .el-dialog__footer) {
  border-top: 1px solid #1E293B;
  padding-top: 16px;
}

:deep(.announcement-dialog .el-form-item__label) {
  color: #CBD5E1;
  font-weight: 600;
  font-size: 13px;
}

:deep(.announcement-dialog .el-input__wrapper),
:deep(.announcement-dialog .el-textarea__inner) {
  background: #1E293B !important;
  box-shadow: 0 0 0 1px #334155 inset !important;
  color: #F8FAFC;
  border-radius: 8px;
  transition: all 0.2s ease;
}

:deep(.announcement-dialog .el-input__wrapper:hover),
:deep(.announcement-dialog .el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #475569 inset !important;
}

:deep(.announcement-dialog .el-input__wrapper.is-focus),
:deep(.announcement-dialog .el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #22C55E inset !important;
}

:deep(.announcement-dialog .el-textarea__inner) {
  background: #1E293B !important;
  color: #F8FAFC;
  line-height: 1.65;
}

:deep(.announcement-dialog .el-radio-group) {
  --el-radio-button-checked-bg-color: rgba(34,197,94,0.15);
  --el-radio-button-checked-border-color: #22C55E;
  --el-radio-button-checked-text-color: #22C55E;
  --el-fill-color-blank: #1E293B;
  --el-border-color: #334155;
  --el-text-color-regular: #94A3B8;
}

.switch-row {
  display: flex;
  gap: 36px;
  padding: 4px 0 8px;
}

.switch-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.switch-label {
  font-size: 13.5px;
  color: #94A3B8;
  font-weight: 500;
}

.radio-type-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.preview-collapse {
  margin-top: 16px;
  border: 1px solid #1E293B;
  border-radius: 10px;
  overflow: hidden;
}

:deep(.preview-collapse .el-collapse-item__header) {
  background: #1E293B;
  color: #94A3B8;
  font-size: 13px;
  border-bottom: 1px solid #1E293B;
  padding: 0 16px;
  height: 40px;
  transition: all 0.2s ease;
}

:deep(.preview-collapse .el-collapse-item__header:hover) {
  background: #263348;
  color: #22C55E;
}

:deep(.preview-collapse .el-collapse-item__wrap) {
  background: #151d2e;
  border-bottom: none;
}

:deep(.preview-collapse .el-collapse-item__content) {
  padding: 18px 16px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-title-text {
  font-size: 16px;
  font-weight: 700;
  color: #F8FAFC;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ml-8 {
  margin-left: 8px;
}

.preview-body {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 8px;
  padding: 16px;
  color: #CBD5E1;
  font-size: 13.5px;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 240px;
  overflow-y: auto;
}

.preview-body::-webkit-scrollbar {
  width: 4px;
}

.preview-body::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
</style>
