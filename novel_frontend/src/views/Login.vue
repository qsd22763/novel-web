<template>
  <div class="lp-root">
    <aside class="lp-side">
      <div class="lp-side__inner">
        <div class="lp-side__deco-line lp-side__deco-line--top"></div>

        <div class="lp-side__title-wrap">
          <span class="lp-side__char">墨</span>
          <span class="lp-side__char">香</span>
          <span class="lp-side__char">書</span>
          <span class="lp-side__char">閣</span>
        </div>

        <div class="lp-side__divider">
          <span class="lp-side__diamond"></span>
        </div>

        <blockquote class="lp-side__quote">
          <p class="lp-side__quote-text">「書中自有黃金屋，<br/>書中自有顏如玉。」</p>
          <cite class="lp-side__quote-cite">—— 宋真宗《勸學詩》</cite>
        </blockquote>

        <div class="lp-side__deco-line lp-side__deco-line--bottom"></div>

        <p class="lp-side__slogan">为阅读而生，为故事而活</p>
      </div>

      <div class="lp-side__bg-pattern" aria-hidden="true">
        <span v-for="n in 12" :key="n" class="lp-side__kanji">文</span>
      </div>
    </aside>

    <main class="lp-main">
      <div class="lp-card">
        <header class="lp-card__header">
          <div class="lp-card__logo">
            <span class="lp-card__logo-text">墨香</span>
          </div>
          <h1 class="lp-card__title">{{ isLogin ? '欢迎回来' : '加入书阁' }}</h1>
          <p class="lp-card__subtitle">{{ isLogin ? '登录以继续您的阅读之旅' : '创建账号，开启阅读新章' }}</p>
        </header>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="lp-form"
          @keyup.enter="handleSubmit"
        >
          <el-form-item label="用户名" prop="username" class="lp-form__item">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
              class="lp-input"
            />
          </el-form-item>

          <el-form-item v-if="!isLogin" label="邮箱" prop="email" class="lp-form__item">
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱地址"
              size="large"
              :prefix-icon="Message"
              class="lp-input"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password" class="lp-form__item">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              class="lp-input"
            />
          </el-form-item>

          <el-form-item v-if="!isLogin" label="确认密码" prop="password_confirm" class="lp-form__item">
            <el-input
              v-model="form.password_confirm"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              class="lp-input"
            />
          </el-form-item>

          <el-form-item v-if="isLogin" class="lp-form__item lp-form__item--options">
            <div class="lp-options">
              <el-checkbox v-model="rememberMe" class="lp-checkbox">记住我</el-checkbox>
              <a href="#" class="lp-forgot" @click.prevent>忘记密码？</a>
            </div>
          </el-form-item>

          <el-form-item class="lp-form__item lp-form__item--submit">
            <button
              type="button"
              class="lp-submit"
              :disabled="loading"
              @click="handleSubmit"
            >
              <span v-if="loading" class="lp-submit__loader"></span>
              <span v-else class="lp-submit__text">{{ isLogin ? '登　录' : '注　册' }}</span>
            </button>
          </el-form-item>
        </el-form>

        <footer class="lp-card__footer">
          <p class="lp-card__footer-text">
            {{ isLogin ? '还没有账号？' : '已有账号？' }}
            <span class="lp-toggle" @click="toggleMode">
              {{ isLogin ? '立即注册 →' : '← 返回登录' }}
            </span>
          </p>
        </footer>

        <div class="lp-divider" aria-hidden="true">
          <span class="lp-divider__line"></span>
          <span class="lp-divider__text">或</span>
          <span class="lp-divider__line"></span>
        </div>

        <div class="lp-social">
          <button class="lp-social__btn" title="微信登录" @click.prevent>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
          </button>
          <button class="lp-social__btn" title="QQ登录" @click.prevent>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,6 12,13 2,6"/></svg>
          </button>
          <button class="lp-social__btn" title="GitHub登录" @click.prevent>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api'

const router = useRouter()

