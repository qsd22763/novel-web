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
          <el-form-item v-if="isLogin" label="身份选择" class="lp-form__item lp-form__item--role">
            <div class="lp-role-selector">
              <label
                class="lp-role-option"
                :class="{ 'lp-role-option--active': userRole === 'user' }"
                @click="userRole = 'user'"
              >
                <span class="lp-role-radio"></span>
                <span class="lp-role-label">普通用户</span>
              </label>
              <label
                class="lp-role-option"
                :class="{ 'lp-role-option--active': userRole === 'admin' }"
                @click="userRole = 'admin'"
              >
                <span class="lp-role-radio"></span>
                <span class="lp-role-label">管理员用户</span>
              </label>
            </div>
          </el-form-item>

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
              placeholder="请输入QQ邮箱 (xxx@qq.com)"
              size="large"
              :prefix-icon="Message"
              class="lp-input"
            />
          </el-form-item>

          <el-form-item v-if="!isLogin" label="验证码" prop="verification_code" class="lp-form__item lp-form__item--code">
            <div class="lp-code-row">
              <el-input
                v-model="form.verification_code"
                placeholder="请输入6位验证码"
                size="large"
                class="lp-code__input"
                maxlength="6"
              />
              <button
                type="button"
                class="lp-code__btn"
                :class="{ 'lp-code__btn--disabled': isCountingDown || !form.email }"
                :disabled="isCountingDown || !form.email"
                @click.prevent="handleSendCode"
              >
                {{ isCountingDown ? `${countdown}s后重试` : '获取验证码' }}
              </button>
            </div>
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

          <el-form-item v-if="isLogin && userRole === 'user'" class="lp-form__item lp-form__item--options">
            <div class="lp-options">
              <el-checkbox v-model="rememberMe" class="lp-checkbox">记住我</el-checkbox>
              <a href="#" class="lp-forgot" @click.prevent>忘记密码？</a>
            </div>
          </el-form-item>

          <el-form-item v-if="isLogin && userRole === 'admin'" class="lp-form__item lp-form__item--options">
            <div class="lp-options">
              <el-checkbox v-model="rememberMe" class="lp-checkbox">记住我</el-checkbox>
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

        <footer v-if="userRole === 'user'" class="lp-card__footer">
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
          <!-- QQ 登录 -->
          <button class="lp-social__btn lp-social__btn--qq" title="QQ登录" @click.prevent="handleQQLogin">
            <svg class="lp-icon-qq" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M21.395 15.035a39.548 39.548 0 00-.803-2.264l-1.079-2.695c.001-.032.014-.602.014-.895C19.527 5.88 16.295 2 12 2S4.473 5.88 4.473 9.181c0 .293.013.863.014.895L3.408 12.77a39.548 39.548 0 00-.803 2.264c-.751 2.441-.506 3.957-.25 4.28.518.642 1.854.79 2.76.568l.77-.192c.598-.149 1.178-.294 1.51-.294.168 0 .348.02.53.06A10 10 0 0012 19.82c1.393 0 2.73-.307 3.974-.863.183-.04.363-.06.531-.06.332 0 .912.145 1.51.294l.77.192c.906.222 2.242.074 2.76-.568.256-.323.501-1.839-.25-4.28zM12 4.5c2.62 0 4.75 2.015 4.75 4.5S14.62 13.5 12 13.5 7.25 11.485 7.25 9.5 9.38 4.5 12 4.5z"/>
              <circle cx="9.5" cy="9" r="1.25"/>
              <circle cx="14.5" cy="9" r="1.25"/>
            </svg>
          </button>
          <!-- GitHub 登录（保留原有） -->
          <button class="lp-social__btn" title="GitHub登录" @click.prevent>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
          </button>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api'

const router = useRouter()
const route = useRoute()

const isLogin = ref(true)
const loading = ref(false)
const rememberMe = ref(false)
const userRole = ref<'user' | 'admin'>('user')
const formRef = ref()
// 验证码倒计时
const isCountingDown = ref(false)
const countdown = ref(60)
let timer: ReturnType<typeof setInterval> | null = null

const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  verification_code: '',
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
  verification_code: isLogin.value ? [] : [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' },
  ],
}))

const toggleMode = () => {
  isLogin.value = !isLogin.value
  formRef.value?.clearValidate()
}

