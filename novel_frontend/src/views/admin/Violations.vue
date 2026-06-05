<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  WarningFilled, Search, Refresh, Plus,
  Edit, Close, Check, View
} from '@element-plus/icons-vue'

interface ViolationRecord {
  id: number
  novel_id: number
  novel_title: string
  violation_type: string
  reason: string
  reporter: string
  handler?: string
  status: 'pending' | 'resolved'
  ban_days?: number | null
  ban_note?: string
  created_at: string
  resolved_at?: string
}

const VIOLATION_TYPES = [
  { value: 'illegal_content', label: '非法内容', color: '#EF4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' },
  { value: 'copyright', label: '版权侵权', color: '#A855F7', bg: 'rgba(168,85,247,0.12)', border: 'rgba(168,85,247,0.3)' },
  { value: 'spam', label: '垃圾信息', color: '#F97316', bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)' },
  { value: 'pornography', label: '色情内容', color: '#DC2626', bg: 'rgba(220,38,38,0.12)', border: 'rgba(220,38,38,0.3)' },
  { value: 'violence', label: '暴力内容', color: '#991B1B', bg: 'rgba(153,27,27,0.12)', border: 'rgba(153,27,27,0.3)' },
  { value: 'other', label: '其他违规', color: '#64748B', bg: 'rgba(100,116,139,0.12)', border: 'rgba(100,116,139,0.3)' },
]

function getViolationStyle(type: string) {
  return VIOLATION_TYPES.find(v => v.value === type) || VIOLATION_TYPES[5]
}

const STATUS_OPTIONS = [
  { value: '', label: '全部状态' },
  { value: 'pending', label: '处理中' },
  { value: 'resolved', label: '已解决' },
]

const loading = ref(false)
const tableData = ref<ViolationRecord[]>([])
const total = ref(0)
const novels = ref<{ id: number; title: string }[]>([])

const queryParams = reactive({
  page: 1,
  page_size: 15,
  status: '' as string,
  violation_type: '' as string,
  search: '',
})

const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({
  novel_id: null as number | null,
  violation_type: '',
  reason: '',
})
const createRules: FormRules = {
  novel_id: [{ required: true, message: '请选择小说', trigger: 'change' }],
  violation_type: [{ required: true, message: '请选择违规类型', trigger: 'change' }],
  reason: [{ required: true, message: '请填写详细原因', trigger: 'blur' }, { min: 10, message: '原因至少10个字符', trigger: 'blur' }],
}

const banDialogVisible = ref(false)
const banTargetId = ref<number | null>(null)
const banForm = reactive({
  days: 30,
  note: '',
})

async function fetchNovels() {
  try {
    const res = await fetch('/api/novels/', { method: 'GET' })
    const data = await res.json()
    novels.value = (data.results || data || []).map((n: any) => ({ id: n.id, title: n.title }))
  } catch {
    novels.value = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, title: ['星辰大海','都市之巅峰战神','穿越之大秦帝国','玄幻世界：剑道独尊','游戏王：卡牌传说'][i % 5] }))
  }
}

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: queryParams.page,
      page_size: queryParams.page_size,
    }
    if (queryParams.status) params.status = queryParams.status
    if (queryParams.violation_type) params.violation_type = queryParams.violation_type
    if (queryParams.search) params.search = queryParams.search

    const res = await fetch(`/api/admin/violations/?${new URLSearchParams(params as any).toString()}`, { method: 'GET' })
    const data = await res.json()
    tableData.value = data.results || []
    total.value = data.count || 0
  } catch {
    mockFetchData()
  } finally {
    loading.value = false
  }
}