const isLogin = ref(true)
const loading = ref(false)
const rememberMe = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})

const validatePasswordConfirm = (_rule: any, value: any, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = computed(() => ({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' },
  ],
  email: isLogin.value ? [] : [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' },
  ],
  password_confirm: isLogin.value ? [] : [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' },
  ],
}))

const toggleMode = () => {
  isLogin.value = !isLogin.value
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (isLogin.value) {
      const res: any = await authApi.login({
        username: form.username,
        password: form.password,
      })
      const user = res.user || res
      localStorage.setItem('user', JSON.stringify(user))
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      await authApi.register({
        username: form.username,
        email: form.email,
        password: form.password,
        password_confirm: form.password_confirm,
      })
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
    }
  } catch (error: any) {
    const detail = error?.response?.data
    if (typeof detail === 'object' && detail !== null) {
      const msgs = []
      for (const key of Object.keys(detail)) {
        const val = detail[key]
        if (Array.isArray(val)) msgs.push(val.join(' '))
        else if (typeof val === 'string') msgs.push(val)
      }
      if (msgs.length) { ElMessage.error(msgs.join('; ')); loading.value = false; return }
    }
    ElMessage.error(error?.response?.data?.detail || error?.message || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

.lp-root {
  --paper-bg: #FDFBF7;
  --ink: #1A1A1A;
  --muted: #6B7280;
  --accent: #CA8A04;
  --accent-dark: #A67C00;
  --border: #E0E0E0;
  --card-bg: #FFFFFF;
  --input-bg: #F5F1EA;
  --input-hover: #EDE8DF;

  min-height: 100vh;
  display: flex;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--paper-bg);
}

.lp-side {
  width: 40%;
  flex-shrink: 0;
  position: relative;
  background: var(--ink);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.lp-side__inner {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  padding: 3rem 2.5rem;
}

.lp-side__deco-line {
  width: 1px;
  background: linear-gradient(to bottom, transparent, var(--accent), transparent);
  align-self: center;
}

.lp-side__deco-line--top,
.lp-side__deco-line--bottom {
  height: 60px;
}

.lp-side__title-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}

.lp-side__char {
  font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--accent);
  line-height: 1.2;
  letter-spacing: 0.05em;
}

.lp-side__divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.lp-side__divider::before,
.lp-side__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(202, 138, 4, 0.5), transparent);
}

.lp-side__diamond {
  width: 6px;
  height: 6px;
  background: var(--accent);
  transform: rotate(45deg);
  flex-shrink: 0;
}

.lp-side__quote {
  margin: 0;
  text-align: center;
  padding: 0 1rem;
}

.lp-side__quote-text {
  font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
  font-size: 1.05rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.75);
  line-height: 2;
  margin: 0 0 0.75rem;
  letter-spacing: 0.08em;
}

.lp-side__quote-cite {
  font-size: 0.78rem;
  color: rgba(202, 138, 4, 0.6);
  font-style: normal;
  letter-spacing: 0.05em;
}

.lp-side__slogan {
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.25);
  letter-spacing: 0.2em;
  margin: 0;
}

.lp-side__bg-pattern {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
  pointer-events: none;
}

.lp-side__kanji {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 5rem;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.018);
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.lp-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  background: var(--paper-bg);
}

.lp-card {
  width: 100%;
  max-width: 420px;
}

.lp-card__header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.lp-card__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  background: var(--ink);
  border-radius: 14px;
  margin-bottom: 1.25rem;
}

.lp-card__logo-text {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 0.03em;
}

.lp-card__title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.5rem;
  letter-spacing: 0.03em;
}

.lp-card__subtitle {
  font-family: 'Libre Baskerville', 'Noto Sans SC', sans-serif;
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
  letter-spacing: 0.02em;
}

.lp-form {
  margin-bottom: 0;
}

.lp-form__item {
  margin-bottom: 1.15rem;
}

.lp-form__item--options {
  margin-bottom: 0.5rem;
}

