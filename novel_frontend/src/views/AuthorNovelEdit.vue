<template>
  <div class="novel-edit">
    <header class="edit-header">
      <div class="inner">
        <router-link to="/author" class="back-link">← 返回作者中心</router-link>
        <h1 class="page-title">{{ isEdit ? '编辑作品信息' : '创作新书' }}</h1>
        <div class="header-actions">
          <button class="btn-ghost" @click="onCancel">取消</button>
          <button class="btn-primary" :disabled="saving" @click="onSave">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </header>

    <main class="edit-main">
      <form class="form" @submit.prevent="onSave">
        <div class="row">
          <label class="label">书名 <span class="req">*</span></label>
          <input v-model="form.title" class="input" maxlength="100" placeholder="给你的作品起一个名字" required />
        </div>

        <div class="row two-col">
          <div>
            <label class="label">分类 <span class="req">*</span></label>
            <select v-model="form.category" class="input" required>
              <option value="">请选择</option>
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="label">连载状态</label>
            <select v-model.number="form.status" class="input">
              <option :value="0">连载中</option>
              <option :value="1">已完结</option>
            </select>
          </div>
        </div>

        <div class="row">
          <label class="label">封面</label>
          <div class="cover-row">
            <input v-model="form.cover" class="input" placeholder="可粘贴图片链接，或点击右侧上传" />
            <label class="upload-btn">
              {{ uploading ? '上传中…' : '上传图片' }}
              <input type="file" accept="image/*" hidden @change="onUpload" :disabled="uploading" />
            </label>
          </div>
          <div v-if="form.cover" class="cover-preview">
            <img :src="resolveCoverPreview(form.cover)" alt="封面预览" @error="onCoverError" />
          </div>
        </div>

        <div class="row">
          <label class="label">标签</label>
          <input v-model="form.tags" class="input" maxlength="200" placeholder="多个标签用英文逗号分隔，如：热血,异世界,搞笑" />
        </div>

        <div class="row">
          <label class="label">作品简介 <span class="req">*</span></label>
          <textarea v-model="form.description" class="textarea" rows="8" maxlength="2000" required placeholder="一段引人入胜的简介，会显示在小说详情页"></textarea>
          <span class="counter">{{ form.description.length }} / 2000</span>
        </div>

        <div v-if="isEdit" class="audit-info">
          <span>当前审核状态：</span>
          <strong>{{ form.audit_status_display || '草稿' }}</strong>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authorApi } from '../api'
import { resolveCover } from '../utils/image'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const uploading = ref(false)

const categories = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']

const form = reactive({
  title: '',
  category: '',
  status: 0 as number,
  cover: '',
  tags: '',
  description: '',
  audit_status_display: '',
})

const onCoverError = (e: Event) => {
  (e.target as HTMLImageElement).style.display = 'none'
}

const resolveCoverPreview = resolveCover

const onUpload = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert('图片不能超过 5MB')
    target.value = ''
    return
  }
  uploading.value = true
  try {
    const res: any = await authorApi.uploadCover(file)
    form.cover = res.url
  } catch (err: any) {
    alert(err?.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
    target.value = ''
  }
}

const onCancel = () => router.push('/author')

const onSave = async () => {
  if (!form.title || !form.category || !form.description) {
    alert('请补全必填项')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title,
      category: form.category,
      status: form.status,
      cover: form.cover,
      tags: form.tags,
      description: form.description,
    }
    if (isEdit.value) {
      await authorApi.updateNovel(Number(route.params.id), payload)
    } else {
      const res = await authorApi.createNovel(payload)
      router.replace(`/author/novel/${res.id}/chapters`)
      return
    }
    router.push('/author')
  } catch (err: any) {
    alert(err?.response?.data?.detail || '保存失败，请重试')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (isEdit.value) {
    const res = await authorApi.novelDetail(Number(route.params.id))
    Object.assign(form, res.data)
  }
})
</script>