// 发送验证码
const handleSendCode = async () => {
  if (!form.email) {
    ElMessage.warning('请先输入QQ邮箱')
    return
  }
  if (!form.email.endsWith('@qq.com')) {
    ElMessage.warning('仅支持QQ邮箱注册（xxx@qq.com）')
    return
  }
  try {
    await authApi.sendVerificationCode(form.email)
    ElMessage.success('验证码已发送，请查收邮件')
    startCountdown()
  } catch (error: any) {
    const detail = error?.response?.data
    if (detail?.email) {
      ElMessage.error(detail.email[0])
    } else {
      ElMessage.error(error?.response?.data?.detail || '发送失败，请稍后重试')
    }
  }
}

// 启动60s倒计时
const startCountdown = () => {
  isCountingDown.value = true
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      stopCountdown()
    }
  }, 1000)
}

// 停止倒计时
const stopCountdown = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  isCountingDown.value = false
  countdown.value = 60
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// ── QQ登录：跳转QQ授权页面 ──
const handleQQLogin = async () => {
  try {
    const res: any = await authApi.getQQAuthUrl()
    if (res?.auth_url) {
      window.location.href = res.auth_url
    } else {
      ElMessage.warning('QQ授权地址获取失败，请稍后重试')
    }
  } catch {
    ElMessage.error('QQ登录服务暂时不可用')
  }
}

// ── 页面加载时检测OAuth回调 ──
const handleOAuthCallback = async () => {
  const code = route.query.code as string
  const provider = route.query.provider as string || route.query.state as string

  if (!code) return

  try {
    let res: any
    // 默认走 QQ 回调
    res = await authApi.qqCallback(code, provider)

    if (res?.token) {
      localStorage.setItem('auth_token', res.token)
      localStorage.setItem('user_info', JSON.stringify(res.user))
      ElMessage.success('第三方登录成功')
      router.push('/')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.error || error?.response?.data?.detail || '第三方登录失败')
  }
}

onMounted(() => {
  handleOAuthCallback()
})