.lp-form__item--submit {
  margin-top: 1.5rem;
  margin-bottom: 0;
}

.lp-form :deep(.el-form-item__label) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.82rem;
  font-weight: 500;
  color: #5C5040;
  padding-bottom: 6px;
  letter-spacing: 0.03em;
}

.lp-form :deep(.el-form-item__error) {
  font-size: 0.78rem;
  color: #C0392B;
}

.lp-input :deep(.el-input__wrapper) {
  background: var(--input-bg);
  border: 1.5px solid transparent;
  border-radius: 10px;
  padding: 2px 14px;
  box-shadow: none !important;
  transition: border-color 0.25s, background-color 0.25s;
}

.lp-input :deep(.el-input__wrapper:hover) {
  background: var(--input-hover);
  border-color: rgba(202, 138, 4, 0.4);
}

.lp-input :deep(.el-input__wrapper.is-focus) {
  background: var(--card-bg);
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(202, 138, 4, 0.1) !important;
}

.lp-input :deep(.el-input__inner) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.92rem;
  color: var(--ink);
}

.lp-input :deep(.el-input__inner::placeholder) {
  color: #B8AD9E;
}

.lp-input :deep(.el-input__prefix-icon) {
  color: #B8AD9E;
  transition: color 0.2s;
}

.lp-input :deep(.el-input__wrapper.is-focus .el-input__prefix-icon) {
  color: var(--accent);
}

.lp-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.lp-checkbox :deep(.el-checkbox__label) {
  font-size: 0.83rem;
  color: #7A6E60;
}

.lp-checkbox :deep(.el-checkbox__inner) {
  border-color: #C9C0B0;
  border-radius: 4px;
}

.lp-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: var(--accent);
  border-color: var(--accent);
}

.lp-forgot {
  font-size: 0.83rem;
  color: #9A8E7E;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s;
}

.lp-forgot:hover {
  color: var(--accent);
}

.lp-submit {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
  box-shadow: 0 4px 20px rgba(202, 138, 4, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
}

.lp-submit:hover {
  opacity: 0.92;
}

.lp-submit:active {
  opacity: 0.85;
}

.lp-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.lp-submit__text {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.15em;
}

.lp-submit__loader {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: lp-spin 0.6s linear infinite;
}

@keyframes lp-spin {
  to { transform: rotate(360deg); }
}

.lp-card__footer {
  text-align: center;
  margin-top: 1.5rem;
}

.lp-card__footer-text {
  font-size: 0.87rem;
  color: #9A8E7E;
  margin: 0;
}

.lp-toggle {
  color: var(--accent);
  font-weight: 500;
  cursor: pointer;
  margin-left: 0.3em;
  transition: color 0.2s;
}

.lp-toggle:hover {
  color: var(--accent-dark);
}

.lp-divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.75rem 0 1.25rem;
}

.lp-divider__line {
  flex: 1;
  height: 1px;
  background: #E8E0D0;
}

.lp-divider__text {
  font-size: 0.78rem;
  color: #C0B8AA;
  flex-shrink: 0;
}

.lp-social {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.lp-social__btn {
  width: 46px;
  height: 46px;
  background: var(--input-bg);
  border: 1.5px solid #E8E0D0;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7A6E60;
  transition: border-color 0.2s, color 0.2s, background-color 0.2s;
}

.lp-social__btn:hover {
  background: var(--input-hover);
  border-color: var(--accent);
  color: var(--accent);
}

@media (max-width: 1024px) {
  .lp-side__char {
    font-size: 2.2rem;
  }
}

@media (max-width: 768px) {
  .lp-side {
    display: none;
  }

  .lp-main {
    min-height: 100vh;
    padding: 2.5rem 1.5rem;
  }
}

@media (max-width: 375px) {
  .lp-card__title {
    font-size: 1.5rem;
  }

  .lp-card {
    max-width: 100%;
  }

  .lp-submit {
    height: 46px;
  }

  .lp-main {
    padding: 2rem 1rem;
  }
}
</style>
