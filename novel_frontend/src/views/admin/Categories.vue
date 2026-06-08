<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  FolderOpened, Plus, Edit, Delete,
  Check, Close, Refresh, Setting,
  CirclePlus, DocumentCopy
} from '@element-plus/icons-vue'

interface CategoryNode {
  id: number
  name: string
  parent_id: number | null
  color: string
  description: string
  sort_order: number
  is_active: boolean
  children?: CategoryNode[]
  book_count?: number
}

const loading = ref(false)
const treeData = ref<CategoryNode[]>([])
const selectedNodeKey = ref<number | null>(null)
const selectedNode = ref<CategoryNode | null>(null)
const treeRef = ref()

const editForm = reactive({
  name: '',
  parent_id: null as number | null,
  color: '#22C55E',
  description: '',
  sort_order: 0,
  is_active: true,
})

const formRef = ref<FormInstance>()
const dialogFormRef = ref<FormInstance>()
const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref<number | null>(null)

const contextMenuVisible = ref(false)
const contextMenuEvent = ref<{ x: number; y: number }>({ x: 0, y: 0 })
const contextMenuNode = ref<CategoryNode | null>(null)

const stats = reactive({
  total: 0,
  active: 0,
  bookCount: 0,
})

const defaultProps = {
  children: 'children',
  label: 'name',
}

function generateMockTree(): CategoryNode[] {
  return [
    {
      id: 1, name: '玄幻', parent_id: null, color: '#A855F7', description: '玄幻修仙类小说', sort_order: 1, is_active: true, book_count: 156,
      children: [
        { id: 11, name: '东方玄幻', parent_id: 1, color: '#A855F7', description: '', sort_order: 1, is_active: true, book_count: 89 },
        { id: 12, name: '西方奇幻', parent_id: 1, color: '#8B5CF6', description: '', sort_order: 2, is_active: true, book_count: 42 },
        { id: 13, name: '异世大陆', parent_id: 1, color: '#7C3AED', description: '', sort_order: 3, is_active: false, book_count: 25 },
      ],
    },
    {
      id: 2, name: '都市', parent_id: null, color: '#3B82F6', description: '都市生活类小说', sort_order: 2, is_active: true, book_count: 234,
      children: [
        { id: 21, name: '都市生活', parent_id: 2, color: '#3B82F6', description: '', sort_order: 1, is_active: true, book_count: 120 },
        { id: 22, name: '商战职场', parent_id: 2, color: '#2563EB', description: '', sort_order: 2, is_active: true, book_count: 67 },
        { id: 23, name: '娱乐明星', parent_id: 2, color: '#1D4ED8', description: '', sort_order: 3, is_active: true, book_count: 47 },
      ],
    },
    {
      id: 3, name: '穿越', parent_id: null, color: '#EC4899', description: '穿越重生类小说', sort_order: 3, is_active: true, book_count: 189,
      children: [
        { id: 31, name: '历史穿越', parent_id: 3, color: '#EC4899', description: '', sort_order: 1, is_active: true, book_count: 98 },
        { id: 32, name: '重生逆袭', parent_id: 3, color: '#DB2777', description: '', sort_order: 2, is_active: true, book_count: 91 },
      ],
    },
    {
      id: 4, name: '科幻', parent_id: null, color: '#06B6D4', description: '科幻未来类小说', sort_order: 4, is_active: true, book_count: 78,
      children: [],
    },
    {
      id: 5, name: '游戏', parent_id: null, color: '#22C55E', description: '游戏竞技类小说', sort_order: 5, is_active: true, book_count: 112,
      children: [
        { id: 51, name: '虚拟网游', parent_id: 5, color: '#22C55E', description: '', sort_order: 1, is_active: true, book_count: 65 },
        { id: 52, name: '电竞', parent_id: 5, color: '#16A34A', description: '', sort_order: 2, is_active: false, book_count: 34 },
        { id: 53, name: '游戏异界', parent_id: 5, color: '#15803D', description: '', sort_order: 3, is_active: true, book_count: 13 },
      ],
    },
    {
      id: 6, name: '悬疑', parent_id: null, color: '#F59E0B', description: '悬疑推理类小说', sort_order: 6, is_active: true, book_count: 56,
      children: [],
    },
    {
      id: 7, name: '武侠', parent_id: null, color: '#EF4444', description: '武侠仙侠类小说', sort_order: 7, is_active: true, book_count: 45,
      children: [],
    },
    {
      id: 8, name: '历史', parent_id: null, color: '#8B5CF6', description: '历史架空类小说', sort_order: 8, is_active: false, book_count: 33,
      children: [],
    },
  ]
}