const handleSubmit = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (isLogin.value) {
      if (userRole.value === 'admin') {
        // 管理员登录：去管理员表校验，跳转后台管理页
        const res: any = await authApi.adminLogin({
          username: form.username,
          password: form.password,
        })
        const user = res.user || res
        localStorage.setItem('user', JSON.stringify(user))
        ElMessage.success('管理员登录成功')
        router.push('/admin')
      } else {
        // 普通用户登录：去普通用户表校验，跳转阅读首页
        const res: any = await authApi.login({
          username: form.username,
          password: form.password,
        })
        const user = res.user || res
        localStorage.setItem('user', JSON.stringify(user))
        ElMessage.success('登录成功')
        router.push('/')
      }
    } else {
      await authApi.register({
        username: form.username,
        email: form.email,
        password: form.password,
        password_confirm: form.password_confirm,
        verification_code: form.verification_code,
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
@import url('https://fonts.loli.net/css2?family=Cormorant+Garamond:wght@400;600;700&family=Libre+Baskerville:wght@400;700&family=Noto+Serif+SC:wght@400;500;600;700;900&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

/* ══════════════════════════════════════════════
   Design Tokens — 轻奢新中式书香色系
   ══════════════════════════════════════════════ */
.lp-root {
  /* 宣纸米白 */
  --rice: #FAF6F0;
  --rice-warm: #FBF8F3;
  --rice-cream: #F7F1E8;
  --rice-pale: #FFFDF9;

  /* 古墨棕 */
  --ink: #1A1511;
  --ink-warm: #251E18;
  --ink-mid: #3D332A;
  --brown-deep: #524438;
  --brown: #736354;
  --brown-soft: #9E8D7A;
  --brown-fade: #C4B5A5;
  --brown-dust: #DDD2C5;

  /* 鎏金 */
  --gold: #DDB96B;
  --gold-main: #C9A04A;
  --gold-deep: #A88532;
  --gold-dim: #8E7028;
  --gold-glow: rgba(221, 185, 107, 0.18);
  --gold-halo: rgba(201, 160, 74, 0.12);
  --gold-whisper: rgba(201, 160, 74, 0.06);

  /* 功能 */
  --card: #FFFCF7;
  --input-bg: #F0E8DC;
  --input-hover: #E8DDD0;
  --border: #DED4C6;
  --error: #B84A44;
  --hint: #ADA092;

  min-height: 100vh;
  display: flex;
  font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--rice);
  position: relative;
  overflow-x: hidden;
}

/* ── 全局纸张颗粒肌理 ── */
.lp-root::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.42;
  background-image:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.72' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
  background-size: 180px 180px;
}

/* ── 全局环境柔光 — 右上角鎏金微晕 ── */
.lp-root::after {
  content: '';
  position: fixed;
  top: -15%;
  right: -8%;
  width: 55%;
  height: 130%;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 40% 30%, rgba(221, 185, 107, 0.045) 0%, transparent 60%),
    radial-gradient(ellipse at 60% 70%, rgba(201, 160, 74, 0.028) 0%, transparent 55%);
}

/* ══════════════════════════════════════════════
   1. 左侧侧边栏 — 暗纹古籍 + 径向渐变
   ══════════════════════════════════════════════ */
.lp-side {
  width: 45%;
  flex-shrink: 0;
  position: relative;
  /* 从上至下柔和深棕径向渐变 */
  background:
    radial-gradient(120% 100% at 50% -10%, rgba(45, 36, 28, 0.6) 0%, transparent 55%),
    radial-gradient(80% 100% at 20% 110%, rgba(37, 30, 24, 0.5) 0%, transparent 50%),
    linear-gradient(175deg, #1A1511 0%, #231C16 35%, #1A1511 70%, #14100D 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  z-index: 1;
}

/* 左侧 — 低透明度暗纹古籍毛笔字底图 */
.lp-side::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.07;
  background-image:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Ctext x='30' y='90' font-family='Noto Serif SC,STSong,SimSun,serif' font-size='72' font-weight='900' fill='%23DDB96B' opacity='0.6'%3E詩%3C/text%3E%3Ctext x='280' y='170' font-family='Noto Serif SC,STSong,SimSun,serif' font-size='56' font-weight='900' fill='%23DDB96B' opacity='0.4'%3E書%3C/text%3E%3Ctext x='60' y='280' font-family='Noto Serif SC,STSong,SimSun,serif' font-size='64' font-weight='900' fill='%23DDB96B' opacity='0.5'%3E畫%3C/text%3E%3Ctext x='260' y='360' font-family='Noto Serif SC,STSong,SimSun,serif' font-size='48' font-weight='900' fill='%23DDB96B' opacity='0.35'%3E韻%3C/text%3E%3Ctext x='150' y='220' font-family='Noto Serif SC,STSong,SimSun,serif' font-size='52' font-weight='900' fill='%23DDB96B' opacity='0.3'%3E雅%3C/text%3E%3C/svg%3E");
  background-size: 320px 320px;
  background-position: center;
  filter: blur(1px);
}

/* 左侧 — 墨韵光斑 */
.lp-side::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse at 25% 15%, rgba(221, 185, 107, 0.055) 0%, transparent 45%),
    radial-gradient(ellipse at 75% 85%, rgba(221, 185, 107, 0.035) 0%, transparent 45%);
}

.lp-side__inner {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2.4rem;
  padding: 3.8rem 3.2rem;
  max-width: 330px;
}

/* 装饰竖线 — 细分割金线 */
.lp-side__deco-line {
  width: 1px;
  background: linear-gradient(to bottom,
    transparent 0%,
    var(--gold) 25%,
    var(--gold) 75%,
    transparent 100%
  );
  align-self: center;
  opacity: 0.5;
}

.lp-side__deco-line--top,
.lp-side__deco-line--bottom {
  height: 52px;
}

/* ── 「墨香書閣」— 鎏金外发光 + 渐变描边 ── */
.lp-side__title-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.08rem;
}

