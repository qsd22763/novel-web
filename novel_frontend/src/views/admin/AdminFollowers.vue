<template>
  <div class="admin-followers">
    <div class="af-toolbar">
      <div class="af-search">
        <el-input
          v-model="searchAuthor"
          placeholder="搜索作者名..."
          clearable
          prefix-icon="Search"
          style="width: 260px"
          @keyup.enter="doSearch"
          @clear="doSearch"
        />
        <button class="af-btn af-btn--primary" @click="doSearch">搜索</button>
      </div>
      <div class="af-total">
        共 <strong>{{ totalCount }}</strong> 条粉丝记录
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      :data="tableData"
      v-loading="loading"
      stripe
      border
      style="width: 100%"
      row-class-name="af-row"
    >
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="用户名" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="af-username">{{ row.username }}</span>
        </template>
      </el-table-column>
      <el-table-column label="关注的作者" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="af-author" @click="goToAuthor(row.author_name)">{{ row.author_name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="关注时间" min-width="180" sortable />
      <el-table-column label="操作" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" size="small" link @click="handleDelete(row)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="af-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../../utils/request'

const router = useRouter()

const tableData = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchAuthor = ref('')
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (searchAuthor.value.trim()) {
      params.author_name = searchAuthor.value.trim()
    }
    const res: any = await request.get('/follow/followers/', { params })
    tableData.value = res.results || []
    totalCount.value = res.count || 0
  } catch (err) {
    console.error('获取粉丝列表失败:', err)
    ElMessage.error('获取粉丝列表失败')
  } finally {
    loading.value = false
  }
}

const doSearch = () => {
  currentPage.value = 1
  loadData()
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户「${row.username}」对作者「${row.author_name}」的关注记录吗？`,
      '确认删除',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    // 管理员通过后端接口删除（使用 unfollow 接口模拟）
    // 这里直接调用后端删除 API
    await request.post('/follow/admin_delete/', { id: row.id })
    ElMessage.success('已删除该关注记录')
    loadData()
  } catch (err: any) {
    if (err !== 'cancel') {
      // fallback: 直接用 unfollow 接口
      try {
        await request.post('/follow/unfollow/', { author_name: row.author_name })
        // 注意：这需要管理员以该用户身份操作，实际场景应提供管理端专用接口
        ElMessage.warning('已尝试取消关注（建议使用管理端专用删除接口）')
        loadData()
      } catch (e) {
        ElMessage.error('删除失败，请检查后端接口')
      }
    }
  }
}

const goToAuthor = (name: string) => {
  window.open(`/author/${encodeURIComponent(name)}`, '_blank')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-followers {
  /* 继承 admin layout 样式 */
}

.af-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.af-search {
  display: flex;
  align-items: center;
  gap: 10px;
}

.af-btn {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
  font-family: 'Fira Sans', system-ui, sans-serif;
}

.af-btn--primary {
  background: #22C55E;
  color: #fff;
  border-color: #22C55E;
  box-shadow: 0 2px 8px rgba(34,197,94,0.3);
}
.af-btn--primary:hover {
  background: #16A34A;
  border-color: #16A34A;
}

.af-total {
  font-size: 13px;
  color: #94A3B8;
}
.af-total strong {
  color: #22C55E;
  font-weight: 600;
}

:deep(.af-row) {
  transition: background-color 0.15s;
}
:deep(.af-row:hover > td) {
  background-color: rgba(34, 197, 94, 0.04) !important;
}

.af-username {
  font-weight: 600;
  color: #F8FAFC;
}

.af-author {
  color: #22C55E;
  cursor: pointer;
  transition: color 0.15s;
}
.af-author:hover {
  color: #86EFAC;
  text-decoration: underline;
}

.af-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-text-color: #94A3B8;
  --el-pagination-button-bg-color: #0F172A;
  --el-pagination-button-color: #94A3B8;
  --el-pagination-hover-color: #22C55E;
}
:deep(.el-pagination .el-pager li) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 6px;
  margin: 0 3px;
  color: #94A3B8;
}
:deep(.el-pagination .el-pager li.is-active) {
  background: #22C55E;
  border-color: #22C55E;
  color: #fff;
}
:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background: #0F172A;
  border: 1px solid #1E293B;
  border-radius: 6px;
}
</style>