function countAllNodes(nodes: CategoryNode[]): { total: number; active: number; books: number } {
  let total = 0
  let active = 0
  let books = 0
  for (const node of nodes) {
    total++
    if (node.is_active) active++
    books += node.book_count || 0
    if (node.children && node.children.length > 0) {
      const sub = countAllNodes(node.children)
      total += sub.total
      active += sub.active
      books += sub.books
    }
  }
  return { total, active, books }
}

async function fetchTree() {
  loading.value = true
  try {
    const res = await fetch('/api/admin/categories/tree/', { method: 'GET' })
    const data = await res.json()
    treeData.value = data || []
  } catch (e) {
    console.error('加载分类树失败:', e)
    treeData.value = []
  } finally {
    loading.value = false
    updateStats()
  }
}

function updateStats() {
  const s = countAllNodes(treeData.value)
  stats.total = s.total
  stats.active = s.active
  stats.bookCount = s.books
}

function findNodeById(nodes: CategoryNode[], id: number): CategoryNode | null {
  for (const node of nodes) {
    if (node.id === id) return node
    if (node.children) {
      const found = findNodeById(node.children, id)
      if (found) return found
    }
  }
  return null
}

function handleNodeClick(data: CategoryNode) {
  selectedNode.value = data
  selectedNodeKey.value = data.id
  Object.assign(editForm, {
    name: data.name,
    parent_id: data.parent_id,
    color: data.color || '#22C55E',
    description: data.description || '',
    sort_order: data.sort_order,
    is_active: data.is_active,
  })
}

function openCreateDialog(parentId?: number) {
  editingId.value = null
  dialogTitle.value = parentId ? '新建子分类' : '新建一级分类'
  Object.assign(editForm, {
    name: '',
    parent_id: parentId || null,
    color: '#22C55E',
    description: '',
    sort_order: 0,
    is_active: true,
  })
  dialogVisible.value = true
  nextTick(() => dialogFormRef.value?.clearValidate())
}

function openEditDialog(node: CategoryNode) {
  editingId.value = node.id
  dialogTitle.value = '编辑分类'
  Object.assign(editForm, {
    name: node.name,
    parent_id: node.parent_id,
    color: node.color || '#22C55E',
    description: node.description || '',
    sort_order: node.sort_order,
    is_active: node.is_active,
  })
  dialogVisible.value = true
  nextTick(() => dialogFormRef.value?.clearValidate())
}