function mockFetchData() {
  const types = VIOLATION_TYPES.map(t => t.value)
  const mockData: ViolationRecord[] = Array.from({ length: 28 }, (_, i) => ({
    id: i + 1,
    novel_id: (i % 10) + 1,
    novel_title: ['星辰大海','都市之巅峰战神','穿越之大秦帝国','玄幻世界：剑道独尊','游戏王：卡牌传说','悬疑档案：午夜追踪','武侠江湖录','历史长河：三国风云','星际殖民计划','重生之商业帝国'][i % 10],
    violation_type: types[i % types.length],
    reason: `该作品存在${VIOLATION_TYPES[i % types.length].label}问题，经用户举报后核实确认。具体情况包括多处不当描述，严重影响阅读体验。`,
    reporter: `用户${String.fromCharCode(65 + (i % 26))}${Math.floor(i / 26) || ''}`,
    handler: i < 15 ? `管理员张三` : undefined,
    status: i < 15 ? 'resolved' : 'pending',
    ban_days: i < 10 ? [30, 7, 0, 90, 14][i % 5] : null,
    ban_note: i < 10 ? '多次违规，予以封禁处理' : undefined,
    created_at: new Date(Date.now() - i * 3600000 * 6).toISOString(),
    resolved_at: i < 15 ? new Date(Date.now() - i * 3600000 * 6 - 1800000).toISOString() : undefined,
  }))

  let filtered = [...mockData]
  if (queryParams.status) filtered = filtered.filter(item => item.status === queryParams.status)
  if (queryParams.violation_type) filtered = filtered.filter(item => item.violation_type === queryParams.violation_type)
  if (queryParams.search) {
    const s = queryParams.search.toLowerCase()
    filtered = filtered.filter(item =>
      item.novel_title.toLowerCase().includes(s) ||
      item.reason.toLowerCase().includes(s) ||
      item.reporter.toLowerCase().includes(s)
    )
  }

  total.value = filtered.length
  const start = (queryParams.page - 1) * queryParams.page_size
  tableData.value = filtered.slice(start, start + queryParams.page_size)
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

function handleSearch() {
  queryParams.page = 1
  fetchData()
}

function handleReset() {
  queryParams.status = ''
  queryParams.violation_type = ''
  queryParams.search = ''
  queryParams.page = 1
  fetchData()
}

function handleRefresh() {
  fetchData()
  ElMessage.success('数据已刷新')
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

function openCreateDialog() {
  Object.assign(createForm, { novel_id: null, violation_type: '', reason: '' })
  createDialogVisible.value = true
  nextTick(() => createFormRef.value?.clearValidate())
}

async function handleSubmitCreate() {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await fetch('/api/admin/violations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createForm),
      })
      ElMessage.success('违规记录已创建')
      createDialogVisible.value = false
      fetchData()
    } catch {
      ElMessage.error('创建失败')
    }
  })
}

function openBanDialog(row: ViolationRecord) {
  banTargetId.value = row.id
  Object.assign(banForm, { days: 30, note: '' })
  banDialogVisible.value = true
}

async function handleSubmitBan() {
  if (!banTargetId.value) return
  try {
    await fetch(`/api/admin/violations/${banTargetId.value}/ban/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(banForm),
    })
    ElMessage.success(`已封禁 ${banForm.days === 0 ? '永久' : banForm.days + '天'}`)
    banDialogVisible.value = false
    fetchData()
  } catch {
    ElMessage.error('封禁操作失败')
  }
}

async function handleMarkOnly(row: ViolationRecord) {
  try {
    await ElMessageBox.confirm(`确定仅标记该违规记录为已处理吗？`, '确认标记', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info',
    })
    await fetch(`/api/admin/violations/${row.id}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'resolved' }),
    })
    ElMessage.success('已标记为已解决')
    fetchData()
  } catch {
  }
}