<style scoped>
.novel-edit {
  min-height: 100vh;
  background: #FDFBF7;
  font-family: 'Noto Serif SC', serif;
  color: #1A1A1A;
}
.edit-header {
  background: #1A1A1A;
  color: #FDFBF7;
  position: sticky;
  top: 0;
  z-index: 10;
}
.inner {
  max-width: 880px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.back-link {
  color: #FDFBF7;
  text-decoration: none;
  font-size: 14px;
  opacity: 0.8;
}
.back-link:hover { opacity: 1; color: #CA8A04; }
.page-title {
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 2px;
  margin: 0;
  flex: 1;
}
.header-actions { display: flex; gap: 10px; }
.btn-ghost, .btn-primary {
  padding: 8px 18px;
  border-radius: 2px;
  font-size: 14px;
  cursor: pointer;
  font-family: inherit;
  border: 1px solid transparent;
}
.btn-ghost {
  background: transparent;
  border-color: #444;
  color: #FDFBF7;
}
.btn-ghost:hover { border-color: #CA8A04; color: #CA8A04; }
.btn-primary {
  background: #CA8A04;
  color: #fff;
}
.btn-primary:hover { background: #A87403; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.edit-main {
  max-width: 880px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.form {
  background: #fff;
  border: 1px solid #ECE7DC;
  border-radius: 4px;
  padding: 32px;
}
.row { margin-bottom: 22px; position: relative; }
.row.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.label {
  display: block;
  font-size: 14px;
  margin-bottom: 8px;
  font-family: 'Noto Sans SC', sans-serif;
  color: #333;
}
.req { color: #C62828; margin-left: 2px; }
.input, .textarea {
  width: 100%;
  border: 1px solid #D8D2C4;
  background: #FDFBF7;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  color: #1A1A1A;
  border-radius: 2px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
.input:focus, .textarea:focus { border-color: #CA8A04; }
.textarea { resize: vertical; line-height: 1.7; }
.counter {
  position: absolute;
  right: 0;
  bottom: -20px;
  font-size: 12px;
  color: #999;
}

.cover-row {
  display: flex;
  gap: 10px;
  align-items: stretch;
}
.cover-row .input { flex: 1; }
.upload-btn {
  display: inline-flex;
  align-items: center;
  padding: 0 18px;
  background: #fff;
  border: 1px solid #D8D2C4;
  color: #1A1A1A;
  font-size: 13px;
  border-radius: 2px;
  cursor: pointer;
  white-space: nowrap;
  font-family: 'Noto Sans SC', sans-serif;
  transition: all 0.2s;
}
.upload-btn:hover { border-color: #CA8A04; color: #CA8A04; }

.cover-preview {
  margin-top: 12px;
  width: 120px;
  height: 160px;
  border: 1px solid #ECE7DC;
  overflow: hidden;
  border-radius: 2px;
}
.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.audit-info {
  padding: 12px 16px;
  background: #FAF6EC;
  border-left: 3px solid #CA8A04;
  font-size: 14px;
  color: #555;
  font-family: 'Noto Sans SC', sans-serif;
}
.audit-info strong { color: #CA8A04; margin-left: 6px; }

@media (max-width: 768px) {
  .inner { padding: 12px 16px; flex-wrap: wrap; gap: 12px; }
  .edit-body { padding: 20px 16px; max-width: 100%; }
  .form-row { grid-template-columns: 1fr; }
  .form-group { margin-bottom: 18px; }
  .form-input, .form-textarea, .form-select { font-size: 15px; }
  textarea.form-textarea { min-height: 140px; }
  .cover-upload-area { height: 160px; }
  .btn-row { flex-direction: column-reverse; }
  .btn-primary, .btn-secondary { width: 100%; text-align: center; justify-content: center; }
}
@media (max-width: 480px) {
  .page-title { font-size: 20px; }
  .edit-header .back-link { font-size: 13px; }
}
</style>