.lp-side__char {
  font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
  font-size: 3.4rem;
  font-weight: 900;
  color: var(--gold);
  line-height: 1.12;
  letter-spacing: 0.1em;
  /* 外发光 + 微妙渐变描边效果 */
  text-shadow:
    0 0 48px rgba(221, 185, 107, 0.35),
    0 0 96px rgba(221, 185, 107, 0.15),
    0 2px 4px rgba(0, 0, 0, 0.45),
    0 0 1px rgba(221, 185, 107, 0.3);
  animation: lp-char-in 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.lp-side__char:nth-child(1) { animation-delay: 0.06s; }
.lp-side__char:nth-child(2) { animation-delay: 0.18s; }
.lp-side__char:nth-child(3) { animation-delay: 0.30s; }
.lp-side__char:nth-child(4) { animation-delay: 0.42s; }

@keyframes lp-char-in {
  from { opacity: 0; transform: translateY(16px) scale(0.92); filter: blur(4px); }
  to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}

/* 分隔线 — 细金线装饰 */
.lp-side__divider {
  display: flex;
  align-items: center;
  gap: 1.3rem;
  width: 100%;
}

.lp-side__divider::before,
.lp-side__divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right,
    transparent 0%,
    rgba(221, 185, 107, 0.35) 40%,
    rgba(221, 185, 107, 0.5) 50%,
    rgba(221, 185, 107, 0.35) 60%,
    transparent 100%
  );
}

.lp-side__diamond {
  width: 6px;
  height: 6px;
  background: var(--gold);
  transform: rotate(45deg);
  flex-shrink: 0;
  box-shadow:
    0 0 10px rgba(221, 185, 107, 0.5),
    0 0 20px rgba(221, 185, 107, 0.2);
}

/* 引文 — 字重分层 + 字距精调 */
.lp-side__quote {
  margin: 0;
  text-align: center;
  padding: 0.6rem 1.4rem;
  position: relative;
}

.lp-side__quote::before,
.lp-side__quote::after {
  content: '"';
  position: absolute;
  font-family: 'Noto Serif SC', serif;
  font-size: 2.2rem;
  color: rgba(221, 185, 107, 0.22);
  line-height: 1;
}

.lp-side__quote::before { top: -0.4rem; left: 0.2rem; }
.lp-side__quote::after { bottom: -1.1rem; right: 0.2rem; content: '"'; }

.lp-side__quote-text {
  font-family: 'Noto Serif SC', 'STSong', 'SimSun', serif;
  font-size: 1rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.68);
  line-height: 2.15;
  margin: 0 0 0.9rem;
  letter-spacing: 0.12em;
}

.lp-side__quote-cite {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.73rem;
  font-weight: 300;
  color: rgba(221, 185, 107, 0.48);
  font-style: normal;
  letter-spacing: 0.07em;
}

/* 底部小字 — 弱化透明度 + 纵向呼吸感 */
.lp-side__slogan {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.71rem;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.16);
  letter-spacing: 0.32em;
  margin: 0;
  text-transform: uppercase;
}

/* 背景汉字水印 — 更淡更雅 */
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
  font-size: 5.8rem;
  font-weight: 900;
  color: rgba(221, 185, 107, 0.018);
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

/* ══════════════════════════════════════════════
   2. 右侧登录卡片 — 宣纸渐变 + 悬浮浮空
   ══════════════════════════════════════════════ */
.lp-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3.2rem 3.8rem;
  background: transparent;
  position: relative;
  z-index: 1;
}