async function handleSubmit() {
  if (!dialogFormRef.value) return
  await dialogFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (editingId.value) {
        await fetch(`/api/admin/categories/${editingId.value}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editForm),
        })
        ElMessage.success('更新成功')
      } else {
        await fetch('/api/admin/categories/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editForm),
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchTree()
      if (selectedNode.value) {
        handleNodeClick(findNodeById(treeData.value, selectedNode.value.id) || selectedNode.value)
      }
    } catch (e) {
      console.error('保存分类失败:', e)
      ElMessage.error(editingId.value ? '更新失败' : '创建失败')
    }
  })
}

async function handleDelete(node: CategoryNode) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类「${node.name}」吗？${node.children && node.children.length > 0 ? '其子分类也将被一并删除。' : ''}`,
      '确认删除',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await fetch(`/api/admin/categories/${node.id}/`, { method: 'DELETE' })
    ElMessage.success('已删除')
    contextMenuVisible.value = false
    if (selectedNode.value?.id === node.id) {
      selectedNode.value = null
      selectedNodeKey.value = null
    }
    fetchTree()
  } catch {
  }
}

async function handleToggle(node: CategoryNode) {
  try {
    await fetch(`/api/admin/categories/${node.id}/toggle/`, { method: 'POST' })
    ElMessage.success(node.is_active ? '已禁用' : '已启用')
    contextMenuVisible.value = false
    fetchTree()
    if (selectedNode.value?.id === node.id) {
      handleNodeClick({ ...node, is_active: !node.is_active })
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

function handleContextMenu(event: MouseEvent, data: CategoryNode, node: any, element: Element) {
  event.preventDefault()
  contextMenuNode.value = data
  contextMenuEvent.value = { x: event.clientX, y: event.clientY }
  contextMenuVisible.value = true
}

function closeContextMenu() {
  contextMenuVisible.value = false
}

function handleRefresh() {
  fetchTree()
  ElMessage.success('数据已刷新')
}

onMounted(() => {
  fetchTree()
  document.addEventListener('click', closeContextMenu)
})
</script>

<template>
  <div class="categories-management">
    <!-- ===== TOP BAR ===== -->
    <div class="top-bar">
      <div class="top-bar-left">
        <h1 class="page-title">
          <el-icon :size="22" class="title-icon"><FolderOpened /></el-icon>
          分类管理
        </h1>
      </div>
      <div class="top-bar-right">
        <el-button @click="openCreateDialog()" :icon="Plus" type="primary" class="action-btn primary-btn">
          新建一级分类
        </el-button>
        <el-button @click="handleRefresh" :icon="Refresh" plain class="action-btn">刷新</el-button>
      </div>
    </div>

    <!-- ===== MAIN CONTENT ===== -->
    <div class="main-content">
      <!-- Left: Tree -->
      <div class="tree-panel">
        <div class="tree-header">
          <span class="tree-header-title">分类树</span>
          <span class="tree-count" style="font-family:'Fira Code',monospace">{{ stats.total }} 项</span>
        </div>
        <div class="tree-body" v-loading="loading">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="defaultProps"
            node-key="id"
            highlight-current
            :expand-on-click-node="false"
            :current-node-key="selectedNodeKey"
            @node-click="handleNodeClick"
            @node-contextmenu="handleContextMenu"
            class="category-tree"
            draggable
          >
            <template #default="{ node, data }">
              <div class="tree-node-content" :class="{ inactive: !data.is_active }">
                <span class="node-color-dot" :style="{ background: data.color || '#22C55E' }"></span>
                <span class="node-label">{{ node.label }}</span>
                <span class="node-badge" v-if="data.book_count">{{ data.book_count }}</span>
                <el-tag v-if="!data.is_active" size="small" type="info" round class="status-tag-mini">禁用</el-tag>
              </div>
            </template>
          </el-tree>

          <!-- Empty State -->
          <div class="tree-empty" v-if="!loading && treeData.length === 0">
            <el-icon :size="36" color="#334155"><FolderOpened /></el-icon>
            <p>暂无分类数据</p>
          </div>
        </div>
      </div>

      <!-- Right: Edit Panel -->
      <div class="edit-panel">
        <div class="panel-header">
          <span class="panel-title">
            <el-icon><Setting /></el-icon>
            {{ selectedNode ? '编辑分类' : '分类详情' }}
          </span>
        </div>

        <!-- Selected Node Edit Form -->
        <div class="panel-body" v-if="selectedNode">
          <el-form
            ref="formRef"
            :model="editForm"
            label-position="top"
            class="edit-form"
          >
            <el-form-item label="分类名称">
              <el-input v-model="editForm.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
            </el-form-item>

            <el-form-item label="父级分类">
              <el-select v-model="editForm.parent_id" placeholder="无（顶级分类）" clearable class="full-width" popper-class="dark-select-dropdown">
                <el-option
                  v-for="n in treeData.filter(t => t.id !== selectedNode?.id)"
                  :key="n.id"
                  :label="n.name"
                  :value="n.id"
                />
              </el-select>
            </el-form-item>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="颜色标识">
                  <div class="color-picker-wrap">
                    <el-color-picker v-model="editForm.color" show-alpha :predefine="['#22C55E','#3B82F6','#A855F7','#EC4899','#F59E0B','#EF4444','#06B6D4','#8B5CF6']" />
                    <span class="color-value" style="font-family:'Fira Code',monospace">{{ editForm.color }}</span>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="排序权重">
                  <el-input-number v-model="editForm.sort_order" :min="0" :max="9999" controls-position="right" class="full-width" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="描述说明">
              <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="分类描述（可选）" maxlength="200" show-word-limit />
            </el-form-item>

            <el-form-item label="状态">
              <div class="switch-wrap">
                <el-switch
                  v-model="editForm.is_active"
                  active-text="启用"
                  inactive-text="禁用"
                  active-color="#22C55E"
                  inactive-color="#334155"
                />
              </div>
            </el-form-item>
          </el-form>

          <div class="panel-actions">
            <el-button @click="openEditDialog(selectedNode!)" type="primary" :icon="Edit">
              在弹窗中编辑
            </el-button>
          </div>
        </div>

        <!-- Unselected Placeholder -->
        <div class="panel-placeholder" v-else>
          <el-icon :size="48" color="#1E293B"><DocumentCopy /></el-icon>
          <p>请从左侧选择一个分类进行编辑</p>
        </div>

        <!-- Stats Footer -->
        <div class="stats-footer">
          <div class="stat-item">
            <span class="stat-value" style="font-family:'Fira Code',monospace;color:#22C55E">{{ stats.total }}</span>
            <span class="stat-label">总分类数</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value" style="font-family:'Fira Code',monospace;color:#3B82F6">{{ stats.active }}</span>
            <span class="stat-label">已启用</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value" style="font-family:'Fira Code',monospace;color:#F59E0B">{{ stats.bookCount }}</span>
            <span class="stat-label">关联书籍</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== CONTEXT MENU ===== -->
    <teleport to="body">
      <div
        v-if="contextMenuVisible"
        class="context-menu"
        :style="{ left: contextMenuEvent.x + 'px', top: contextMenuEvent.y + 'px' }"
      >
        <div class="context-menu-item" @click="openCreateDialog(contextMenuNode!.id); closeContextMenu()">
          <el-icon><CirclePlus /></el-icon> 新建子分类
        </div>
        <div class="context-menu-item" @click="openEditDialog(contextMenuNode!); closeContextMenu()">
          <el-icon><Edit /></el-icon> 编辑
        </div>
        <div class="context-menu-item" @click="handleToggle(contextMenuNode!); closeContextMenu()">
          <el-icon><Close /></el-icon> {{ contextMenuNode?.is_active ? '禁用' : '启用' }}
        </div>
        <div class="context-menu-item danger" @click="handleDelete(contextMenuNode!); closeContextMenu()">
          <el-icon><Delete /></el-icon> 删除
        </div>
      </div>
    </teleport>

    <!-- ===== CREATE/EDIT DIALOG ===== -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="560px"
      :close-on-click-modal="false"
      class="category-dialog"
      destroy-on-close
    >
      <el-form
        ref="dialogFormRef"
        :model="editForm"
        label-position="top"
        class="dialog-form"
      >
        <el-form-item label="分类名称" :rules="[{ required: true, message: '请输入分类名称', trigger: 'blur' }]">
          <el-input v-model="editForm.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="父级分类">
          <el-select v-model="editForm.parent_id" placeholder="无（顶级分类）" clearable class="full-width" popper-class="dark-select-dropdown">
            <el-option
              v-for="n in treeData.filter(t => t.id !== editingId)"
              :key="n.id"
              :label="n.name"
              :value="n.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="颜色标识">
              <div class="color-picker-wrap">
                <el-color-picker v-model="editForm.color" :predefine="['#22C55E','#3B82F6','#A855F7','#EC4899','#F59E0B','#EF4444','#06B6D4','#8B5CF6']" />
                <span class="color-value" style="font-family:'Fira Code',monospace">{{ editForm.color }}</span>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重">
              <el-input-number v-model="editForm.sort_order" :min="0" :max="9999" controls-position="right" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述说明">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="分类描述（可选）" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="状态">
          <el-switch
            v-model="editForm.is_active"
            active-text="启用"
            inactive-text="禁用"
            active-color="#22C55E"
            inactive-color="#334155"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存修改' : '创建分类' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.categories-management {
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
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
  gap: 12px;
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

/* ===== MAIN CONTENT LAYOUT ===== */
.main-content {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  min-height: calc(100vh - 180px);
}

/* ===== TREE PANEL ===== */
.tree-panel {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.tree-header-title {
  font-size: 13px;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.tree-count {
  font-size: 12px;
  color: #64748B;
}

.tree-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.tree-body::-webkit-scrollbar {
  width: 4px;
}

.tree-body::-webkit-scrollbar-track {
  background: transparent;
}

.tree-body::-webkit-scrollbar-thumb {
  background: rgba(148,163,184,0.2);
  border-radius: 4px;
}

/* Category Tree */
.category-tree {
  background: transparent;
  --el-tree-node-hover-bg-color: rgba(30,41,59,0.5);
  --el-tree-text-color: #CBD5E1;
}

.category-tree :deep(.el-tree-node__content) {
  height: 40px;
  border-radius: 8px;
  margin: 2px 0;
  transition: all 0.2s ease;
}

.category-tree :deep(.el-tree-node__content:hover) {
  background: rgba(30,41,59,0.5);
}

.category-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(34,197,94,0.04)) !important;
  border: 1px solid rgba(34,197,94,0.25);
  box-shadow: 0 0 12px rgba(34,197,94,0.08);
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-right: 8px;
}

.tree-node-content.inactive {
  opacity: 0.5;
}

.node-color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 6px currentColor;
}

.node-label {
  font-size: 13.5px;
  font-weight: 500;
  color: inherit;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-badge {
  font-size: 10.5px;
  font-family: 'Fira Code', monospace;
  color: #64748B;
  background: rgba(30,41,59,0.5);
  padding: 1px 7px;
  border-radius: 8px;
  flex-shrink: 0;
}

.status-tag-mini {
  font-size: 10px !important;
  height: 18px !important;
  line-height: 17px !important;
  padding: 0 6px !important;
  flex-shrink: 0;
}

/* Tree Empty */
.tree-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
}

.tree-empty p {
  font-size: 13px;
  color: #64748B;
  margin: 0;
}

/* ===== EDIT PANEL ===== */
.edit-panel {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: #94A3B8;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.panel-title .el-icon {
  color: #22C55E;
}

.panel-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.panel-body::-webkit-scrollbar {
  width: 4px;
}

.panel-body::-webkit-scrollbar-thumb {
  background: rgba(148,163,184,0.2);
  border-radius: 4px;
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

.edit-form :deep(.el-input__inner),
.edit-form :deep(.el-textarea__inner) {
  color: #F8FAFC;
}

.edit-form :deep(.el-select .el-input__wrapper) {
  background: #1E293B;
}

.full-width {
  width: 100%;
}

.color-picker-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-value {
  font-size: 12px;
  color: #94A3B8;
}

.switch-wrap {
  display: flex;
  align-items: center;
}

.panel-actions {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(30,41,59,0.4);
  display: flex;
  justify-content: flex-end;
}

/* Panel Placeholder */
.panel-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 60px 20px;
}

.panel-placeholder p {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

/* Stats Footer */
.stats-footer {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid rgba(30,41,59,0.5);
  background: rgba(15,23,42,0.5);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
}

.stat-label {
  font-size: 11px;
  color: #64748B;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.stat-divider {
  width: 1px;
  height: 28px;
  background: #1E293B;
}

/* ===== CONTEXT MENU ===== */
.context-menu {
  position: fixed;
  z-index: 9999;
  min-width: 160px;
  padding: 5px;
  background: #161d2f;
  border: 1px solid #1E293B;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(34,197,94,0.05);
  animation: contextFadeIn 0.15s ease;
}

@keyframes contextFadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 13px;
  color: #CBD5E1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.context-menu-item:hover {
  background: rgba(34,197,94,0.1);
  color: #22C55E;
}

.context-menu-item.danger {
  color: #EF4444;
}

.context-menu-item.danger:hover {
  background: rgba(239,68,68,0.1);
  color: #F87171;
}

.context-menu-item .el-icon {
  font-size: 15px;
}

/* ===== DIALOG ===== */
.category-dialog :deep(.el-dialog) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.category-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(30,41,59,0.5);
}

.category-dialog :deep(.el-dialog__title) {
  color: #F8FAFC;
  font-size: 17px;
  font-weight: 700;
}

.category-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #64748B;
}

.category-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.category-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid rgba(30,41,59,0.5);
}

.dialog-form :deep(.el-form-item__label) {
  color: #94A3B8;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding-bottom: 4px;
}

.dialog-form :deep(.el-input__wrapper),
.dialog-form :deep(.el-textarea__inner) {
  background: #1E293B;
  box-shadow: 0 0 0 1px #334155;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dialog-form :deep(.el-input__wrapper:hover),
.dialog-form :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #475569;
}

.dialog-form :deep(.el-input__wrapper.is-focus),
.dialog-form :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #22C55E, 0 0 0 3px rgba(34,197,94,0.1);
}

.dialog-form :deep(.el-input__inner),
.dialog-form :deep(.el-textarea__inner) {
  color: #F8FAFC;
}

.dialog-form :deep(.el-select .el-input__wrapper) {
  background: #1E293B;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .tree-panel {
    max-height: 400px;
  }
}
</style>