async function handleUnban(row: ViolationRecord) {
  try {
    await ElMessageBox.confirm('确定要解封该书籍吗？', '确认解封', {
      confirmButtonText: '确定解封',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await fetch(`/api/admin/violations/${row.id}/unban/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    ElMessage.success('已解封')
    fetchData()
  } catch {
  }
}

onMounted(() => {
  fetchNovels()
  fetchData()
})
</script>

<template>
  <div class="violations-management">
    <!-- ===== TOP BAR ===== -->
    <div class="top-bar">
      <div class="top-bar-left">
        <h1 class="page-title">
          <el-icon :size="22" class="title-icon"><WarningFilled /></el-icon>
          违规管控
        </h1>
        <span class="total-count" style="font-family:'Fira Code',monospace" v-if="total > 0">
          共 <em>{{ total }}</em> 条记录
        </span>
      </div>
      <div class="top-bar-right">
        <el-button @click="openCreateDialog" :icon="Plus" type="primary" class="action-btn primary-btn">
          新建违规记录
        </el-button>
        <el-button @click="handleRefresh" :icon="Refresh" plain class="action-btn">刷新</el-button>
      </div>
    </div>

    <!-- ===== FILTER SECTION ===== -->
    <div class="filter-bar">
      <div class="filter-item">
        <label class="filter-label">状态</label>
        <el-select v-model="queryParams.status" placeholder="全部状态" clearable class="filter-select" popper-class="dark-select-dropdown" @change="handleSearch">
          <el-option v-for="opt in STATUS_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">违规类型</label>
        <el-select v-model="queryParams.violation_type" placeholder="全部类型" clearable class="filter-select" popper-class="dark-select-dropdown" @change="handleSearch">
          <el-option v-for="t in VIOLATION_TYPES" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
      <div class="filter-item filter-search">
        <label class="filter-label">搜索</label>
        <el-input v-model="queryParams.search" placeholder="书名 / 原因 / 举报人" :prefix-icon="Search" clearable @keyup.enter="handleSearch" />
      </div>
      <div class="filter-actions">
        <el-button type="primary" @click="handleSearch" :icon="Search" size="default">查询</el-button>
        <el-button @click="handleReset" plain>重置</el-button>
      </div>
    </div>

    <!-- ===== DATA TABLE ===== -->
    <div class="table-wrapper">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        class="violations-table"
        row-class-name="violation-row"
      >
        <el-table-column label="小说名" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <a class="novel-link">{{ row.novel_title }}</a>
          </template>
        </el-table-column>

        <el-table-column label="违规类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              round
              size="small"
              :style="{
                background: getViolationStyle(row.violation_type).bg,
                color: getViolationStyle(row.violation_type).color,
                borderColor: getViolationStyle(row.violation_type).border,
                border: `1px solid ${getViolationStyle(row.violation_type).border}`,
              }"
              class="violation-type-tag"
            >{{ getViolationStyle(row.violation_type).label }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="详细原因" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="reason-text">{{ row.reason }}</span>
          </template>
        </el-table-column>

        <el-table-column label="举报人" width="100" align="center">
          <template #default="{ row }">
            <span class="reporter-text">{{ row.reporter }}</span>
          </template>
        </el-table-column>

        <el-table-column label="处理人" width="100" align="center">
          <template #default="{ row }">
            <span class="handler-text">{{ row.handler || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'resolved' ? 'success' : 'warning'" size="small" round effect="dark">
              {{ row.status === 'resolved' ? '已解决' : '处理中' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="时间" width="155">
          <template #default="{ row }">
            <span style="font-family:'Fira Code',monospace;font-size:12px;color:#64748B">
              {{ formatDate(row.created_at) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <div class="action-group" v-if="row.status === 'pending'">
              <el-button size="small" type="danger" plain @click="openBanDialog(row)" class="ban-btn">
                封禁
              </el-button>
              <el-button size="small" @click="handleMarkOnly(row)" class="mark-btn">
                仅标记
              </el-button>
            </div>
            <div class="action-group" v-else>
              <el-button size="small" link type="primary" @click="handleUnban(row)" class="unban-link" v-if="row.ban_days !== null && row.ban_days !== undefined">
                解封
              </el-button>
              <el-popover placement="left" :width="240" trigger="hover" v-if="row.ban_note">
                <template #reference>
                  <el-button size="small" link class="note-link">
                    <el-icon :size="13"><View /></el-icon> 备注
                  </el-button>
                </template>
                <div class="note-popover-content">
                  <p class="note-label">解封备注</p>
                  <p class="note-text">{{ row.ban_note }}</p>
                  <p class="note-time" style="font-family:'Fira Code',monospace;font-size:11px;color:#64748B;margin-top:8px">
                    处理时间：{{ formatDate(row.resolved_at || '') }}
                  </p>
                </div>
              </el-popover>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :page-sizes="[15, 30, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="dark-pagination"
        />
      </div>
    </div>

    <!-- ===== CREATE DIALOG ===== -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建违规记录"
      width="560px"
      :close-on-click-modal="false"
      class="create-dialog"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-position="top"
        class="create-form"
      >
        <el-form-item label="选择小说" prop="novel_id">
          <el-select v-model="createForm.novel_id" placeholder="请选择小说" filterable class="full-width" popper-class="dark-select-dropdown">
            <el-option v-for="n in novels" :key="n.id" :label="n.title" :value="n.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="违规类型" prop="violation_type">
          <el-select v-model="createForm.violation_type" placeholder="请选择违规类型" class="full-width" popper-class="dark-select-dropdown">
            <el-option v-for="t in VIOLATION_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细原因" prop="reason">
          <el-input v-model="createForm.reason" type="textarea" :rows="4" placeholder="请详细描述违规情况..." maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitCreate">创建记录</el-button>
      </template>
    </el-dialog>

    <!-- ===== BAN DIALOG ===== -->
    <el-dialog
      v-model="banDialogVisible"
      title="封禁处理"
      width="480px"
      :close-on-click-modal="false"
      class="ban-dialog"
      destroy-on-close
    >
      <div class="ban-content">
        <div class="ban-warning">
          <el-icon :size="32" color="#EF4444"><WarningFilled /></el-icon>
          <div class="ban-warning-text">
            <h3>封禁警告</h3>
            <p>此操作将禁止该书籍在平台上展示。请谨慎设置封禁时长。</p>
          </div>
        </div>

        <el-form label-position="top" class="ban-form">
          <el-form-item label="封禁天数">
            <el-input-number v-model="banForm.days" :min="0" :max="3650" controls-position="right" class="full-width" />
            <div class="form-hint">输入 <strong style="color:#EF4444">0</strong> 表示永久封禁，默认 <strong style="color:#22C55E">30</strong> 天</div>
          </el-form-item>
          <el-form-item label="备注说明">
            <el-input v-model="banForm.note" type="textarea" :rows="3" placeholder="填写封禁原因和备注（可选）" maxlength="200" show-word-limit />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="banDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleSubmitBan">
          确认封禁{{ banForm.days === 0 ? '(永久)' : `(${banForm.days}天)` }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Fira+Code:wght@400;500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

.violations-management {
  font-family: 'Fira Sans', system-ui, -apple-system, sans-serif;
  padding-bottom: 32px;
}

/* ===== TOP BAR ===== */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
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
  color: #F59E0B;
}

.total-count {
  font-size: 13px;
  color: #64748B;
  font-weight: 500;
}

.total-count em {
  color: #F59E0B;
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

.primary-btn {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  border: none;
  color: #fff;
  font-weight: 600;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #16A34A, #15803D);
  box-shadow: 0 4px 16px rgba(34,197,94,0.3);
}

/* ===== FILTER BAR ===== */
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  margin-bottom: 18px;
  padding: 16px 20px;
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 12px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 11.5px;
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

.filter-search .el-input {
  width: 100%;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
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

/* ===== VIOLATIONS TABLE ===== */
.violations-table {
  --el-table-bg-color: #020617;
  --el-table-tr-bg-color: #020617;
  --el-table-header-bg-color: rgba(15,23,42,0.8);
  --el-table-row-hover-bg-color: rgba(245,158,11,0.04);
  --el-table-border-color: #1E293B;
  --el-table-text-color: #E2E8F0;
  --el-table-header-text-color: #94A3B8;
  font-size: 13px;
  border: none;
  width: 100%;
  background: #020617 !important;
}

.violations-table :deep(.el-table__inner-wrapper) {
  background: #020617 !important;
}

.violations-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.violations-table :deep(th.el-table__cell) {
  font-weight: 650;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748B !important;
  background: rgba(15,23,42,0.6) !important;
  border-bottom: 1px solid #1E293B !important;
  padding: 12px 0;
}

.violations-table :deep(td.el-table__cell) {
  border-bottom: 1px solid rgba(30,41,59,0.4);
  padding: 12px 0;
  vertical-align: middle;
  background: #020617 !important;
}

.violations-table :deep(.el-table__body tr) {
  cursor: default;
  transition: all 0.2s ease;
  position: relative;
}

.violations-table :deep(.el-table__body tr::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: linear-gradient(180deg, #F59E0B, #D97706);
  border-radius: 0 3px 3px 0;
  transition: width 0.2s ease;
}

.violations-table :deep(.el-table__body tr:hover::before) {
  width: 3px;
}

.violations-table :deep(.el-table--striped .el-table__row--striped td.el-table__cell) {
  background: rgba(30,41,59,0.2) !important;
}

.violations-table :deep(.el-table__empty-text) {
  color: #64748B;
}

.novel-link {
  font-weight: 600;
  font-size: 13.5px;
  color: #F8FAFC;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.novel-link:hover {
  color: #22C55E;
}

.violation-type-tag {
  font-size: 11.5px !important;
  font-weight: 600 !important;
  height: 22px !important;
  line-height: 20px !important;
  padding: 0 10px !important;
}

.reason-text {
  font-size: 12.5px;
  color: #94A3B8;
  line-height: 1.4;
}

.reporter-text,
.handler-text {
  font-size: 12.5px;
  color: #CBD5E1;
}

.action-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.ban-btn {
  font-size: 12px;
  border-radius: 6px;
}

.mark-btn {
  font-size: 12px;
  border-radius: 6px;
  border-color: #334155;
  color: #94A3B8;
}

.mark-btn:hover {
  border-color: #3B82F6;
  color: #3B82F6;
}

.unban-link {
  color: #22C55E;
  font-size: 12px;
}

.unban-link:hover {
  color: #4ADE80;
}

.note-link {
  color: #64748B;
  font-size: 12px;
}

.note-link:hover {
  color: #94A3B8;
}

/* Note Popover */
.note-popover-content {
  padding: 4px 0;
}

.note-label {
  font-size: 12px;
  font-weight: 600;
  color: #94A3B8;
  margin: 0 0 6px;
}

.note-text {
  font-size: 13px;
  color: #E2E8F0;
  line-height: 1.5;
  margin: 0;
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

.dark-pagination :deep(.el-pagination__sizes),
.dark-pagination :deep(.el-pagination__total) {
  color: #64748B;
  font-family: 'Fira Code', monospace;
  font-size: 12px;
}

/* ===== CREATE DIALOG ===== */
.create-dialog :deep(.el-dialog) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.create-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.create-dialog :deep(.el-dialog__title) {
  color: #F8FAFC;
  font-size: 17px;
  font-weight: 700;
}

.create-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

.create-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.create-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(30,41,59,0.5);
}

.create-form :deep(.el-form-item__label) {
  color: #94A3B8;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding-bottom: 4px;
}

.create-form :deep(.el-input__wrapper),
.create-form :deep(.el-textarea__inner) {
  background: #1E293B;
  box-shadow: 0 0 0 1px #334155;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.create-form :deep(.el-input__wrapper:hover),
.create-form :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #475569;
}

.create-form :deep(.el-input__wrapper.is-focus),
.create-form :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #22C55E, 0 0 0 3px rgba(34,197,94,0.1);
}

.create-form :deep(.el-input__inner),
.create-form :deep(.el-textarea__inner) {
  color: #F8FAFC;
}

.create-form :deep(.el-select .el-input__wrapper) {
  background: #1E293B;
}

.full-width {
  width: 100%;
}

/* ===== BAN DIALOG ===== */
.ban-dialog :deep(.el-dialog) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.ban-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.ban-dialog :deep(.el-dialog__title) {
  color: #EF4444;
  font-size: 17px;
  font-weight: 700;
}

.ban-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

.ban-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.ban-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(30,41,59,0.5);
}

.ban-warning {
  display: flex;
  gap: 14px;
  padding: 18px;
  background: rgba(239,68,68,0.06);
  border: 1px solid rgba(239,68,68,0.15);
  border-radius: 12px;
  margin-bottom: 20px;
}

.ban-warning-text h3 {
  font-size: 15px;
  font-weight: 700;
  color: #EF4444;
  margin: 0 0 4px;
}

.ban-warning-text p {
  font-size: 12.5px;
  color: #94A3B8;
  margin: 0;
  line-height: 1.5;
}

.ban-form :deep(.el-form-item__label) {
  color: #94A3B8;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding-bottom: 4px;
}

.ban-form :deep(.el-input__wrapper),
.ban-form :deep(.el-textarea__inner) {
  background: #1E293B;
  box-shadow: 0 0 0 1px #334155;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.ban-form :deep(.el-input__wrapper:hover),
.ban-form :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #475569;
}

.ban-form :deep(.el-input__wrapper.is-focus),
.ban-form :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #EF4444, 0 0 0 3px rgba(239,68,68,0.1);
}

.ban-form :deep(.el-input__inner),
.ban-form :deep(.el-textarea__inner) {
  color: #F8FAFC;
}

.form-hint {
  font-size: 11.5px;
  color: #64748B;
  margin-top: 4px;
}
</style>