.lp-card {
  width: 100%;
  max-width: 420px;
  /* 宣纸米白渐变底色 */
  background:
    linear-gradient(165deg, var(--rice-pale) 0%, var(--card) 40%, var(--rice-cream) 100%);
  border-radius: 22px;
  padding: 2.9rem 2.7rem 2.5rem;
  /* 多层投影营造悬浮浮空效果 */
  box-shadow:
    0 2px 4px rgba(26, 21, 17, 0.03),
    0 6px 28px rgba(26, 21, 17, 0.06),
    0 14px 48px rgba(26, 21, 17, 0.05),
    0 24px 72px rgba(26, 21, 17, 0.03),
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    inset 0 -1px 0 rgba(210, 198, 182, 0.3);
  /* 极淡鎏金细描边 */
  border: 1px solid rgba(201, 160, 74, 0.12);
  transition:
    transform 0.4s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.4s cubic-bezier(0.22, 1, 0.36, 1);
  /* 入场动画：缓缓上浮 */
  animation: lp-card-enter 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes lp-card-enter {
  from {
    opacity: 0;
    transform: translateY(28px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片悬浮 — 浮空感增强 */
.lp-card:hover {
  transform: translateY(-3px);
  box-shadow:
    0 4px 8px rgba(26, 21, 17, 0.04),
    0 10px 36px rgba(26, 21, 17, 0.08),
    0 20px 60px rgba(26, 21, 17, 0.06),
    0 32px 88px rgba(26, 21, 17, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.95),
    inset 0 -1px 0 rgba(210, 198, 182, 0.3),
    0 0 0 1px rgba(201, 160, 74, 0.1);
}

/* ── 头部 ── */
.lp-card__header {
  text-align: center;
  margin-bottom: 2.3rem;
}

.lp-card__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  background: linear-gradient(145deg, var(--ink), #251E18);
  border-radius: 14px;
  margin-bottom: 1.15rem;
  box-shadow:
    0 4px 14px rgba(26, 21, 17, 0.22),
    0 1px 3px rgba(26, 21, 17, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  position: relative;
  overflow: hidden;
}

.lp-card__logo::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, transparent 45%, rgba(221, 185, 107, 0.07) 100%);
  pointer-events: none;
}

.lp-card__logo-text {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 0.91rem;
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 0.05em;
}

.lp-card__title {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1.78rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 0.42rem;
  letter-spacing: 0.05em;
}

.lp-card__subtitle {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.85rem;
  color: var(--brown-soft);
  margin: 0;
  letter-spacing: 0.03em;
  font-weight: 400;
}

/* ══════════════════════════════════════════════
   3. 表单通用
   ══════════════════════════════════════════════ */
.lp-form { margin-bottom: 0; }

.lp-form__item { margin-bottom: 1.18rem; }
.lp-form__item--options { margin-bottom: 0.55rem; }
.lp-form__item--role { margin-bottom: 1.12rem; }
.lp-form__item--code { margin-bottom: 1.18rem; }
.lp-form__item--submit { margin-top: 1.7rem; margin-bottom: 0; }

.lp-form :deep(.el-form-item__label) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--brown-deep);
  padding-bottom: 7px;
  letter-spacing: 0.05em;
}

.lp-form :deep(.el-form-item__label::before) {
  color: var(--gold-main) !important;
}

.lp-form :deep(.el-form-item__error) {
  font-size: 0.75rem;
  color: var(--error);
  padding-top: 3px;
}

/* ══════════════════════════════════════════════
   4. 身份选择器 — 浅棕鎏金渐变 + 内部柔光
   ══════════════════════════════════════════════ */
.lp-role-selector {
  display: flex;
  gap: 0;
  width: 100%;
  border: 1.5px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--input-bg);
  transition: border-color 0.35s ease, box-shadow 0.35s ease;
  position: relative;
}

.lp-role-selector:hover {
  border-color: var(--brown-fade);
  box-shadow: 0 0 0 3px var(--gold-whisper);
}

.lp-role-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 11px 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  position: relative;
  background: transparent;
}

/* 未选中态 — 哑光宣纸质感 */
.lp-role-option:not(.lp-role-option--active):hover {
  background: var(--input-hover);
}

