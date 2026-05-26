<template>
  <div class="login-page">
    <div class="login-decoration">
      <div class="decoration-content">
        <h1 class="brand">墨香书阁</h1>
        <p class="slogan">为阅读而生，为故事而活</p>
        <div class="book-illustration">
          <div class="book-stack">
            <div class="book b1"></div>
            <div class="book b2"></div>
            <div class="book b3"></div>
            <div class="book b4"></div>
          </div>
        </div>
        <div class="decoration-quote">
          <p>"一本好书，一杯清茶，一个下午。"</p>
        </div>
      </div>
      <div class="decoration-bg">
        <div class="bg-circle circle-1"></div>
        <div class="bg-circle circle-2"></div>
        <div class="bg-circle circle-3"></div>
      </div>
    </div>

    <div class="login-container">
      <div class="login-card">
        <div class="card-header">
          <h2>{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
          <p>{{ isLogin ? '登录以继续您的阅读之旅' : '开始您的阅读之旅' }}</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="login-form">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="邮箱" prop="email" v-if="!isLogin">
            <el-input
              v-model="form.email"
              placeholder="请输入邮箱"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="password_confirm" v-if="!isLogin">
            <el-input
              v-model="form.password_confirm"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item v-if="isLogin">
            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              class="submit-btn"
              size="large"
              @click="handleSubmit"
              :loading="loading"
              :round="true"
            >
              {{ isLogin ? '登 录' : '注 册' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="card-footer">
          <p>
            {{ isLogin ? '还没有账号？' : '已有账号？' }}
            <span @click="toggleMode" class="toggle-link">{{ isLogin ? '立即注册' : '立即登录' }}</span>
          </p>
        </div>

        <div class="divider">
          <span>或</span>
        </div>

        <div class="social-login">
          <el-button class="social-btn" circle>
            <span class="social-icon">微</span>
          </el-button>
          <el-button class="social-btn" circle>
            <span class="social-icon">腾</span>
          </el-button>
          <el-button class="social-btn" circle>
            <span class="social-icon">git</span>
          </el-button>
        </div>
      </div>
    </div>
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

const validatePasswordConfirm = (rule: any, value: any, callback: any) => {
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
      const res = await authApi.login({
        username: form.username,
        password: form.password,
      })
      localStorage.setItem('user', JSON.stringify(res.user))
      localStorage.setItem('token', res.token)
      ElMessage.success('登录成功')
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
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  background: #faf8f5;
}

.login-decoration {
  flex: 1;
  position: relative;
  background: linear-gradient(160deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
  padding: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.decoration-content {
  position: relative;
  z-index: 2;
  text-align: center;
}

.brand {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 3rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 1rem;
}

.slogan {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 3rem;
}

.book-illustration {
  margin: 0 auto 3rem;
}

.book-stack {
  position: relative;
  width: 200px;
  height: 280px;
  margin: 0 auto;
}

.book {
  position: absolute;
  border-radius: 4px 12px 12px 4px;
  transform-origin: left bottom;
}

.b1 {
  width: 45px;
  height: 220px;
  background: linear-gradient(90deg, #e8d5b7 0%, #d4c4a8 100%);
  left: 20px;
  bottom: 0;
  transform: rotate(-6deg);
}

.b2 {
  width: 50px;
  height: 240px;
  background: linear-gradient(90deg, #8b7355 0%, #6b5344 100%);
  left: 55px;
  bottom: 0;
  transform: rotate(-2deg);
}

.b3 {
  width: 40px;
  height: 200px;
  background: linear-gradient(90deg, #c9a959 0%, #a08040 100%);
  left: 95px;
  bottom: 0;
  transform: rotate(3deg);
}

.b4 {
  width: 48px;
  height: 230px;
  background: linear-gradient(90deg, #6b8e7d 0%, #4a6b5a 100%);
  left: 130px;
  bottom: 0;
  transform: rotate(7deg);
}

.decoration-quote {
  max-width: 300px;
  margin: 0 auto;
}

.decoration-quote p {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-style: italic;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.decoration-bg {
  position: absolute;
  inset: 0;
  z-index: 1;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.05;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: #fff;
  top: -100px;
  right: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: #fff;
  bottom: -50px;
  left: -50px;
}

.circle-3 {
  width: 200px;
  height: 200px;
  background: #fff;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.login-container {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 24px;
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h2 {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 0.5rem;
}

.card-header p {
  font-size: 0.9rem;
  color: #888;
  margin: 0;
}

.login-form {
  margin-bottom: 1rem;
}

.login-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 16px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.forgot-link {
  color: #888;
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #1a1a1a;
}

.submit-btn {
  width: 100%;
  height: 50px;
  font-size: 1rem;
  border-radius: 25px;
  background: #1a1a1a;
  border-color: #1a1a1a;
  margin-top: 0.5rem;
}

.submit-btn:hover {
  background: #333;
  border-color: #333;
}

.card-footer {
  text-align: center;
  margin-top: 1rem;
}

.card-footer p {
  font-size: 0.9rem;
  color: #888;
  margin: 0;
}

.toggle-link {
  color: #1a1a1a;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.toggle-link:hover {
  color: #555;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #eee;
}

.divider span {
  padding: 0 1rem;
  font-size: 0.8rem;
  color: #aaa;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.social-btn {
  width: 48px;
  height: 48px;
  border: 1px solid #eee;
  background: #fff;
  transition: all 0.2s;
}

.social-btn:hover {
  background: #f5f5f5;
  border-color: #ddd;
  transform: translateY(-2px);
}

.social-icon {
  font-size: 0.85rem;
  color: #666;
}

@media (max-width: 1024px) {
  .login-decoration {
    display: none;
  }

  .login-container {
    width: 100%;
    min-height: 100vh;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 2rem 1.5rem;
    border-radius: 20px;
  }

  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>
