<template>
  <div class="chapter-edit">
    <header class="head">
      <div class="inner">
        <router-link :to="`/author/novel/${novelId}/chapters`" class="back-link">← 返回章节列表</router-link>
        <h1 class="title">{{ isEdit ? '编辑章节' : '撰写新章节' }}</h1>
        <div class="actions">
          <span class="status-tag" v-if="lastSavedAt">已保存 {{ lastSavedAt }}</span>
          <button class="btn-ghost" @click="onSaveDraft" :disabled="saving">存草稿</button>
          <button class="btn-primary" @click="onPublish" :disabled="saving">
            {{ saving ? '保存中…' : '发布章节' }}
          </button>
        </div>
      </div>
    </header>

    <main class="main">
      <input
        v-model="form.title"
        class="title-input"
        placeholder="章节标题，例如：第一章 风起云涌"
        maxlength="100"
      />
      <div class="toolbar">
        <span class="word-count">字数：{{ wordCount }}</span>
        <span class="hint">提示：用空行分段，段首会自动缩进两格</span>
      </div>
      <textarea
        v-model="form.content"
        class="content-input"
        placeholder="开始你的故事…"
        @input="onContentInput"
      ></textarea>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authorApi } from '../api'

const route = useRoute()
const router = useRouter()

const novelId = Number(route.params.novelId)
const chapterId = computed(() => route.params.id ? Number(route.params.id) : null)
const isEdit = computed(() => !!chapterId.value)

const saving = ref(false)
const lastSavedAt = ref('')

const form = reactive({
  title: '',
  content: '',
  publish_status: 1 as number,
})

const wordCount = computed(() => form.content.replace(/\s/g, '').length)

let autoSaveTimer: number | null = null
const onContentInput = () => {
  if (autoSaveTimer) window.clearTimeout(autoSaveTimer)
  autoSaveTimer = window.setTimeout(() => {
    if (isEdit.value) doSave(form.publish_status, true)
  }, 8000)
}

const doSave = async (publishStatus: number, silent = false) => {
  if (!form.title.trim()) {
    if (!silent) alert('请填写章节标题')
    return null
  }
  if (!form.content.trim()) {
    if (!silent) alert('请填写章节内容')
    return null
  }
  saving.value = true
  try {
    if (isEdit.value && chapterId.value) {
      await authorApi.updateChapter(chapterId.value, {
        title: form.title,
        content: form.content,
        publish_status: publishStatus,
      })
      form.publish_status = publishStatus
    } else {
      const res = await authorApi.createChapter({
        novel: novelId,
        title: form.title,
        content: form.content,
        publish_status: publishStatus,
      })
      router.replace(`/author/novel/${novelId}/chapter/${res.id}/edit`)
    }
    const now = new Date()
    lastSavedAt.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
    return true
  } catch (err: any) {
    if (!silent) alert(err?.response?.data?.detail || '保存失败')
    return null
  } finally {
    saving.value = false
  }
}

const onSaveDraft = async () => {
  const ok = await doSave(0)
  if (ok && !isEdit.value) return
  if (ok) alert('草稿已保存')
}

const onPublish = async () => {
  const ok = await doSave(1)
  if (ok) {
    alert('章节已发布')
    router.push(`/author/novel/${novelId}/chapters`)
  }
}

onMounted(async () => {
  if (isEdit.value && chapterId.value) {
    const res = await authorApi.chapterDetail(chapterId.value)
    form.title = res.title
    form.content = res.content || ''
    form.publish_status = res.publish_status
  }
})
</script>

<style scoped>
.chapter-edit {
  min-height: 100vh;
  background: #FDFBF7;
  font-family: 'Noto Serif SC', serif;
  color: #1A1A1A;
  display: flex;
  flex-direction: column;
}
.head {
  background: #1A1A1A;
  color: #FDFBF7;
  position: sticky;
  top: 0;
  z-index: 10;
}
.inner {
  max-width: 880px;
  margin: 0 auto;
  padding: 14px 24px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.back-link {
  color: #FDFBF7;
  text-decoration: none;
  font-size: 14px;
  opacity: 0.85;
}
.back-link:hover { color: #CA8A04; opacity: 1; }
.title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 2px;
}
.actions { display: flex; align-items: center; gap: 10px; }
.status-tag {
  font-size: 12px;
  color: #999;
  font-family: 'Noto Sans SC', sans-serif;
  margin-right: 8px;
}
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
.btn-primary { background: #CA8A04; color: #fff; }
.btn-primary:hover { background: #A87403; }
.btn-primary:disabled, .btn-ghost:disabled { opacity: 0.6; cursor: not-allowed; }

.main {
  max-width: 880px;
  margin: 0 auto;
  padding: 36px 24px 80px;
  width: 100%;
  flex: 1;
  box-sizing: border-box;
}
.title-input {
  width: 100%;
  font-size: 28px;
  font-family: inherit;
  font-weight: 600;
  border: none;
  background: transparent;
  padding: 12px 0;
  border-bottom: 2px solid #ECE7DC;
  outline: none;
  color: #1A1A1A;
  letter-spacing: 1px;
  box-sizing: border-box;
}
.title-input:focus { border-bottom-color: #CA8A04; }
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  font-size: 13px;
  color: #888;
  font-family: 'Noto Sans SC', sans-serif;
}
.word-count { color: #CA8A04; }
.content-input {
  width: 100%;
  min-height: 65vh;
  border: 1px solid #ECE7DC;
  background: #fff;
  padding: 28px 32px;
  font-size: 17px;
  line-height: 2;
  font-family: inherit;
  color: #1A1A1A;
  border-radius: 4px;
  outline: none;
  resize: vertical;
  box-sizing: border-box;
}
.content-input:focus { border-color: #CA8A04; }
</style>