/* 选中态 — 浅棕鎏金渐变 + 内部柔光 */
.lp-role-option--active {
  background: linear-gradient(135deg, #EADBC8 0%, #E2D2BC 50%, #D9C8AE 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.55),
    inset 0 -1px 0 rgba(164, 140, 112, 0.1),
    0 1px 4px rgba(82, 68, 56, 0.08);
}

/* 单选指示器 */
.lp-role-radio {
  width: 17px;
  height: 17px;
  border-radius: 50%;
  border: 1.5px solid var(--brown-fade);
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  background: var(--rice-pale);
}

.lp-role-option:not(.lp-role-option--active):hover .lp-role-radio {
  border-color: var(--brown-soft);
}

.lp-role-option--active .lp-role-radio {
  border-color: var(--gold-deep);
  background: linear-gradient(145deg, var(--gold-main), var(--gold-deep));
  box-shadow:
    0 0 0 2.5px rgba(201, 160, 74, 0.18),
    0 1px 3px rgba(168, 133, 50, 0.25);
}

.lp-role-option--active .lp-role-radio::after {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
}

.lp-role-label {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--brown);
  letter-spacing: 0.04em;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.lp-role-option--active .lp-role-label {
  color: var(--ink-mid);
  font-weight: 600;
}

/* ══════════════════════════════════════════════
   5. 输入框 — 宣纸底色 + 聚焦鎏金柔光
   ══════════════════════════════════════════════ */
.lp-input :deep(.el-input__wrapper) {
  background: var(--input-bg);
  border: 1.5px solid var(--border);
  border-radius: 11px;
  padding: 3px 14px;
  box-shadow:
    inset 0 1px 3px rgba(82, 68, 56, 0.055),
    0 1px 0 rgba(255, 255, 255, 0.5) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 46px;
}

/* hover — 淡墨色渐变微光过渡 */
.lp-input :deep(.el-input__wrapper:hover) {
  background: var(--input-hover);
  border-color: var(--brown-fade);
  box-shadow:
    inset 0 1px 3px rgba(82, 68, 56, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.5) !important;
}

/* focus — 描边变成鎏金柔光 */
.lp-input :deep(.el-input__wrapper.is-focus) {
  background: var(--rice-pale);
  border-color: var(--gold-main);
  box-shadow:
    inset 0 1px 3px rgba(82, 68, 56, 0.03),
    0 0 0 3.5px var(--gold-halo),
    0 0 18px var(--gold-glow),
    0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.lp-input :deep(.el-input__inner) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.9rem;
  color: var(--ink);
  font-weight: 400;
}

.lp-input :deep(.el-input__inner::placeholder) {
  color: var(--hint);
  font-weight: 300;
}

.lp-input :deep(.el-input__prefix-icon) {
  color: var(--hint);
  transition: color 0.3s ease;
  font-size: 1rem;
}

.lp-input :deep(.el-input__wrapper.is-focus .el-input__prefix-icon) {
  color: var(--gold-main);
}

.lp-input :deep(.el-input__suffix-inner .el-icon) {
  color: var(--hint);
  transition: color 0.25s;
}
.lp-input :deep(.el-input__suffix-inner .el-icon:hover) {
  color: var(--brown-soft);
}

/* ══════════════════════════════════════════════
   5b. 验证码行 — 输入框 + 获取按钮
   ══════════════════════════════════════════════ */
.lp-code-row {
  display: flex;
  gap: 10px;
  width: 100%;
  align-items: stretch;
}

.lp-code__input {
  flex: 1;
}

.lp-code__input :deep(.el-input__wrapper) {
  background: var(--input-bg);
  border: 1.5px solid var(--border);
  border-radius: 11px;
  padding: 3px 14px;
  box-shadow:
    inset 0 1px 3px rgba(82, 68, 56, 0.055),
    0 1px 0 rgba(255, 255, 255, 0.5) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 46px;
}

.lp-code__input :deep(.el-input__wrapper:hover) {
  background: var(--input-hover);
  border-color: var(--brown-fade);
}

.lp-code__input :deep(.el-input__wrapper.is-focus) {
  background: var(--rice-pale);
  border-color: var(--gold-main);
  box-shadow:
    inset 0 1px 3px rgba(82, 68, 56, 0.03),
    0 0 0 3.5px var(--gold-halo),
    0 0 18px var(--gold-glow),
    0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.lp-code__input :deep(.el-input__inner) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.9rem;
  color: var(--ink);
  font-weight: 400;
  letter-spacing: 0.2em;
}

.lp-code__input :deep(.el-input__inner::placeholder) {
  letter-spacing: 0.02em;
}

/* 获取验证码按钮 — 鎏金棕配色 */
.lp-code__btn {
  flex-shrink: 0;
  padding: 0 16px;
  height: 46px;
  white-space: nowrap;
  cursor: pointer;
  border: none;
  border-radius: 11px;
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: #FFFBF5;
  letter-spacing: 0.04em;
  /* 鎏金棕渐变 */
  background: linear-gradient(135deg, #736354 0%, #A88532 60%, #DDB96B 100%);
  box-shadow:
    0 2px 8px rgba(115, 99, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    inset 0 -1px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.lp-code__btn::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 50%;
  background: linear-gradient(to bottom,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 100%
  );
  pointer-events: none;
  border-radius: 11px 11px 0 0;
}

.lp-code__btn:hover:not(.lp-code__btn--disabled):not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 4px 14px rgba(168, 133, 50, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  filter: brightness(1.05);
}

.lp-code__btn:active:not(.lp-code__btn--disabled):not(:disabled) {
  transform: translateY(0) scale(0.97);
}

/* 禁用态 — 哑光灰 */
.lp-code__btn--disabled,
.lp-code__btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 1px 4px rgba(82, 68, 56, 0.12) !important;
  background: linear-gradient(135deg, #9E8D7A, #B5A48C) !important;
}

/* ══════════════════════════════════════════════
   5c. 第三方登录 — QQ 图标专属样式
   ══════════════════════════════════════════════ */
.lp-icon-qq {
  color: #12B7F5;
}

.lp-social__btn--qq:hover .lp-icon-qq {
  filter: drop-shadow(0 0 6px rgba(18, 183, 245, 0.4));
}

/* ══════════════════════════════════════════════
   6. 辅助文字 — 对齐 + 鎏金下划线
   ══════════════════════════════════════════════ */
.lp-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 3px 0;
}

.lp-checkbox :deep(.el-checkbox__label) {
  font-size: 0.81rem;
  font-weight: 400;
  color: var(--brown);
  letter-spacing: 0.02em;
  padding-left: 4px;
}

.lp-checkbox :deep(.el-checkbox__inner) {
  border-color: var(--brown-fade);
  border-radius: 5px;
  width: 16px; height: 16px;
  transition: all 0.25s ease;
  background: var(--rice-pale);
}

.lp-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, var(--gold-main), var(--gold-deep));
  border-color: var(--gold-main);
}

/* 忘记密码 / 注册切换 — hover 鎏金下划线 */
.lp-forgot {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.81rem;
  font-weight: 400;
  color: var(--brown-soft);
  text-decoration: none;
  cursor: pointer;
  letter-spacing: 0.01em;
  position: relative;
  transition: color 0.25s ease;
}

.lp-forgot::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1.5px;
  background: linear-gradient(90deg, var(--gold), var(--gold-deep));
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 1px;
}

.lp-forgot:hover {
  color: var(--gold-main);
}

.lp-forgot:hover::after {
  width: 100%;
}

/* ══════════════════════════════════════════════
   7. 登录主按钮 — 扫光动效 + 浮雕质感
   ══════════════════════════════════════════════ */
.lp-submit {
  width: 100%;
  height: 51px;
  /* 深棕到哑金细腻渐变 */
  background: linear-gradient(135deg, #4A3C30 0%, #735B3E 35%, #A88532 70%, #DDB96B 100%);
  border: none;
  border-radius: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  transition:
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  /* 浮雕内阴影质感 */
  box-shadow:
    0 4px 18px rgba(74, 60, 48, 0.32),
    0 1px 4px rgba(74, 60, 48, 0.18),
    inset 0 1.5px 0 rgba(255, 255, 255, 0.14),
    inset 0 -1.5px 0 rgba(0, 0, 0, 0.12);
}

/* 顶部内发光浮雕 */
.lp-submit::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 52%;
  background: linear-gradient(to bottom,
    rgba(255, 255, 255, 0.12) 0%,
    rgba(255, 255, 255, 0.04) 50%,
    transparent 100%
  );
  pointer-events: none;
  border-radius: 13px 13px 0 0;
}

/* ── 鎏金高光扫光动效 ── */
.lp-submit::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(
    105deg,
    transparent 0%,
    rgba(255, 255, 255, 0.08) 35%,
    rgba(255, 255, 255, 0.18) 50%,
    rgba(255, 255, 255, 0.08) 65%,
    transparent 100%
  );
  pointer-events: none;
  transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform: skewX(-12deg);
}

/* hover: 上浮 + 触发扫光 */
.lp-submit:hover {
  transform: translateY(-2.5px);
  box-shadow:
    0 8px 28px rgba(74, 60, 48, 0.38),
    0 3px 10px rgba(221, 185, 107, 0.15),
    inset 0 1.5px 0 rgba(255, 255, 255, 0.18),
    inset 0 -1.5px 0 rgba(0, 0, 0, 0.1);
}

.lp-submit:hover::after {
  left: 150%;
}

/* active: 下沉反馈 */
.lp-submit:active {
  transform: translateY(1px) scale(0.985);
  box-shadow:
    0 2px 8px rgba(74, 60, 48, 0.28),
    inset 0 2px 5px rgba(0, 0, 0, 0.15);
}

.lp-submit:disabled,
.lp-submit[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: 0 2px 8px rgba(74, 60, 48, 0.12) !important;
}

.lp-submit:hover:disabled::after,
.lp-submit:disabled::after {
  display: none;
}

.lp-submit__text {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 1rem;
  font-weight: 600;
  color: #FFFBF5;
  letter-spacing: 0.2em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.18);
  position: relative;
  z-index: 1;
}

.lp-submit__loader {
  width: 20px; height: 20px;
  border: 2px solid rgba(255, 251, 245, 0.22);
  border-top-color: #FFFBF5;
  border-radius: 50%;
  animation: lp-spin 0.6s linear infinite;
  position: relative;
  z-index: 1;
}

@keyframes lp-spin { to { transform: rotate(360deg); } }

/* ══════════════════════════════════════════════
   8. 底部注册 & 分割线
   ══════════════════════════════════════════════ */
.lp-card__footer {
  text-align: center;
  margin-top: 1.65rem;
}

.lp-card__footer-text {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 0.84rem;
  color: var(--brown-soft);
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.01em;
}

/* 注册链接 — 鎏金下划线 */
.lp-toggle {
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--gold-main);
  font-weight: 600;
  cursor: pointer;
  margin-left: 0.3em;
  position: relative;
  transition: color 0.25s ease;
  letter-spacing: 0.02em;
}

.lp-toggle::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1.5px;
  background: linear-gradient(90deg, var(--gold), var(--gold-deep));
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 1px;
}

.lp-toggle:hover {
  color: var(--gold-deep);
}

.lp-toggle:hover::after {
  width: 100%;
}

/* 分割线 */
.lp-divider {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin: 1.9rem 0 1.4rem;
}

.lp-divider__line {
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--border), transparent);
}

.lp-divider__text {
  font-family: 'Noto Serif SC', serif;
  font-size: 0.75rem;
  color: var(--brown-fade);
  flex-shrink: 0;
  letter-spacing: 0.09em;
  font-weight: 400;
}

/* ══════════════════════════════════════════════
   9. 第三方登录图标 — 哑光底 + 鎏金填充过渡
   ══════════════════════════════════════════════ */
.lp-social {
  display: flex;
  justify-content: center;
  gap: 0.9rem;
}

.lp-social__btn {
  width: 49px;
  height: 49px;
  /* 哑光底色 */
  background: var(--input-bg);
  border: 1.5px solid var(--border);
  border-radius: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--brown);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(82, 68, 56, 0.04);
}

/* hover: 浅鎏金填充过渡 */
.lp-social__btn:hover {
  background: linear-gradient(145deg, var(--input-hover), #EDE2D3);
  border-color: var(--gold-main);
  color: var(--gold-main);
  transform: translateY(-2.5px);
  box-shadow:
    0 5px 16px rgba(201, 160, 74, 0.14),
    0 2px 6px rgba(82, 68, 56, 0.06);
}

.lp-social__btn:active {
  transform: translateY(0);
}

/* ══════════════════════════════════════════════
   10. 响应式
   ══════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .lp-side { width: 42%; }
  .lp-side__char { font-size: 2.7rem; }
  .lp-main { padding: 2.6rem 2.2rem; }
  .lp-card { padding: 2.5rem 2.3rem 2.1rem; }
}

@media (max-width: 768px) {
  .lp-side { display: none; }
  .lp-main {
    min-height: 100vh;
    padding: 2.3rem 1.5rem;
    align-items: flex-start;
    padding-top: 3.8rem;
  }
  .lp-card {
    border-radius: 18px;
    padding: 2.3rem 1.9rem 1.9rem;
    box-shadow:
      0 4px 20px rgba(26, 21, 17, 0.05),
      0 12px 40px rgba(26, 21, 17, 0.04),
      inset 0 1px 0 rgba(255, 255, 255, 0.85);
  }
}

@media (max-width: 480px) {
  .lp-card__title { font-size: 1.53rem; }
  .lp-card { max-width: 100%; padding: 2.1rem 1.5rem 1.7rem; }
  .lp-submit { height: 47px; border-radius: 12px; }
  .lp-main { padding: 2rem 1.1rem; }
  .lp-role-label { font-size: 0.8rem; }
  .lp-role-option { padding: 10px 12px; }
}

@media (prefers-reduced-motion: reduce) {
  .lp-side__char,
  .lp-submit,
  .lp-submit::after,
  .lp-social__btn,
  .lp-role-option,
  .lp-role-selector,
  .lp-input :deep(.el-input__wrapper),
  .lp-code__input :deep(.el-input__wrapper),
  .lp-code__btn,
  .lp-card,
  .lp-forgot,
  .lp-toggle {
    animation: none !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
